import simpy
import random
from content_data import CONTENT_CATALOG

class SatelliteNode:
    def __init__(self, env):
        self.env = env
        self.cache = {}  # placeholder for satellite's content cache
    
    def handle_request(self, env, content_id):
        print(f"Simulated time: {env.now}, Satellite received request for content: {content_id}")

def user_agent(env, satellite_node):
    while True:
        # Randomly select a content_id from the CONTENT_CATALOG
        content_item = random.choice(CONTENT_CATALOG)
        content_id = content_item['id']
        
        # Print user request message
        print(f"Simulated time: {env.now}, User requesting content: {content_id}")
        
        # Send request to satellite
        satellite_node.handle_request(env, content_id)
        
        # Wait for 5 simulated time units before next request
        yield env.timeout(5)

if __name__ == "__main__":
    # Create the simulation environment
    env = simpy.Environment()
    
    # Instantiate the SatelliteNode
    satellite_node = SatelliteNode(env)
    
    # Start two user_agent processes
    env.process(user_agent(env, satellite_node))
    env.process(user_agent(env, satellite_node))
    
    # Run the simulation for 50 time units
    env.run(until=50)
