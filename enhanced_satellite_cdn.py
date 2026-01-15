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
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

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
