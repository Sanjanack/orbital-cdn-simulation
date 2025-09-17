"""
Live Satellite CDN Simulation with Real-time Data Visualization
==============================================================

This enhanced simulation provides live data streaming, real-time visualizations,
and interactive controls for presenting the satellite CDN project.

Team Members: 
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)

Features:
- Real-time data streaming
- Interactive web dashboard
- Live performance metrics
- Content type analysis
- Cache visualization
- User activity monitoring
"""

from flask import Flask, render_template, jsonify, request
import simpy
import random
import threading
import time
import json
from collections import OrderedDict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from content_data import CONTENT_CATALOG

app = Flask(__name__)

# Global simulation state
simulation_state = {
    'running': False,
    'paused': False,
    'speed': 1.0,  # Simulation speed multiplier
    'start_time': None,
    'current_time': 0.0
}

# Real-time data storage
live_data = {
    'requests': deque(maxlen=1000),  # Recent requests
    'performance': deque(maxlen=100),  # Performance metrics
    'cache_status': {},  # Current cache state
    'user_activity': {},  # User request patterns
    'content_stats': {},  # Content type statistics
    'system_metrics': {}  # System performance metrics
}

@dataclass
class LiveContent:
    """Enhanced content class for live simulation"""
    content_id: str
    size: int
    content_type: str
    popularity: float
    request_count: int = 0
    last_requested: float = 0.0

class LiveSatellite:
    """Enhanced satellite with live monitoring capabilities"""
    
    def __init__(self, env: simpy.Environment, cache_size: int = 15):
        self.env = env
        self.cache_size = cache_size
        self.cache: OrderedDict[str, LiveContent] = OrderedDict()
        
        # Performance tracking
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_evictions = 0
        self.total_content_delivered = 0
        
        # Real-time metrics
        self.request_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=50)
        
    def request_content(self, content: LiveContent, user_id: str) -> Dict:
        """Handle content request with live data logging"""
        self.total_requests += 1
        current_time = self.env.now
        
        # Update content request count
        content.request_count += 1
        content.last_requested = current_time
        
        # Check cache
        if content.content_id in self.cache:
            # Cache HIT
            self.cache.move_to_end(content.content_id)
            self.cache_hits += 1
            status = 'Hit'
            delivery_source = 'Satellite Cache'
        else:
            # Cache MISS
            self.cache_misses += 1
            status = 'Miss'
            delivery_source = 'Ground Station'
            
            # Handle cache eviction if full
            if len(self.cache) >= self.cache_size:
                evicted = self.cache.popitem(last=False)
                self.cache_evictions += 1
            
            # Add to cache
            self.cache[content.content_id] = content
        
        # Update delivery stats
        self.total_content_delivered += content.size
        
        # Create live data entry
        live_entry = {
            'timestamp': current_time,
            'user_id': user_id,
            'content_id': content.content_id,
            'content_type': content.content_type,
            'content_size': content.size,
            'status': status,
            'delivery_source': delivery_source,
            'cache_size': len(self.cache),
            'cache_utilization': len(self.cache) / self.cache_size,
            'hit_rate': (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0
        }
        
        # Update live data
        live_data['requests'].append(live_entry)
        self.request_history.append(live_entry)
        
        # Update cache status
        live_data['cache_status'] = {
            'current_size': len(self.cache),
            'max_size': self.cache_size,
            'utilization': len(self.cache) / self.cache_size,
            'cached_items': list(self.cache.keys()),
            'evictions': self.cache_evictions
        }
        
        # Update user activity
        if user_id not in live_data['user_activity']:
            live_data['user_activity'][user_id] = {'requests': 0, 'hits': 0, 'misses': 0}
        live_data['user_activity'][user_id]['requests'] += 1
        if status == 'Hit':
            live_data['user_activity'][user_id]['hits'] += 1
        else:
            live_data['user_activity'][user_id]['misses'] += 1
        
        # Update content statistics
        if content.content_type not in live_data['content_stats']:
            live_data['content_stats'][content.content_type] = {'requests': 0, 'hits': 0, 'size': 0}
        live_data['content_stats'][content.content_type]['requests'] += 1
        live_data['content_stats'][content.content_type]['size'] += content.size
        if status == 'Hit':
            live_data['content_stats'][content.content_type]['hits'] += 1
        
        return live_entry
    
    def get_live_metrics(self) -> Dict:
        """Get current live performance metrics"""
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0,
            'cache_evictions': self.cache_evictions,
            'total_content_delivered': self.total_content_delivered,
            'cache_utilization': len(self.cache) / self.cache_size,
            'current_time': self.env.now
        }

def create_live_content_catalog() -> List[LiveContent]:
    """Create enhanced content catalog for live simulation"""
    content_list = []
    
    # Convert existing content
    for item in CONTENT_CATALOG:
        if 'video' in item['id'].lower():
            content_type = 'video'
            popularity = 0.85
        elif 'image' in item['id'].lower():
            content_type = 'image'
            popularity = 0.65
        elif 'audio' in item['id'].lower():
            content_type = 'audio'
            popularity = 0.75
        elif 'game' in item['id'].lower():
            content_type = 'game'
            popularity = 0.95
        else:
            content_type = 'document'
            popularity = 0.45
            
        content = LiveContent(
            content_id=item['id'],
            size=item['size'],
            content_type=content_type,
            popularity=popularity
        )
        content_list.append(content)
    
    # Add additional content for variety
    additional_content = [
        LiveContent('live_sports_stream', 250, 'video', 0.98),
        LiveContent('breaking_news', 15, 'document', 0.60),
        LiveContent('weather_forecast', 8, 'document', 0.40),
        LiveContent('music_playlist', 120, 'audio', 0.80),
        LiveContent('educational_video', 180, 'video', 0.70),
        LiveContent('social_media_feed', 45, 'document', 0.75),
        LiveContent('gaming_tutorial', 95, 'video', 0.85),
        LiveContent('podcast_episode', 85, 'audio', 0.65),
        LiveContent('product_catalog', 35, 'document', 0.30),
        LiveContent('live_concert', 300, 'video', 0.90),
        LiveContent('esports_tournament', 400, 'video', 0.99),
        LiveContent('virtual_reality_game', 500, 'game', 0.97),
        LiveContent('ai_generated_content', 80, 'video', 0.75),
        LiveContent('blockchain_data', 25, 'document', 0.35),
        LiveContent('quantum_computing_demo', 150, 'video', 0.80)
    ]
    
    content_list.extend(additional_content)
    return content_list

def live_user_process(env: simpy.Environment, satellite: LiveSatellite, 
                     content_catalog: List[LiveContent], user_id: str):
    """Enhanced user process with live data generation"""
    content_weights = [content.popularity for content in content_catalog]
    
    while simulation_state['running']:
        try:
            # Check if simulation is paused
            if simulation_state['paused']:
                yield env.timeout(1)
                continue
            
            # Select content based on popularity
            selected_content = random.choices(content_catalog, weights=content_weights)[0]
            
            # Make request
            log_entry = satellite.request_content(selected_content, user_id)
            
            # Update simulation time
            simulation_state['current_time'] = env.now
            
            # Wait based on simulation speed
            yield env.timeout(2.0 / simulation_state['speed'])
            
        except simpy.Interrupt:
            break

def performance_monitor(env: simpy.Environment, satellite: LiveSatellite):
    """Monitor performance and update live data"""
    while simulation_state['running']:
        try:
            metrics = satellite.get_live_metrics()
            live_data['performance'].append({
                'timestamp': env.now,
                **metrics
            })
            
            # Update system metrics
            live_data['system_metrics'] = {
                'simulation_time': env.now,
                'real_time': time.time(),
                'speed': simulation_state['speed'],
                'status': 'Paused' if simulation_state['paused'] else 'Running'
            }
            
            yield env.timeout(5.0 / simulation_state['speed'])
            
        except simpy.Interrupt:
            break

def run_live_simulation():
    """Main simulation runner"""
    global simulation_state
    
    # Initialize simulation
    env = simpy.Environment()
    content_catalog = create_live_content_catalog()
    satellite = LiveSatellite(env, cache_size=15)
    
    # Start processes
    user_processes = []
    for i in range(5):  # 5 users
        user_id = f"User_{i+1}"
        process = env.process(live_user_process(env, satellite, content_catalog, user_id))
        user_processes.append(process)
    
    # Start performance monitoring
    monitor_process = env.process(performance_monitor(env, satellite))
    
    # Run simulation
    simulation_state['start_time'] = time.time()
    while simulation_state['running']:
        try:
            env.run(until=env.now + 10)  # Run in chunks
            time.sleep(0.1)  # Small delay for web responsiveness
        except:
            break
    
    # Cleanup
    for process in user_processes:
        process.interrupt()
    monitor_process.interrupt()

# Flask Routes
@app.route('/')
def index():
    return render_template('live_dashboard.html')

@app.route('/api/start_simulation')
def start_simulation():
    if not simulation_state['running']:
        simulation_state['running'] = True
        simulation_state['paused'] = False
        thread = threading.Thread(target=run_live_simulation)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/api/stop_simulation')
def stop_simulation():
    simulation_state['running'] = False
    return jsonify({'status': 'stopped'})

@app.route('/api/pause_simulation')
def pause_simulation():
    simulation_state['paused'] = not simulation_state['paused']
    return jsonify({'status': 'paused' if simulation_state['paused'] else 'resumed'})

@app.route('/api/set_speed')
def set_speed():
    speed = request.args.get('speed', 1.0, type=float)
    simulation_state['speed'] = max(0.1, min(5.0, speed))  # Limit between 0.1x and 5x
    return jsonify({'status': 'speed_updated', 'speed': simulation_state['speed']})

@app.route('/api/live_data')
def get_live_data():
    return jsonify({
        'requests': list(live_data['requests'])[-50:],  # Last 50 requests
        'performance': list(live_data['performance'])[-20:],  # Last 20 performance points
        'cache_status': live_data['cache_status'],
        'user_activity': live_data['user_activity'],
        'content_stats': live_data['content_stats'],
        'system_metrics': live_data['system_metrics']
    })

@app.route('/api/simulation_status')
def get_simulation_status():
    return jsonify(simulation_state)

if __name__ == '__main__':
    print("🚀 Starting Live Satellite CDN Simulation...")
    print("📊 Access the dashboard at: http://localhost:5000")
    print("🎯 Features: Real-time data, interactive controls, live metrics")
    app.run(debug=True, host='0.0.0.0', port=5000) 