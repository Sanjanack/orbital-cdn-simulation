from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from enhanced_satellite_cdn import Satellite, SimulationConfig, create_content_catalog
import simpy
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orbital_cdn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SimulationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    config = db.Column(db.Text, nullable=False)  # JSON string
    results = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='running')  # 'running', 'completed', 'failed'

class ContentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('simulation_session.id'), nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    content_id = db.Column(db.String(100), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    content_size = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'Hit' or 'Miss'
    delivery_source = db.Column(db.String(50), nullable=False)
    cache_utilization = db.Column(db.Float, nullable=False)
    hit_rate = db.Column(db.Float, nullable=False)
# Add this filter for JSON parsing in templates
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if value is None:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Global simulation state
simulation_state = {
    'running': False,
    'current_session': None,
    'satellite': None,
    'env': None,
    'config': None
}

def create_default_admin():
    """Create default admin user if none exists"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@orbitalcdn.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/admin123")
    else:
        # Ensure admin has correct role and a known password for dev access
        updated = False
        if admin.role != 'admin':
            admin.role = 'admin'
            updated = True
        # Always reset to default for dev convenience
        admin.set_password('admin123')
        updated = True
        if updated:
            db.session.commit()
            print("Default admin credentials ensured: admin/admin123")

def ensure_schema_migrations():
    """Ensure database schema is initialized and compatible.

    This is a lightweight guard used by the launcher. It creates tables if
    they don't exist and can be extended for simple migrations.
    """
    try:
        db.create_all()
    except Exception as exc:
        print(f"Schema migration check failed: {exc}")

def run_simulation_background(config_dict):
    """Run simulation in background thread"""
    try:
        # Create SimPy environment
        env = simpy.Environment()
        
        # Create configuration
        config = SimulationConfig(
            simulation_duration=config_dict.get('simulation_duration', 200.0),
            request_interval=config_dict.get('request_interval', 3.0),
            cache_size=config_dict.get('cache_size', 12),
            content_catalog_size=config_dict.get('content_catalog_size', 20),
            user_count=config_dict.get('user_count', 4),
            log_interval=config_dict.get('log_interval', 10.0)
        )
        
        # Create content catalog
        content_catalog = create_content_catalog(config)
        
        # Create satellite
        satellite = Satellite(env, config)
        
        # Start user processes
        for i in range(config.user_count):
            user_id = f"User_{i+1}"
            env.process(user_request_process(env, satellite, content_catalog, user_id, config))
        
        # Start performance monitoring
        env.process(performance_monitor_process(env, satellite, config))
        
        # Run simulation
        env.run(until=config.simulation_duration)
        
        # Update simulation state
        simulation_state['running'] = False
        simulation_state['satellite'] = satellite
        simulation_state['env'] = env
        simulation_state['config'] = config
        
        print("Simulation completed successfully")

        # Persist results and mark session completed
        try:
            from sqlalchemy import func
            with app.app_context():
                session_id = simulation_state.get('current_session')
                if session_id is not None:
                    sim_session = SimulationSession.query.get(session_id)
                    if sim_session:
                        # Save request logs into ContentRequest
                        for entry in satellite.request_log:
                            db.session.add(ContentRequest(
                                session_id=session_id,
                                timestamp=float(entry.get('timestamp', 0.0)),
                                user_id=str(entry.get('user_id', 'unknown')),
                                content_id=str(entry.get('content_id', 'unknown')),
                                content_type=str(entry.get('content_type', 'unknown')),
                                content_size=int(entry.get('content_size', 0)),
                                status=str(entry.get('status', 'Miss')),
                                delivery_source=str(entry.get('delivery_source', 'Unknown')),
                                cache_utilization=float(entry.get('cache_utilization', 0.0)),
                                hit_rate=float(entry.get('hit_rate', 0.0))
                            ))
                        # Store summarized results
                        stats = satellite.get_final_statistics()
                        sim_session.results = json.dumps(stats)
                        sim_session.status = 'completed'
                        db.session.commit()
        except Exception as persist_exc:
            print(f"Failed to persist simulation results: {persist_exc}")
    except Exception as e:
        print(f"Simulation error: {e}")
        simulation_state['running'] = False

def ensure_runtime_satellite() -> Satellite:
    """Ensure a runtime satellite and environment exist for on-demand requests."""
    if simulation_state['env'] is None or simulation_state['satellite'] is None:
        env = simpy.Environment()
        config = SimulationConfig(
            simulation_duration=10.0,
            request_interval=1.0,
            cache_size=12,
            content_catalog_size=20,
            user_count=1,
            log_interval=5.0
        )
        satellite = Satellite(env, config)
        simulation_state['env'] = env
        simulation_state['satellite'] = satellite
        simulation_state['config'] = config
    return simulation_state['satellite']


def user_request_process(env, satellite, content_catalog, user_id, config):
    """User request process for background simulation"""
    import random
    content_weights = [content.popularity for content in content_catalog]
    
    while env.now < config.simulation_duration:
        try:
            selected_content = random.choices(content_catalog, weights=content_weights)[0]
            log_entry = satellite.request_content(selected_content.content_id, selected_content, user_id)
            yield env.timeout(config.request_interval)
        except simpy.Interrupt:
            break

def performance_monitor_process(env, satellite, config):
    """Performance monitoring process for background simulation"""
    while env.now < config.simulation_duration:
        satellite.log_performance()
        yield env.timeout(config.log_interval)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # Get user's simulation sessions
    sessions = SimulationSession.query.filter_by(user_id=current_user.id).order_by(SimulationSession.created_at.desc()).limit(5).all()
    
    return render_template('user_dashboard.html', sessions=sessions)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Get all simulation sessions
    sessions = SimulationSession.query.order_by(SimulationSession.created_at.desc()).limit(20).all()
    
    # Get user statistics
    total_users = User.query.count()
    total_sessions = SimulationSession.query.count()
    completed_sessions = SimulationSession.query.filter_by(status='completed').count()
    running_sessions = SimulationSession.query.filter_by(status='running').count()
    
    # Get recent content requests
    recent_requests = ContentRequest.query.order_by(ContentRequest.timestamp.desc()).limit(50).all()

    # Users list for management table and lookups
    users = User.query.order_by(User.created_at.desc()).all()
    user_map = {u.id: u.username for u in users}

    # Active simulations and pending users (no workflow -> empty list)
    active_simulations = SimulationSession.query.filter_by(status='running').all()
    pending_users = []

    # Compute CDN stats summary from latest completed session if available
    latest_completed = SimulationSession.query.filter_by(status='completed').order_by(SimulationSession.created_at.desc()).first()
    cdn_stats = {
        'total_requests': 0,
        'cache_hits': 0,
        'cache_misses': 0,
        'avg_hit_rate': 0.0
    }
    if latest_completed and latest_completed.results:
        try:
            res = json.loads(latest_completed.results)
            cdn_stats['total_requests'] = int(res.get('total_requests', 0))
            cdn_stats['cache_hits'] = int(res.get('cache_hits', 0))
            cdn_stats['cache_misses'] = int(res.get('cache_misses', 0))
            cdn_stats['avg_hit_rate'] = float(res.get('cache_hit_rate', 0.0))
        except Exception:
            pass

    now = datetime.utcnow()

    # Current satellite runtime KPIs if available
    current_satellite = simulation_state.get('satellite')
    current_kpis = None
    if current_satellite is not None:
        try:
            current_kpis = {
                'cache_utilization': len(current_satellite.cache) / current_satellite.cache_size if current_satellite.cache_size else 0.0,
                'hit_rate': (current_satellite.cache_hits / current_satellite.total_requests) * 100 if current_satellite.total_requests else 0.0,
                'cache_size': len(current_satellite.cache),
                'cache_capacity': current_satellite.cache_size,
                'satellite_name': 'LEO-1'
            }
        except Exception:
            current_kpis = None
    
    return render_template('admin_dashboard.html', 
                         sessions=sessions, 
                         users=users,
                         user_map=user_map,
                         total_users=total_users,
                         total_sessions=total_sessions,
                         completed_sessions=completed_sessions,
                         running_sessions=running_sessions,
                         recent_requests=recent_requests,
                         active_simulations=active_simulations,
                         pending_users=pending_users,
                         cdn_stats=cdn_stats,
                         current_kpis=current_kpis,
                         now=now)

@app.route('/start_simulation', methods=['POST'])
@login_required
def start_simulation():
    if simulation_state['running']:
        return jsonify({'error': 'Simulation already running'})
    
    config_data = {
        'simulation_duration': float(request.form.get('simulation_duration', 200)),
        'request_interval': float(request.form.get('request_interval', 3)),
        'cache_size': int(request.form.get('cache_size', 12)),
        'content_catalog_size': int(request.form.get('content_catalog_size', 20)),
        'user_count': int(request.form.get('user_count', 4)),
        'log_interval': float(request.form.get('log_interval', 10))
    }
    
    # Create simulation session
    session = SimulationSession(
        user_id=current_user.id,
        config=json.dumps(config_data),
        status='running'
    )
    db.session.add(session)
    db.session.commit()
    
    # Start simulation in background
    simulation_state['running'] = True
    simulation_state['current_session'] = session.id
    
    thread = threading.Thread(target=run_simulation_background, args=(config_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'session_id': session.id})

@app.route('/simulation_status')
@login_required
def simulation_status():
    if simulation_state['running']:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'completed'})

@app.route('/simulation_results')
@login_required
def simulation_results():
    if not simulation_state['satellite']:
        return jsonify({'error': 'No simulation results available'})
    
    satellite = simulation_state['satellite']
    stats = satellite.get_final_statistics()
    
    # Convert logs to DataFrames for analysis
    request_df = pd.DataFrame(satellite.request_log)
    performance_df = pd.DataFrame(satellite.performance_log)
    
    # Generate charts
    charts = generate_charts(request_df, performance_df, stats)
    
    return jsonify({
        'statistics': stats,
        'charts': charts,
        'request_count': len(satellite.request_log),
        'performance_count': len(satellite.performance_log)
    })

def generate_charts(request_df, performance_df, stats):
    """Generate base64 encoded charts for dashboard display"""
    charts = {}
    
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # 1. Cache Hit Rate Over Time
    if not performance_df.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(performance_df['timestamp'], performance_df['hit_rate'], marker='o', linewidth=2)
        plt.title('Cache Hit Rate Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Simulation Time', fontsize=12)
        plt.ylabel('Hit Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save to base64
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        charts['hit_rate'] = base64.b64encode(img.getvalue()).decode()
        plt.close()
    
    # 2. Cache Utilization Over Time
    if not performance_df.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(performance_df['timestamp'], performance_df['cache_utilization'], marker='s', linewidth=2, color='orange')
        plt.title('Cache Utilization Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Simulation Time', fontsize=12)
        plt.ylabel('Cache Utilization', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        charts['cache_utilization'] = base64.b64encode(img.getvalue()).decode()
        plt.close()
    
    # 3. Content Type Distribution
    if not request_df.empty:
        plt.figure(figsize=(10, 6))
        content_type_counts = request_df['content_type'].value_counts()
        plt.pie(content_type_counts.values, labels=content_type_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Content Type Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        charts['content_distribution'] = base64.b64encode(img.getvalue()).decode()
        plt.close()
    
    # 4. Request Status Comparison
    if not request_df.empty:
        plt.figure(figsize=(8, 6))
        status_counts = request_df['status'].value_counts()
        colors = ['#2ecc71' if status == 'Hit' else '#e74c3c' for status in status_counts.index]
        plt.bar(status_counts.index, status_counts.values, color=colors, alpha=0.8)
        plt.title('Request Status Comparison', fontsize=14, fontweight='bold')
        plt.xlabel('Status', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        charts['request_status'] = base64.b64encode(img.getvalue()).decode()
        plt.close()
    
    return charts

@app.route('/api/analytics')
@login_required
def analytics_api():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get analytics data
    total_users = User.query.count()
    total_sessions = SimulationSession.query.count()
    completed_sessions = SimulationSession.query.filter_by(status='completed').count()
    
    # User growth over time
    users_over_time = db.session.query(
        db.func.date(User.created_at).label('date'),
        db.func.count(User.id).label('count')
    ).group_by(db.func.date(User.created_at)).all()
    
    # Session statistics by day
    sessions_over_time = db.session.query(
        db.func.date(SimulationSession.created_at).label('date'),
        db.func.count(SimulationSession.id).label('count')
    ).group_by(db.func.date(SimulationSession.created_at)).all()
    
    return jsonify({
        'total_users': total_users,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'users_over_time': [{'date': str(u.date), 'count': u.count} for u in users_over_time],
        'sessions_over_time': [{'date': str(s.date), 'count': s.count} for s in sessions_over_time]
    })

@app.route('/api/admin/monitoring')
@login_required
def admin_monitoring_api():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    active_sessions = SimulationSession.query.filter_by(status='running').count()
    return jsonify({
        'active_sessions': active_sessions,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/request_content', methods=['POST'])
@login_required
def api_request_content():
    """Handle a single user content request and return immediate result details."""
    try:
        payload = request.get_json(silent=True) or {}
        content_type = (payload.get('content_type') or request.form.get('content_type') or 'document').strip()
        size = int((payload.get('size') or request.form.get('size') or 10))
        speed = float((payload.get('speed') or request.form.get('speed') or 1.0))
        content_id = (payload.get('content_id') or request.form.get('content_id') or f'{content_type}_{size}mb')

        # Ensure runtime satellite
        satellite = ensure_runtime_satellite()
        env = simulation_state['env']

        # Build a minimal content surrogate compatible with Satellite
        from enhanced_satellite_cdn import Content
        content = Content(content_id=content_id, size=size, content_type=content_type, popularity=0.5)

        # Advance env a tiny step to simulate timing; speed influences perceived delivery_time
        # Perform the request
        log_entry = satellite.request_content(content_id, content, user_id=str(current_user.id))
        # Simulated delivery time: faster for hits, slower for misses, scaled by speed
        base_time = 0.3 if log_entry['status'] == 'Hit' else 1.2
        delivery_time = max(0.05, base_time / max(0.1, speed))

        # Persist request row linked to an ad-hoc session (optional: current_session if any)
        session_id = simulation_state.get('current_session')
        db.session.add(ContentRequest(
            session_id=session_id or 0,
            timestamp=float(log_entry.get('timestamp', 0.0)),
            user_id=str(current_user.id),
            content_id=content_id,
            content_type=content_type,
            content_size=size,
            status=log_entry['status'],
            delivery_source=log_entry['delivery_source'],
            cache_utilization=float(log_entry.get('cache_utilization', 0.0)),
            hit_rate=float(log_entry.get('hit_rate', 0.0))
        ))
        db.session.commit()

        return jsonify({
            'connected': True,
            'satellite': 'LEO-1',
            'status': log_entry['status'],
            'delivery_source': log_entry['delivery_source'],
            'cache_utilization': log_entry.get('cache_utilization', 0.0),
            'hit_rate': log_entry.get('hit_rate', 0.0),
            'delivery_time': delivery_time,
            'request': {
                'content_id': content_id,
                'content_type': content_type,
                'size': size,
                'speed': speed
            }
        })
    except Exception as exc:
        return jsonify({'connected': False, 'error': str(exc)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 