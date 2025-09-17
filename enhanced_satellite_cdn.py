"""
Orbital CDN – Simulating Content Delivery Network via Satellites
================================================================

Team Members: 
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)

Project Description:
This simulation models a single LEO satellite serving as a content delivery node,
implementing LRU caching strategy to improve content availability in remote regions.

Technical Stack:
- Core Programming Language: Python 3.x
- Simulation Framework: SimPy (for discrete-event simulation)
- Data Storage: CSV (for logging simulation events)
- Data Analysis: Pandas (for efficient processing of CSV logs)

Author: Team Orbital CDN
Date: 2025
"""

import simpy
import random
import csv
import time
import pandas as pd
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# ENTITY DEFINITIONS
# =============================================================================

@dataclass
class Content:
    """
    Content entity representing digital content items that can be cached and delivered.
    
    Attributes:
        content_id (str): Unique identifier for the content
        size (int): Size of the content in MB
        content_type (str): Type of content (video, image, document, audio, game)
        popularity (float): Popularity score (0.0 to 1.0) for request generation
        creation_time (float): Simulation time when content was created
    """
    content_id: str
    size: int
    content_type: str
    popularity: float = 1.0
    creation_time: float = 0.0

@dataclass
class SimulationConfig:
    """
    Configuration parameters for the satellite CDN simulation.
    
    Attributes:
        simulation_duration (float): Total simulation time in units
        request_interval (float): Time between user requests
        cache_size (int): Maximum number of content items in satellite cache
        content_catalog_size (int): Number of content items in the catalog
        user_count (int): Number of simulated users
        log_interval (float): Interval for performance logging
    """
    simulation_duration: float = 200.0
    request_interval: float = 3.0
    cache_size: int = 10
    content_catalog_size: int = 20
    user_count: int = 3
    log_interval: float = 10.0

# =============================================================================
# SATELLITE CLASS WITH LRU CACHE
# =============================================================================

class Satellite:
    """
    Represents a Low Earth Orbit (LEO) satellite with LRU caching capabilities.
    
    The satellite serves as a content delivery node, receiving requests from users
    and either serving content from its cache (hit) or fetching from ground station (miss).
    Implements Least Recently Used (LRU) eviction policy for cache management.
    """
    
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        """
        Initialize the satellite with LRU cache and performance tracking.
        
        Args:
            env: SimPy environment for simulation timing
            config: Simulation configuration parameters
        """
        self.env = env
        self.config = config
        self.cache_size = config.cache_size
        
        # LRU Cache Implementation using OrderedDict
        self.cache: OrderedDict[str, Content] = OrderedDict()
        
        # Performance Metrics
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_content_delivered = 0  # MB
        self.cache_evictions = 0
        
        # Request Logging
        self.request_log: List[Dict] = []
        self.performance_log: List[Dict] = []
        
        # Cache Statistics
        self.cache_utilization_history: List[float] = []
        self.hit_rate_history: List[float] = []
        
    def request_content(self, content_id: str, content: Content, user_id: str) -> Dict:
        """
        Handle a content request using LRU caching strategy.
        
        Args:
            content_id: ID of the requested content
            content: Content object to cache if needed
            user_id: ID of the requesting user
            
        Returns:
            Dict containing request details and cache status
        """
        self.total_requests += 1
        current_time = self.env.now
        
        # Check if content is in cache
        if content_id in self.cache:
            # Cache HIT - move to end (most recently used)
            self.cache.move_to_end(content_id)
            self.cache_hits += 1
            status = 'Hit'
            delivery_source = 'Satellite Cache'
        else:
            # Cache MISS - add to cache
            self.cache_misses += 1
            status = 'Miss'
            delivery_source = 'Ground Station'
            
            # If cache is full, remove least recently used item
            if len(self.cache) >= self.cache_size:
                # Remove the first item (least recently used)
                evicted_content = self.cache.popitem(last=False)
                self.cache_evictions += 1
            
            # Add new content to cache (most recently used)
            self.cache[content_id] = content
        
        # Update delivery statistics
        self.total_content_delivered += content.size
        
        # Calculate current metrics
        cache_utilization = len(self.cache) / self.cache_size
        hit_rate = (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0
        
        # Create detailed log entry
        log_entry = {
            'timestamp': current_time,
            'user_id': user_id,
            'content_id': content_id,
            'content_type': content.content_type,
            'content_size': content.size,
            'status': status,
            'delivery_source': delivery_source,
            'cache_size': len(self.cache),
            'cache_utilization': cache_utilization,
            'hit_rate': hit_rate,
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses
        }
        
        self.request_log.append(log_entry)
        return log_entry
    
    def log_performance(self):
        """Log current performance metrics for analysis."""
        current_time = self.env.now
        cache_utilization = len(self.cache) / self.cache_size
        hit_rate = (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0
        
        performance_entry = {
            'timestamp': current_time,
            'cache_utilization': cache_utilization,
            'hit_rate': hit_rate,
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_evictions': self.cache_evictions,
            'total_content_delivered': self.total_content_delivered
        }
        
        self.performance_log.append(performance_entry)
        self.cache_utilization_history.append(cache_utilization)
        self.hit_rate_history.append(hit_rate)
    
    def get_final_statistics(self) -> Dict:
        """
        Calculate final simulation statistics.
        
        Returns:
            Dict containing comprehensive simulation results
        """
        final_hit_rate = (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0
        avg_cache_utilization = sum(self.cache_utilization_history) / len(self.cache_utilization_history) if self.cache_utilization_history else 0
        
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': final_hit_rate,
            'cache_evictions': self.cache_evictions,
            'total_content_delivered_mb': self.total_content_delivered,
            'average_cache_utilization': avg_cache_utilization,
            'final_cache_size': len(self.cache),
            'cached_content': list(self.cache.keys()),
            'simulation_duration': self.env.now
        }

# =============================================================================
# USER REQUEST PROCESS
# =============================================================================

def user_request_process(env: simpy.Environment, satellite: Satellite, 
                        content_catalog: List[Content], user_id: str,
                        config: SimulationConfig):
    """
    SimPy process that generates periodic content requests from a user.
    
    This process simulates a user making requests to the satellite CDN.
    Requests are generated based on content popularity and random selection.
    
    Args:
        env: SimPy environment
        satellite: Satellite instance to receive requests
        content_catalog: List of available content items
        user_id: Unique identifier for this user
        config: Simulation configuration
    """
    
    # Create popularity-weighted content selection
    content_weights = [content.popularity for content in content_catalog]
    
    while env.now < config.simulation_duration:
        try:
            # Select content based on popularity weights
            selected_content = random.choices(content_catalog, weights=content_weights)[0]
            
            # Make request to satellite
            log_entry = satellite.request_content(selected_content.content_id, selected_content, user_id)
            
            # Print request details for monitoring
            print(f"Time {env.now:.1f}: User {user_id} requested {selected_content.content_id} ({selected_content.content_type}) - {log_entry['status']}")
            
            # Wait before next request
            yield env.timeout(config.request_interval)
            
        except simpy.Interrupt:
            print(f"User {user_id} request process interrupted")
            break

# =============================================================================
# PERFORMANCE MONITORING PROCESS
# =============================================================================

def performance_monitor_process(env: simpy.Environment, satellite: Satellite, config: SimulationConfig):
    """
    SimPy process that periodically logs performance metrics.
    
    Args:
        env: SimPy environment
        satellite: Satellite instance to monitor
        config: Simulation configuration
    """
    while env.now < config.simulation_duration:
        satellite.log_performance()
        yield env.timeout(config.log_interval)

# =============================================================================
# CONTENT CATALOG GENERATION
# =============================================================================

def create_content_catalog(config: SimulationConfig) -> List[Content]:
    """
    Create a comprehensive content catalog with realistic content types and popularity.
    
    Args:
        config: Simulation configuration
        
    Returns:
        List of Content objects with diverse content types and popularity scores
    """
    content_list = []
    
    # Convert existing CONTENT_CATALOG to Content objects
    from content_data import CONTENT_CATALOG
    
    for item in CONTENT_CATALOG:
        # Determine content type and popularity
        if 'video' in item['id'].lower():
            content_type = 'video'
            popularity = 0.85  # Videos are very popular
        elif 'image' in item['id'].lower():
            content_type = 'image'
            popularity = 0.65  # Images are moderately popular
        elif 'audio' in item['id'].lower():
            content_type = 'audio'
            popularity = 0.75  # Audio is popular
        elif 'game' in item['id'].lower():
            content_type = 'game'
            popularity = 0.95  # Games are extremely popular
        else:
            content_type = 'document'
            popularity = 0.45  # Documents are less popular
            
        content = Content(
            content_id=item['id'],
            size=item['size'],
            content_type=content_type,
            popularity=popularity,
            creation_time=0.0
        )
        content_list.append(content)
    
    # Add additional content for comprehensive testing
    additional_content = [
        Content('live_sports_stream', 250, 'video', 0.98),
        Content('breaking_news', 15, 'document', 0.60),
        Content('weather_forecast', 8, 'document', 0.40),
        Content('music_playlist', 120, 'audio', 0.80),
        Content('educational_video', 180, 'video', 0.70),
        Content('social_media_feed', 45, 'document', 0.75),
        Content('gaming_tutorial', 95, 'video', 0.85),
        Content('podcast_episode', 85, 'audio', 0.65),
        Content('product_catalog', 35, 'document', 0.30),
        Content('live_concert', 300, 'video', 0.90)
    ]
    
    content_list.extend(additional_content)
    
    # Ensure we have the requested catalog size
    if len(content_list) > config.content_catalog_size:
        content_list = content_list[:config.content_catalog_size]
    
    return content_list

# =============================================================================
# DATA ANALYSIS AND VISUALIZATION
# =============================================================================

def analyze_simulation_results(satellite: Satellite, config: SimulationConfig):
    """
    Analyze simulation results and generate comprehensive reports.
    
    Args:
        satellite: Satellite instance with simulation data
        config: Simulation configuration
    """
    
    # Convert logs to pandas DataFrames for analysis
    request_df = pd.DataFrame(satellite.request_log)
    performance_df = pd.DataFrame(satellite.performance_log)
    
    # Calculate detailed statistics
    stats = satellite.get_final_statistics()
    
    print("\n" + "="*80)
    print("ORBITAL CDN SIMULATION - COMPREHENSIVE ANALYSIS")
    print("="*80)
    print(f"Simulation Duration: {stats['simulation_duration']:.1f} time units")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Cache Hits: {stats['cache_hits']}")
    print(f"Cache Misses: {stats['cache_misses']}")
    print(f"Cache Hit Rate: {stats['cache_hit_rate']:.2f}%")
    print(f"Cache Evictions: {stats['cache_evictions']}")
    print(f"Total Content Delivered: {stats['total_content_delivered_mb']:.1f} MB")
    print(f"Average Cache Utilization: {stats['average_cache_utilization']:.2f}")
    print(f"Final Cache Size: {stats['final_cache_size']}/{config.cache_size}")
    
    # Content type analysis
    if not request_df.empty:
        print("\n--- Content Type Analysis ---")
        content_type_stats = request_df.groupby('content_type').agg({
            'status': ['count', lambda x: (x == 'Hit').sum()],
            'content_size': 'sum'
        }).round(2)
        content_type_stats.columns = ['Total Requests', 'Hits', 'Total Size (MB)']
        content_type_stats['Hit Rate (%)'] = (content_type_stats['Hits'] / content_type_stats['Total Requests'] * 100).round(2)
        print(content_type_stats)
    
    print("\n--- Cached Content ---")
    print(f"Currently cached: {', '.join(stats['cached_content'])}")
    print("="*80)
    
    return request_df, performance_df, stats

def save_simulation_data(satellite: Satellite, config: SimulationConfig):
    """
    Save simulation data to CSV files for further analysis.
    
    Args:
        satellite: Satellite instance with simulation data
        config: Simulation configuration
    """
    
    # Save detailed request log
    request_filename = f'satellite_cdn_requests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(request_filename, 'w', newline='', encoding='utf-8') as csvfile:
        if satellite.request_log:
            fieldnames = satellite.request_log[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log_entry in satellite.request_log:
                writer.writerow(log_entry)
    
    # Save performance log
    performance_filename = f'satellite_cdn_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(performance_filename, 'w', newline='', encoding='utf-8') as csvfile:
        if satellite.performance_log:
            fieldnames = satellite.performance_log[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log_entry in satellite.performance_log:
                writer.writerow(log_entry)
    
    print(f"\nSimulation data saved:")
    print(f"- Request log: {request_filename}")
    print(f"- Performance log: {performance_filename}")

# =============================================================================
# MAIN SIMULATION EXECUTION
# =============================================================================

def main():
    """
    Main simulation function that orchestrates the entire satellite CDN simulation.
    """
    print("="*80)
    print("ORBITAL CDN - SATELLITE CONTENT DELIVERY NETWORK SIMULATION")
    print("="*80)
    print("Team Members:")
    print("1. Neha (U25UV23T064063)")
    print("2. Sanjana C K (U25UV22T064049)")
    print("="*80)
    
    # Simulation configuration
    config = SimulationConfig(
        simulation_duration=200.0,
        request_interval=3.0,
        cache_size=12,
        content_catalog_size=20,
        user_count=4,
        log_interval=10.0
    )
    
    print(f"Simulation Configuration:")
    print(f"- Duration: {config.simulation_duration} time units")
    print(f"- Request Interval: {config.request_interval} time units")
    print(f"- Cache Size: {config.cache_size} items")
    print(f"- Content Catalog: {config.content_catalog_size} items")
    print(f"- Users: {config.user_count}")
    print(f"- Performance Logging: Every {config.log_interval} time units")
    print("="*80)
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create content catalog
    content_catalog = create_content_catalog(config)
    print(f"Created content catalog with {len(content_catalog)} items")
    
    # Create satellite with LRU cache
    satellite = Satellite(env, config)
    print(f"Initialized satellite with {config.cache_size}-item LRU cache")
    
    # Start user request processes
    for i in range(config.user_count):
        user_id = f"User_{i+1}"
        env.process(user_request_process(env, satellite, content_catalog, user_id, config))
        print(f"Started {user_id} process")
    
    # Start performance monitoring
    env.process(performance_monitor_process(env, satellite, config))
    print("Started performance monitoring process")
    
    # Run simulation
    print(f"\nRunning simulation for {config.simulation_duration} time units...")
    print("="*80)
    start_time = time.time()
    env.run(until=config.simulation_duration)
    end_time = time.time()
    
    # Calculate and display results
    print(f"\nSimulation completed in {end_time - start_time:.2f} seconds")
    
    # Analyze results
    request_df, performance_df, stats = analyze_simulation_results(satellite, config)
    
    # Save data
    save_simulation_data(satellite, config)
    
    print("\nSimulation completed successfully!")
    print("="*80)

if __name__ == "__main__":
    main() 