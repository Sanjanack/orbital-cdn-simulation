from flask import Flask, render_template, jsonify
import simpy
import random
import threading
import time
from content_data import CONTENT_CATALOG

app = Flask(__name__)

# Global variables to store simulation state
simulation_log = []
simulation_running = False
env = None
satellite_node = None

class SatelliteNode:
    def __init__(self, env):
        self.env = env
        self.cache = {}
    
    def handle_request(self, env, content_id):
        log_entry = {
            'time': env.now,
            'type': 'satellite_response',
            'content_id': content_id,
            'message': f'Satellite received request for content: {content_id}'
        }
        simulation_log.append(log_entry)

def user_agent(env, satellite_node):
    while simulation_running:
        try:
            # Randomly select a content_id from the CONTENT_CATALOG
            content_item = random.choice(CONTENT_CATALOG)
            content_id = content_item['id']
            
            # Log user request
            log_entry = {
                'time': env.now,
                'type': 'user_request',
                'content_id': content_id,
                'message': f'User requesting content: {content_id}'
            }
            simulation_log.append(log_entry)
            
            # Send request to satellite
            satellite_node.handle_request(env, content_id)
            
            # Wait for 2 simulated time units before next request
            yield env.timeout(2)
        except simpy.Interrupt:
            break

def run_simulation():
    global env, satellite_node, simulation_running
    simulation_running = True
    simulation_log.clear()
    
    # Create the simulation environment
    env = simpy.Environment()
    
    # Instantiate the SatelliteNode
    satellite_node = SatelliteNode(env)
    
    # Start two user_agent processes
    env.process(user_agent(env, satellite_node))
    env.process(user_agent(env, satellite_node))
    
    # Run the simulation for 30 time units
    env.run(until=30)
    
    simulation_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_simulation')
def start_simulation():
    global simulation_running
    if not simulation_running:
        thread = threading.Thread(target=run_simulation)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/get_logs')
def get_logs():
    return jsonify(simulation_log)

@app.route('/stop_simulation')
def stop_simulation():
    global simulation_running
    simulation_running = False
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 