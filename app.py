from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
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
from satellite_constellation import SatelliteConstellation, create_leo_constellation, ConstellationSatellite
from advanced_caching import LRUCache, LFUCache, FIFOCache, AdaptiveCache
from realtime_collaboration import init_collaboration, register_socketio_handlers
import simpy
import threading
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "orbital_cdn.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SocketIO for real-time collaboration
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize collaboration manager
collaboration_manager = init_collaboration(socketio)
register_socketio_handlers(socketio, collaboration_manager)

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

class UserMessage(db.Model):
    """User-to-user messaging system"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    content_id = db.Column(db.String(100))  # Optional: link to shared content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class SharedContent(db.Model):
    """Content sharing between users"""
    id = db.Column(db.Integer, primary_key=True)
    sharer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.String(100), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    content_size = db.Column(db.Integer, nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.utcnow)
    accessed = db.Column(db.Boolean, default=False)
    
    sharer = db.relationship('User', foreign_keys=[sharer_id], backref='shared_contents')
    receiver_rel = db.relationship('User', foreign_keys=[receiver_id], backref='received_contents')

class SatelliteNode(db.Model):
    """Multi-satellite constellation support"""
    id = db.Column(db.Integer, primary_key=True)
    satellite_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)  # km
    cache_size = db.Column(db.Integer, nullable=False)
    cache_utilization = db.Column(db.Float, default=0.0)
    hit_rate = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, inactive, maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
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
    'constellation': None,  # Multi-satellite constellation
    'env': None,
    'config': None,
    'caching_strategy': 'LRU',  # LRU, LFU, FIFO, Adaptive
    'multi_satellite_enabled': False,
    'collaboration_enabled': False,
    # Track which satellite the current user last connected to (useful for multi-satellite UI)
    'last_connected_satellite_by_user': {}  # { user_id(int): "LEO-1" }
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
    
    # Use enhanced dashboard for better user experience
    return render_template('user_dashboard_enhanced.html', sessions=sessions)

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
    
    # Set style - use available style
    try:
        plt.style.use('seaborn-v0_8')
    except OSError:
        try:
            plt.style.use('seaborn')
        except OSError:
            plt.style.use('default')
            sns.set_style("whitegrid")
    
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
    """Handle realistic NTN content request with proper algorithmic flow."""
    try:
        payload = request.get_json(silent=True) or {}
        content_id = payload.get('content_id', '').strip()
        
        if not content_id:
            return jsonify({
                'connected': False,
                'error': 'Content ID is required',
                'content_delivered': False
            }), 400
        
        # Initialize NTN simulation if not exists (respect selected caching strategy)
        selected_strategy = simulation_state.get('caching_strategy', 'LRU')
        if 'ntn_sim' not in simulation_state:
            from ntn_network_simulation import NTNSimulation
            simulation_state['ntn_sim'] = NTNSimulation(cache_size=12, caching_strategy=selected_strategy)
        else:
            # If user changed strategy, refresh the simulator so the cache policy matches
            try:
                if getattr(simulation_state['ntn_sim'], 'caching_strategy', None) != str(selected_strategy).upper():
                    from ntn_network_simulation import NTNSimulation
                    simulation_state['ntn_sim'] = NTNSimulation(cache_size=12, caching_strategy=selected_strategy)
            except Exception:
                pass
        
        ntn_sim = simulation_state['ntn_sim']
        
        # Simulate realistic content request
        result = ntn_sim.simulate_request(content_id, str(current_user.id))
        
        if result['status'] == 'ERROR':
            return jsonify({
                'connected': True,
                'satellite_connected': True,
                'status': 'ERROR',
                'error': result.get('error', 'Unknown error'),
                'content_delivered': False,
                'steps': result.get('steps', [])
            }), 400
        
        # Get content details
        content = result.get('content')
        if not content:
            return jsonify({
                'connected': True,
                'error': 'Content not found',
                'content_delivered': False
            }), 404
        
        # Get statistics
        stats = ntn_sim.get_statistics()
        
        # Persist to database
        session_id = simulation_state.get('current_session')
        db.session.add(ContentRequest(
            session_id=session_id or 0,
            timestamp=float(result.get('timestamp', 0.0)),
            user_id=str(current_user.id),
            content_id=content_id,
            content_type=content.content_type,
            content_size=content.size_mb,
            status=result['status'],
            delivery_source=result['source'],
            cache_utilization=stats['cache_utilization'],
            hit_rate=stats['cache_hit_rate']
        ))
        db.session.commit()
        
        # Pick best strategy display from simulator result (important for ADAPTIVE)
        result_strategy = result.get('caching_strategy') or selected_strategy
        result_strategy_current = result.get('caching_strategy_current')

        # Return realistic response with all details
        response_data = {
            'connected': True,
            'satellite': 'LEO-1',
            'satellite_connected': True,
            'satellite_id': 'LEO-1',
            'multi_satellite': False,
            'caching_strategy': result_strategy,
            'caching_strategy_current': result_strategy_current,
            'status': result['status'],
            'delivery_source': result['source'],
            'delivery_time': result.get('delivery_time', result.get('total_time', 0)),
            'cache_utilization': stats['cache_utilization'],
            'hit_rate': stats['cache_hit_rate'],
            'content_delivered': True,
            'content_received': {
                'content_id': content.content_id,
                'title': content.title,
                'content_type': content.content_type,
                'size_mb': content.size_mb,
                'description': content.description,
                'category': content.category,
                'received_at': datetime.utcnow().isoformat()
            },
            'steps': result.get('steps', []),
            'statistics': stats
        }

        # Remember which satellite user is connected to (single-satellite mode)
        try:
            simulation_state['last_connected_satellite_by_user'][int(current_user.id)] = 'LEO-1'
        except Exception:
            pass
        
        # Add performance comparison data
        if 'performance' in result:
            response_data['performance'] = result['performance']
        
        # Add latency information
        if 'latency_satellite_ms' in result:
            response_data['latency_satellite_ms'] = result['latency_satellite_ms']
        if 'latency_ground_ms' in result:
            response_data['latency_ground_ms'] = result['latency_ground_ms']
        
        return jsonify(response_data)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({
            'connected': False,
            'satellite_connected': False,
            'error': str(exc),
            'content_delivered': False
        }), 400

@app.route('/api/available_content', methods=['GET'])
@login_required
def available_content():
    """Get list of available content from catalog with filtering"""
    try:
        if 'ntn_sim' not in simulation_state:
            from ntn_network_simulation import NTNSimulation
            simulation_state['ntn_sim'] = NTNSimulation(cache_size=12, caching_strategy=simulation_state.get('caching_strategy', 'LRU'))
        
        ntn_sim = simulation_state['ntn_sim']
        content_list = ntn_sim.get_available_content()
        
        # Apply filters if provided
        content_type = request.args.get('type', '')
        size_filter = request.args.get('size', '')
        
        filtered_content = content_list
        
        if content_type:
            filtered_content = [c for c in filtered_content if c['type'] == content_type]
        
        if size_filter:
            if size_filter == '0-10':
                filtered_content = [c for c in filtered_content if 0 <= c['size_mb'] < 10]
            elif size_filter == '10-50':
                filtered_content = [c for c in filtered_content if 10 <= c['size_mb'] < 50]
            elif size_filter == '50-100':
                filtered_content = [c for c in filtered_content if 50 <= c['size_mb'] < 100]
            elif size_filter == '100+':
                filtered_content = [c for c in filtered_content if c['size_mb'] >= 100]
        
        return jsonify({
            'success': True,
            'content': filtered_content,
            'total_items': len(filtered_content),
            'filters_applied': {
                'type': content_type,
                'size': size_filter
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# =============================================================================
# USER INTERACTION APIs - Messaging & Content Sharing
# =============================================================================

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message to another user"""
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        message = data.get('message', '').strip()
        content_id = data.get('content_id')  # Optional content sharing
        
        if not receiver_id or not message:
            return jsonify({'error': 'Receiver ID and message are required'}), 400
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        user_message = UserMessage(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=message,
            content_id=content_id
        )
        db.session.add(user_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message_id': user_message.id,
            'created_at': user_message.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_messages', methods=['GET'])
@login_required
def get_messages():
    """Get user's messages"""
    try:
        messages = UserMessage.query.filter(
            (UserMessage.receiver_id == current_user.id) | 
            (UserMessage.sender_id == current_user.id)
        ).order_by(UserMessage.created_at.desc()).limit(50).all()
        
        return jsonify({
            'messages': [{
                'id': msg.id,
                'sender_id': msg.sender_id,
                'sender_username': msg.sender.username,
                'receiver_id': msg.receiver_id,
                'receiver_username': msg.receiver.username,
                'message': msg.message,
                'content_id': msg.content_id,
                'created_at': msg.created_at.isoformat(),
                'read': msg.read,
                'is_sent': msg.sender_id == current_user.id
            } for msg in messages]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/share_content', methods=['POST'])
@login_required
def share_content():
    """Share content with another user"""
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content_id = data.get('content_id')
        content_type = data.get('content_type', 'document')
        content_size = data.get('content_size', 0)
        
        if not receiver_id or not content_id:
            return jsonify({'error': 'Receiver ID and content ID are required'}), 400
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        shared = SharedContent(
            sharer_id=current_user.id,
            receiver_id=receiver_id,
            content_id=content_id,
            content_type=content_type,
            content_size=content_size
        )
        db.session.add(shared)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'shared_content_id': shared.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_shared_content', methods=['GET'])
@login_required
def get_shared_content():
    """Get content shared with current user"""
    try:
        shared = SharedContent.query.filter_by(
            receiver_id=current_user.id,
            accessed=False
        ).order_by(SharedContent.shared_at.desc()).all()
        
        return jsonify({
            'shared_content': [{
                'id': s.id,
                'sharer_username': s.sharer.username,
                'content_id': s.content_id,
                'content_type': s.content_type,
                'content_size': s.content_size,
                'shared_at': s.shared_at.isoformat()
            } for s in shared]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_users', methods=['GET'])
@login_required
def get_users():
    """Get list of users for messaging/sharing"""
    try:
        users = User.query.filter(User.id != current_user.id).all()
        return jsonify({
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role
            } for u in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/satellite_status', methods=['GET'])
@login_required
def satellite_status():
    """Get real-time satellite constellation status with connection info"""
    try:
        satellites = SatelliteNode.query.filter_by(status='active').all()
        satellite = simulation_state.get('satellite')
        
        satellite_data = []
        if satellite:
            satellite_data.append({
                'satellite_id': 'LEO-1',
                'name': 'LEO Satellite 1',
                'cache_utilization': len(satellite.cache) / satellite.cache_size if satellite.cache_size else 0,
                'hit_rate': (satellite.cache_hits / satellite.total_requests * 100) if satellite.total_requests else 0,
                'status': 'active',
                'cached_items': len(satellite.cache),
                'cache_size': satellite.cache_size,
                'total_requests': satellite.total_requests,
                'latitude': 0.0,
                'longitude': 0.0,
                'altitude': 550.0,
                'connected': True,
                'signal_strength': 'Strong',
                'latency_ms': 15
            })
        
        # Try to get constellation data if available
        constellation = simulation_state.get('constellation')
        if constellation:
            stats = constellation.get_constellation_stats()
            satellite_data = stats.get('satellites', satellite_data)
        
        connected_satellite_id = None
        try:
            connected_satellite_id = simulation_state.get('last_connected_satellite_by_user', {}).get(int(current_user.id))
        except Exception:
            connected_satellite_id = None

        return jsonify({
            'satellites': satellite_data,
            'total_satellites': len(satellite_data),
            'constellation_stats': constellation.get_constellation_stats() if constellation else None,
            'connection_status': 'connected' if satellite else 'disconnected',
            'connected_satellite_id': connected_satellite_id,
            'multi_satellite_enabled': bool(simulation_state.get('multi_satellite_enabled')),
            'caching_strategy': simulation_state.get('caching_strategy', 'LRU')
        })
    except Exception as e:
        return jsonify({'error': str(e), 'connection_status': 'error'}), 400

@app.route('/api/satellite_connection', methods=['GET'])
@login_required
def satellite_connection():
    """Check satellite connection status"""
    try:
        satellite = simulation_state.get('satellite')
        if satellite:
            return jsonify({
                'connected': True,
                'satellite_id': 'LEO-1',
                'status': 'active',
                'signal_strength': 'Strong',
                'latency_ms': 15,
                'altitude_km': 550,
                'orbital_speed_km_s': 7.5,
                'connection_quality': 'Excellent'
            })
        else:
            return jsonify({
                'connected': False,
                'status': 'disconnected',
                'message': 'Satellite not initialized'
            })
    except Exception as e:
        return jsonify({'connected': False, 'error': str(e)}), 400

@app.route('/api/constellation_stats', methods=['GET'])
@login_required
def constellation_stats():
    """Get detailed constellation statistics"""
    try:
        constellation = simulation_state.get('constellation')
        if not constellation:
            return jsonify({
                'total_satellites': 0,
                'total_requests': 0,
                'total_hits': 0,
                'total_misses': 0,
                'overall_hit_rate': 0,
                'inter_satellite_hits': 0,
                'inter_satellite_hit_rate': 0,
                'satellites': [],
                'message': 'Multi-satellite mode not enabled. Enable it from Multi-Satellite tab.'
            })
        
        stats = constellation.get_constellation_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/geographic_distribution', methods=['GET'])
@login_required
def geographic_distribution():
    """Get geographic distribution of requests and satellites"""
    try:
        constellation = simulation_state.get('constellation')
        satellite = simulation_state.get('satellite')
        
        data = {
            'satellites': [],
            'request_distribution': {}
        }
        
        if constellation:
            stats = constellation.get_constellation_stats()
            data['satellites'] = stats.get('satellites', [])
        
        # Get request distribution by region (simplified)
        if satellite and satellite.request_log:
            for entry in satellite.request_log[-100:]:  # Last 100 requests
                region = 'Global'  # Simplified - could be enhanced with actual geolocation
                if region not in data['request_distribution']:
                    data['request_distribution'][region] = 0
                data['request_distribution'][region] += 1
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# =============================================================================
# ADVANCED FEATURES APIs - Multi-Satellite, Advanced Caching, Collaboration
# =============================================================================

@app.route('/api/enable_multi_satellite', methods=['POST'])
@login_required
def enable_multi_satellite():
    """Enable multi-satellite constellation mode"""
    try:
        data = request.get_json() or {}
        num_satellites = int(data.get('num_satellites', 5))
        
        # Create SimPy environment if not exists
        if simulation_state['env'] is None:
            simulation_state['env'] = simpy.Environment()
        
        # Create configuration
        if simulation_state['config'] is None:
            simulation_state['config'] = SimulationConfig()
        
        # Create constellation
        constellation = create_leo_constellation(
            simulation_state['env'],
            simulation_state['config'],
            num_satellites=num_satellites,
            caching_strategy=simulation_state.get('caching_strategy', 'LRU')
        )
        
        simulation_state['constellation'] = constellation
        simulation_state['multi_satellite_enabled'] = True
        
        stats = constellation.get_constellation_stats()
        
        return jsonify({
            'success': True,
            'message': f'Multi-satellite constellation enabled with {num_satellites} satellites',
            'constellation_stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/set_caching_strategy', methods=['POST'])
@login_required
def set_caching_strategy():
    """Set caching strategy (LRU, LFU, FIFO, Adaptive)"""
    try:
        data = request.get_json() or {}
        strategy = data.get('strategy', 'LRU').upper()
        
        valid_strategies = ['LRU', 'LFU', 'FIFO', 'ADAPTIVE']
        if strategy not in valid_strategies:
            return jsonify({
                'success': False,
                'error': f'Invalid strategy. Must be one of: {", ".join(valid_strategies)}'
            }), 400
        
        simulation_state['caching_strategy'] = strategy

        # If multi-satellite constellation is enabled, rebuild it so satellites use the new strategy
        try:
            if simulation_state.get('multi_satellite_enabled'):
                num_satellites = len(simulation_state.get('constellation').satellites) if simulation_state.get('constellation') else 5
                if simulation_state.get('env') is None:
                    simulation_state['env'] = simpy.Environment()
                if simulation_state.get('config') is None:
                    simulation_state['config'] = SimulationConfig()
                simulation_state['constellation'] = create_leo_constellation(
                    simulation_state['env'],
                    simulation_state['config'],
                    num_satellites=num_satellites,
                    caching_strategy=strategy
                )
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'message': f'Caching strategy set to {strategy}',
            'strategy': strategy
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/get_caching_strategies', methods=['GET'])
@login_required
def get_caching_strategies():
    """Get available caching strategies and current selection"""
    return jsonify({
        'available_strategies': [
            {'id': 'LRU', 'name': 'Least Recently Used', 'description': 'Evicts least recently accessed items'},
            {'id': 'LFU', 'name': 'Least Frequently Used', 'description': 'Evicts least frequently accessed items'},
            {'id': 'FIFO', 'name': 'First In First Out', 'description': 'Evicts oldest items first'},
            {'id': 'ADAPTIVE', 'name': 'Adaptive', 'description': 'Automatically switches between strategies based on performance'}
        ],
        'current_strategy': simulation_state.get('caching_strategy', 'LRU')
    })

@app.route('/api/create_collaboration_session', methods=['POST'])
@login_required
def create_collaboration_session():
    """Create a new real-time collaboration session"""
    try:
        data = request.get_json() or {}
        config = data.get('config', {})
        
        session_id = f"collab_{current_user.id}_{int(time.time())}"
        
        session_data = collaboration_manager.create_session(
            session_id=session_id,
            creator_id=current_user.id,
            config=config
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'session_data': session_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/join_collaboration_session', methods=['POST'])
@login_required
def join_collaboration_session():
    """Join an existing collaboration session"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        session_data = collaboration_manager.join_session(session_id, current_user.id)
        
        if session_data:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'session_data': session_data
            })
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/collaboration_session/<session_id>', methods=['GET'])
@login_required
def get_collaboration_session(session_id):
    """Get collaboration session details"""
    try:
        session_data = collaboration_manager.get_session(session_id)
        
        if session_data:
            return jsonify({
                'success': True,
                'session': session_data
            })
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/multi_satellite_request', methods=['POST'])
@login_required
def multi_satellite_request():
    """Make a content request using multi-satellite constellation"""
    try:
        if not simulation_state.get('multi_satellite_enabled'):
            return jsonify({
                'success': False,
                'error': 'Multi-satellite mode not enabled. Call /api/enable_multi_satellite first'
            }), 400
        
        data = request.get_json() or {}
        content_id = data.get('content_id')
        user_id = str(current_user.id)
        
        if not content_id:
            return jsonify({'success': False, 'error': 'Content ID required'}), 400
        
        constellation = simulation_state.get('constellation')
        if not constellation:
            return jsonify({'success': False, 'error': 'Constellation not initialized'}), 400
        
        # Assign user to a satellite
        satellite = constellation.assign_user_to_satellite(user_id)
        try:
            simulation_state['last_connected_satellite_by_user'][int(current_user.id)] = satellite.satellite_id
        except Exception:
            pass
        
        # Get content from catalog
        from realistic_content_catalog import get_content_by_id
        content_item = get_content_by_id(content_id)
        
        if not content_item:
            return jsonify({'success': False, 'error': 'Content not found'}), 404
        
        # Convert ContentItem to Content for simulation
        from enhanced_satellite_cdn import Content
        content = Content(
            content_id=content_item.content_id,
            size=content_item.size_mb,
            content_type=content_item.content_type,
            popularity=content_item.popularity_score
        )
        
        # Make request
        result = satellite.request_content(content_id, content, user_id)

        # Add a simple delivery time estimate for UI consistency
        status = str(result.get('status', '')).lower()
        if 'hit' in status:
            est_delivery_time = 0.15
        else:
            est_delivery_time = 1.50
        
        # Broadcast to collaboration session if active
        user_session_id = collaboration_manager.get_user_session(current_user.id)
        if user_session_id:
            collaboration_manager.add_request(user_session_id, result)
            collaboration_manager.update_cache_state(user_session_id, {
                'satellite_id': satellite.satellite_id,
                'cache_size': len(satellite.cache),
                'cache_capacity': satellite.cache_size,
                'utilization': len(satellite.cache) / satellite.cache_size if satellite.cache_size > 0 else 0
            })
        
        # Determine actual strategy used by the satellite (handle ADAPTIVE)
        strategy_used = simulation_state.get('caching_strategy', 'LRU')
        strategy_current = None
        try:
            cache_stats_now = satellite.cache_policy.get_stats()
            if cache_stats_now.get('adaptive'):
                strategy_used = 'ADAPTIVE'
                strategy_current = cache_stats_now.get('current_strategy', cache_stats_now.get('strategy'))
            else:
                strategy_used = cache_stats_now.get('strategy', strategy_used)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'result': {
                **result,
                'delivery_time': est_delivery_time
            },
            'satellite_id': satellite.satellite_id,
            'multi_satellite': True,
            'caching_strategy': strategy_used,
            'caching_strategy_current': strategy_current,
            'content_received': {
                'content_id': content_item.content_id,
                'title': content_item.title,
                'content_type': content_item.content_type,
                'size_mb': content_item.size_mb,
                'description': content_item.description,
                'category': content_item.category,
                'received_at': datetime.utcnow().isoformat()
            },
            'constellation_stats': constellation.get_constellation_stats()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables including new models
        db.create_all()
        create_default_admin()
        
        # Initialize default satellites if none exist
        if SatelliteNode.query.count() == 0:
            default_satellites = [
                SatelliteNode(
                    satellite_id='LEO-1',
                    name='LEO Satellite 1',
                    latitude=0.0,
                    longitude=0.0,
                    altitude=550.0,
                    cache_size=12,
                    status='active'
                ),
                SatelliteNode(
                    satellite_id='LEO-2',
                    name='LEO Satellite 2',
                    latitude=30.0,
                    longitude=60.0,
                    altitude=550.0,
                    cache_size=12,
                    status='active'
                ),
                SatelliteNode(
                    satellite_id='LEO-3',
                    name='LEO Satellite 3',
                    latitude=-30.0,
                    longitude=120.0,
                    altitude=550.0,
                    cache_size=12,
                    status='active'
                )
            ]
            for sat in default_satellites:
                db.session.add(sat)
            db.session.commit()
            print("Default satellites initialized")
    
    # Run with SocketIO for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 