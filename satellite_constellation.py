"""
Multi-Satellite Constellation Management
========================================

This module provides support for managing multiple satellites in a constellation,
including inter-satellite communication, load balancing, and geographic distribution.

Team Members:
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

import simpy
import random
import math
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enhanced_satellite_cdn import Satellite, SimulationConfig, Content

from advanced_caching import LRUCache as AdvLRUCache, LFUCache, FIFOCache, AdaptiveCache

def _create_constellation_cache(strategy: str, capacity: int):
    """Create cache object for constellation satellites based on selected strategy."""
    s = (strategy or "LRU").upper()
    if s == "LRU":
        return AdvLRUCache(capacity)
    if s == "LFU":
        return LFUCache(capacity)
    if s == "FIFO":
        return FIFOCache(capacity)
    if s == "ADAPTIVE":
        return AdaptiveCache(capacity)
    return AdvLRUCache(capacity)

@dataclass
class SatellitePosition:
    """Satellite position in 3D space"""
    latitude: float  # degrees
    longitude: float  # degrees
    altitude: float  # km
    velocity: float = 7.5  # km/s (typical LEO velocity)
    
    def distance_to(self, other: 'SatellitePosition') -> float:
        """Calculate distance to another satellite"""
        # Simplified distance calculation
        lat_diff = abs(self.latitude - other.latitude)
        lon_diff = abs(self.longitude - other.longitude)
        alt_diff = abs(self.altitude - other.altitude)
        return math.sqrt(lat_diff**2 + lon_diff**2 + alt_diff**2)

class ConstellationSatellite(Satellite):
    """Enhanced satellite with constellation support"""
    
    def __init__(self, env: simpy.Environment, config: SimulationConfig, 
                 satellite_id: str, position: SatellitePosition, caching_strategy: str = "LRU"):
        super().__init__(env, config)
        self.satellite_id = satellite_id
        self.position = position
        self.constellation = None  # Will be set by Constellation
        self.inter_satellite_requests = 0
        self.inter_satellite_hits = 0
        self.caching_strategy = (caching_strategy or "LRU").upper()
        # Override base OrderedDict cache with advanced cache implementation
        self.cache_policy = _create_constellation_cache(self.caching_strategy, self.cache_size)
        
    def request_content_from_neighbor(self, content_id: str, content: Content) -> Optional[Dict]:
        """Request content from neighboring satellites"""
        if not self.constellation:
            return None
        
        # Find nearest satellites
        neighbors = self.constellation.get_nearest_satellites(self, max_distance=1000)
        
        for neighbor in neighbors:
            if neighbor.satellite_id == self.satellite_id:
                continue
            
            # Check if neighbor has content
            if neighbor.cache_policy.contains(content_id):
                self.inter_satellite_requests += 1
                self.inter_satellite_hits += 1
                
                # Pull from neighbor and store locally
                neighbor_content = neighbor.cache_policy.get(content_id)
                if neighbor_content is None:
                    neighbor_content = content
                self.cache_policy.put(content_id, neighbor_content)
                
                return {
                    'status': 'Neighbor Hit',
                    'source_satellite': neighbor.satellite_id,
                    'distance': self.position.distance_to(neighbor.position)
                }
        
        self.inter_satellite_requests += 1
        return None
    
    def request_content(self, content_id: str, content: Content, user_id: str) -> Dict:
        """Enhanced request with inter-satellite support"""
        self.total_requests += 1
        current_time = self.env.now
        strategy_name = self.cache_policy.get_stats().get('strategy', self.caching_strategy)
        
        # Check local cache first
        if self.cache_policy.contains(content_id):
            self.cache_policy.get(content_id)
            self.cache_hits += 1
            status = 'Hit'
            delivery_source = f'{self.satellite_id} Cache'
        else:
            # Check neighboring satellites
            neighbor_result = self.request_content_from_neighbor(content_id, content)
            
            if neighbor_result:
                self.cache_hits += 1
                status = 'Neighbor Hit'
                delivery_source = f'{neighbor_result["source_satellite"]} (Inter-Satellite)'
            else:
                # Cache MISS - fetch from ground
                self.cache_misses += 1
                status = 'Miss'
                delivery_source = 'Ground Station'
                # Add to cache via selected strategy
                before_evictions = self.cache_policy.get_stats().get('evictions', 0)
                self.cache_policy.put(content_id, content)
                after_evictions = self.cache_policy.get_stats().get('evictions', 0)
                if after_evictions > before_evictions:
                    self.cache_evictions += (after_evictions - before_evictions)
        
        # Update delivery statistics
        self.total_content_delivered += content.size
        
        # Calculate metrics
        cache_stats = self.cache_policy.get_stats()
        cache_utilization = (cache_stats.get('utilization', 0) / 100) if cache_stats.get('utilization', None) is not None else 0
        hit_rate = (self.cache_hits / self.total_requests) * 100 if self.total_requests > 0 else 0
        
        # Create log entry
        log_entry = {
            'timestamp': current_time,
            'user_id': user_id,
            'content_id': content_id,
            'content_type': content.content_type,
            'content_size': content.size,
            'status': status,
            'delivery_source': delivery_source,
            'satellite_id': self.satellite_id,
            'cache_size': cache_stats.get('size', 0),
            'cache_utilization': cache_utilization,
            'hit_rate': hit_rate,
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'inter_satellite_hits': self.inter_satellite_hits,
            'caching_strategy': strategy_name
        }
        
        self.request_log.append(log_entry)
        return log_entry

class SatelliteConstellation:
    """Manages a constellation of satellites"""
    
    def __init__(self, env: simpy.Environment, config: SimulationConfig):
        self.env = env
        self.config = config
        self.satellites: List[ConstellationSatellite] = []
        self.satellite_map: Dict[str, ConstellationSatellite] = {}
        
    def add_satellite(self, satellite_id: str, position: SatellitePosition, caching_strategy: str = "LRU") -> ConstellationSatellite:
        """Add a satellite to the constellation"""
        satellite = ConstellationSatellite(self.env, self.config, satellite_id, position, caching_strategy=caching_strategy)
        satellite.constellation = self
        self.satellites.append(satellite)
        self.satellite_map[satellite_id] = satellite
        return satellite
    
    def get_nearest_satellites(self, reference: ConstellationSatellite, 
                               max_distance: float = 1000) -> List[ConstellationSatellite]:
        """Get nearest satellites to a reference satellite"""
        distances = []
        for sat in self.satellites:
            if sat.satellite_id == reference.satellite_id:
                continue
            dist = reference.position.distance_to(sat.position)
            if dist <= max_distance:
                distances.append((dist, sat))
        
        # Sort by distance
        distances.sort(key=lambda x: x[0])
        return [sat for _, sat in distances[:3]]  # Return top 3 nearest
    
    def get_satellite_by_id(self, satellite_id: str) -> Optional[ConstellationSatellite]:
        """Get satellite by ID"""
        return self.satellite_map.get(satellite_id)
    
    def get_constellation_stats(self) -> Dict:
        """Get overall constellation statistics"""
        total_requests = sum(s.total_requests for s in self.satellites)
        total_hits = sum(s.cache_hits for s in self.satellites)
        total_inter_satellite_hits = sum(s.inter_satellite_hits for s in self.satellites)
        # Strategy may vary for Adaptive; show per-satellite and an overall label
        strategies = []
        for s in self.satellites:
            try:
                strategies.append(s.cache_policy.get_stats().get('strategy', getattr(s, 'caching_strategy', 'LRU')))
            except Exception:
                strategies.append(getattr(s, 'caching_strategy', 'LRU'))
        overall_strategy = strategies[0] if strategies else 'LRU'
        if any(st != overall_strategy for st in strategies):
            overall_strategy = 'ADAPTIVE'
        
        return {
            'total_satellites': len(self.satellites),
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': sum(s.cache_misses for s in self.satellites),
            'overall_hit_rate': (total_hits / total_requests * 100) if total_requests > 0 else 0,
            'inter_satellite_hits': total_inter_satellite_hits,
            'inter_satellite_hit_rate': (total_inter_satellite_hits / total_requests * 100) if total_requests > 0 else 0,
            'caching_strategy': overall_strategy,
            'satellites': [{
                'id': s.satellite_id,
                'position': {
                    'latitude': s.position.latitude,
                    'longitude': s.position.longitude,
                    'altitude': s.position.altitude
                },
                'cache_utilization': (s.cache_policy.get_stats().get('utilization', 0) / 100) if s.cache_size > 0 else 0,
                'hit_rate': (s.cache_hits / s.total_requests * 100) if s.total_requests > 0 else 0,
                'total_requests': s.total_requests,
                'caching_strategy': (s.cache_policy.get_stats().get('strategy', getattr(s, 'caching_strategy', 'LRU')))
            } for s in self.satellites]
        }
    
    def assign_user_to_satellite(self, user_id: str) -> ConstellationSatellite:
        """Assign a user to the nearest satellite"""
        # Simple round-robin assignment
        return self.satellites[hash(user_id) % len(self.satellites)]

def create_leo_constellation(env: simpy.Environment, config: SimulationConfig, 
                            num_satellites: int = 5, caching_strategy: str = "LRU") -> SatelliteConstellation:
    """Create a realistic LEO satellite constellation"""
    constellation = SatelliteConstellation(env, config)
    
    # Create satellites in orbital plane
    for i in range(num_satellites):
        # Distribute satellites evenly around the globe
        latitude = (i * 360 / num_satellites) % 180 - 90  # -90 to 90
        longitude = (i * 360 / num_satellites) % 360  # 0 to 360
        altitude = 550 + random.uniform(-50, 50)  # Typical LEO altitude: 500-600 km
        
        position = SatellitePosition(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude
        )
        
        satellite_id = f'LEO-{i+1}'
        constellation.add_satellite(satellite_id, position, caching_strategy=caching_strategy)
    
    return constellation

