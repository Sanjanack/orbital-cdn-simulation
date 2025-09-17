"""
Satellite-Based Content Delivery Network (CDN) Simulation
========================================================

This simulation models a single satellite's caching behavior using SimPy.
It implements an LRU (Least Recently Used) caching strategy and tracks
cache hit rates for content delivery optimization.

Author: AI Assistant
Date: 2025
"""

import simpy
import random
import csv
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional
from content_data import CONTENT_CATALOG

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Content:
    """
    Represents a content item that can be cached and delivered by the satellite.
    
    Attributes:
        content_id (str): Unique identifier for the content
        size (int): Size of the content in MB
        popularity (float): Popularity score (0.0 to 1.0) for request generation
    """
    content_id: str
    size: int
    popularity: float = 1.0

# =============================================================================
# SATELLITE CLASS WITH LRU CACHE
# =============================================================================

class Satellite:
    """
    Represents a satellite with an LRU (Least Recently Used) cache.
    
    The satellite receives content requests and either serves them from cache
    (hit) or fetches them from the ground station (miss). The cache uses
    an LRU eviction policy to manage limited storage space.
    """
    
    def __init__(self, env: simpy.Environment, cache_size: int = 10):
        """
        Initialize the satellite with a fixed-size LRU cache.
        
        Args:
            env: SimPy environment for simulation timing
            cache_size: Maximum number of content items the cache can hold
        """
        self.env = env
        self.cache_size = cache_size
        self.cache: OrderedDict[str, Content] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.request_log: List[Dict] = []
        
        # Performance metrics
        self.total_requests = 0
        self.cache_utilization = 0.0
        
    def request_content(self, content_id: str, content: Content) -> Dict:
        """
        Handle a content request using LRU caching strategy.
        
        Args:
            content_id: ID of the requested content
            content: Content object to cache if needed
            
        Returns:
            Dict containing request details and cache status
        """
        self.total_requests += 1
        current_time = self.env.now
        
        # Check if content is in cache
        if content_id in self.cache:
            # Cache HIT - move to end (most recently used)
            self.cache.move_to_end(content_id)
            self.hits += 1
            status = 'Hit'
        else:
            # Cache MISS - add to cache
            self.misses += 1
            status = 'Miss'
            
            # If cache is full, remove least recently used item
            if len(self.cache) >= self.cache_size:
                # Remove the first item (least recently used)
                self.cache.popitem(last=False)
            
            # Add new content to cache (most recently used)
            self.cache[content_id] = content
        
        # Update cache utilization
        self.cache_utilization = len(self.cache) / self.cache_size
        
        # Create log entry
        log_entry = {
            'timestamp': current_time,
            'content_id': content_id,
            'content_size': content.size,
            'status': status,
            'cache_size': len(self.cache),
            'cache_utilization': self.cache_utilization
        }
        
        self.request_log.append(log_entry)
        return log_entry
    
    def get_hit_rate(self) -> float:
        """
        Calculate the current cache hit rate.
        
        Returns:
            Hit rate as a percentage (0.0 to 100.0)
        """
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
    
    def get_cache_status(self) -> Dict:
        """
        Get current cache status and statistics.
        
        Returns:
            Dict containing cache statistics
        """
        return {
            'total_requests': self.total_requests,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.get_hit_rate(),
            'cache_size': len(self.cache),
            'cache_utilization': self.cache_utilization,
            'cached_content': list(self.cache.keys())
        }

# =============================================================================
# USER REQUEST PROCESS
# =============================================================================

def user_request_process(env: simpy.Environment, satellite: Satellite, 
                        content_catalog: List[Content], 
                        request_interval: float = 2.0,
                        simulation_duration: float = 100.0):
    """
    SimPy process that generates periodic content requests.
    
    This process simulates multiple users making requests to the satellite.
    Requests are generated based on content popularity and random selection.
    
    Args:
        env: SimPy environment
        satellite: Satellite instance to receive requests
        content_catalog: List of available content items
        request_interval: Time between requests (simulation time units)
        simulation_duration: Total simulation duration
    """
    
    # Create popularity-weighted content selection
    content_weights = [content.popularity for content in content_catalog]
    
    while env.now < simulation_duration:
        try:
            # Select content based on popularity weights
            selected_content = random.choices(content_catalog, weights=content_weights)[0]
            
            # Make request to satellite
            log_entry = satellite.request_content(selected_content.content_id, selected_content)
            
            # Print request details (optional, for debugging)
            print(f"Time {env.now:.1f}: Request for {selected_content.content_id} - {log_entry['status']}")
            
            # Wait before next request
            yield env.timeout(request_interval)
            
        except simpy.Interrupt:
            print("User request process interrupted")
            break

# =============================================================================
# SIMULATION SETUP AND EXECUTION
# =============================================================================

def create_content_catalog() -> List[Content]:
    """
    Create a content catalog with popularity scores for realistic request patterns.
    
    Returns:
        List of Content objects with popularity weights
    """
    content_list = []
    
    # Convert existing CONTENT_CATALOG to Content objects with popularity
    for item in CONTENT_CATALOG:
        # Assign popularity based on content type and size
        if 'video' in item['id'].lower():
            popularity = 0.8  # Videos are popular
        elif 'image' in item['id'].lower():
            popularity = 0.6  # Images are moderately popular
        elif 'audio' in item['id'].lower():
            popularity = 0.7  # Audio is popular
        elif 'game' in item['id'].lower():
            popularity = 0.9  # Games are very popular
        else:
            popularity = 0.5  # Default popularity
            
        content = Content(
            content_id=item['id'],
            size=item['size'],
            popularity=popularity
        )
        content_list.append(content)
    
    # Add some additional content for variety
    additional_content = [
        Content('video_streaming', 150, 0.85),
        Content('live_sports', 200, 0.95),
        Content('news_update', 30, 0.4),
        Content('weather_data', 25, 0.3),
        Content('social_media', 80, 0.75)
    ]
    
    content_list.extend(additional_content)
    return content_list

def save_simulation_log(satellite: Satellite, filename: str = 'simulation_log.csv'):
    """
    Save simulation results to a CSV file.
    
    Args:
        satellite: Satellite instance containing the log data
        filename: Output CSV filename
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'content_id', 'content_size', 'status', 
                     'cache_size', 'cache_utilization']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for log_entry in satellite.request_log:
            writer.writerow(log_entry)
    
    print(f"Simulation log saved to {filename}")

def print_simulation_summary(satellite: Satellite):
    """
    Print a comprehensive summary of simulation results.
    
    Args:
        satellite: Satellite instance with simulation data
    """
    stats = satellite.get_cache_status()
    
    print("\n" + "="*60)
    print("SATELLITE CDN SIMULATION RESULTS")
    print("="*60)
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Cache Hits: {stats['hits']}")
    print(f"Cache Misses: {stats['misses']}")
    print(f"Cache Hit Rate: {stats['hit_rate']:.2f}%")
    print(f"Final Cache Size: {stats['cache_size']}/{satellite.cache_size}")
    print(f"Cache Utilization: {stats['cache_utilization']:.2f}")
    print(f"Cached Content: {', '.join(stats['cached_content'])}")
    print("="*60)

def main():
    """
    Main simulation function that orchestrates the entire simulation.
    """
    print("Starting Satellite CDN Simulation...")
    print("="*50)
    
    # Simulation parameters
    SIMULATION_DURATION = 100.0  # simulation time units
    REQUEST_INTERVAL = 2.0       # time between requests
    CACHE_SIZE = 8              # maximum cache entries
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create content catalog
    content_catalog = create_content_catalog()
    print(f"Created content catalog with {len(content_catalog)} items")
    
    # Create satellite with LRU cache
    satellite = Satellite(env, cache_size=CACHE_SIZE)
    print(f"Initialized satellite with {CACHE_SIZE}-item LRU cache")
    
    # Start user request process
    env.process(user_request_process(env, satellite, content_catalog, 
                                   REQUEST_INTERVAL, SIMULATION_DURATION))
    
    # Run simulation
    print(f"\nRunning simulation for {SIMULATION_DURATION} time units...")
    start_time = time.time()
    env.run(until=SIMULATION_DURATION)
    end_time = time.time()
    
    # Calculate and display results
    print(f"\nSimulation completed in {end_time - start_time:.2f} seconds")
    
    # Force print the summary
    print_simulation_summary(satellite)
    
    # Save results to CSV
    save_simulation_log(satellite)
    
    print("\nSimulation completed successfully!")

if __name__ == "__main__":
    main() 