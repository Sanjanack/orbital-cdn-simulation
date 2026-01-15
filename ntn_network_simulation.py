"""
NTN (Non-Terrestrial Network) Satellite CDN Simulation
======================================================

Realistic simulation of satellite-based content delivery network
with proper algorithmic functioning, latency calculations, and
actual content delivery.

Team Members:
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

import simpy
import time
import math
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from realistic_content_catalog import ContentItem, REALISTIC_CONTENT_CATALOG, get_content_by_id

@dataclass
class NetworkMetrics:
    """Network performance metrics"""
    satellite_latency_ms: float = 15.0  # LEO satellite latency
    ground_latency_ms: float = 150.0    # Ground station latency
    satellite_bandwidth_mbps: float = 100.0  # Satellite bandwidth
    ground_bandwidth_mbps: float = 1000.0   # Ground station bandwidth
    packet_loss_rate: float = 0.001  # 0.1% packet loss
    
    def calculate_delivery_time(self, size_mb: float, from_satellite: bool = True) -> float:
        """Calculate realistic delivery time based on size and source"""
        if from_satellite:
            bandwidth = self.satellite_bandwidth_mbps
            latency = self.satellite_latency_ms / 1000.0
        else:
            bandwidth = self.ground_bandwidth_mbps
            latency = self.ground_latency_ms / 1000.0
        
        # Time = (size in MB * 8) / bandwidth in Mbps + latency
        transfer_time = (size_mb * 8) / bandwidth
        total_time = transfer_time + latency
        
        return total_time

class LRUCache:
    """Proper LRU Cache implementation"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, ContentItem] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, content_id: str) -> Optional[ContentItem]:
        """Get content from cache"""
        if content_id in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(content_id)
            self.hits += 1
            return self.cache[content_id]
        self.misses += 1
        return None
    
    def put(self, content_id: str, content: ContentItem):
        """Add content to cache"""
        if content_id in self.cache:
            # Update existing
            self.cache.move_to_end(content_id)
        else:
            # Check if cache is full
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
                self.evictions += 1
            # Add new content
            self.cache[content_id] = content
    
    def contains(self, content_id: str) -> bool:
        """Check if content is in cache"""
        return content_id in self.cache
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'size': len(self.cache),
            'capacity': self.capacity,
            'utilization': len(self.cache) / self.capacity * 100 if self.capacity > 0 else 0
        }

class SatelliteNode:
    """Realistic satellite node with proper NTN functionality"""
    
    def __init__(self, env: simpy.Environment, satellite_id: str, cache_size: int = 12):
        self.env = env
        self.satellite_id = satellite_id
        self.cache = LRUCache(cache_size)
        self.network_metrics = NetworkMetrics()
        
        # Statistics
        self.total_requests = 0
        self.total_content_delivered_mb = 0.0
        self.request_log: List[Dict] = []
        
        # Connection status
        self.connected = True
        self.signal_strength = "Strong"
        self.altitude_km = 550.0
        
    def request_content(self, content_id: str, user_id: str) -> Dict:
        """
        Realistic content request flow with actual satellite communication:
        1. User sends request to satellite
        2. Satellite receives and processes request
        3. Check satellite cache (LRU algorithm)
        4. If HIT: Deliver from satellite cache
        5. If MISS: Fetch from ground station → Upload to satellite → Deliver
        """
        self.total_requests += 1
        request_start_time = self.env.now
        current_time = request_start_time
        
        steps = []
        
        # Step 1: User sends request to satellite
        steps.append({
            'time': current_time,
            'action': 'user_request',
            'message': f'User {user_id} sends request for: {content_id}',
            'latency_ms': 0,
            'location': 'User Device'
        })
        current_time += 0.001  # Request transmission time
        
        # Step 2: Satellite receives request
        steps.append({
            'time': current_time,
            'action': 'satellite_receive',
            'message': f'Satellite {self.satellite_id} receives request',
            'latency_ms': 15,
            'location': f'Satellite {self.satellite_id}'
        })
        current_time += 0.015  # Satellite processing latency
        
        # Step 3: Check satellite cache using LRU algorithm
        steps.append({
            'time': current_time,
            'action': 'cache_check',
            'message': 'Checking satellite cache (LRU algorithm)...',
            'latency_ms': 1,
            'location': f'Satellite {self.satellite_id} Cache'
        })
        current_time += 0.001
        
        cached_content = self.cache.get(content_id)
        
        if cached_content:
            # Cache HIT - deliver from satellite (FAST PATH)
            steps.append({
                'time': current_time,
                'action': 'cache_hit',
                'message': f'✓ CACHE HIT! Content found in satellite cache',
                'latency_ms': 1,
                'location': f'Satellite {self.satellite_id} Cache',
                'cache_info': {
                    'cached_items': len(self.cache.cache),
                    'hit_rate': self.cache.get_stats()['hit_rate']
                }
            })
            current_time += 0.001
            
            # Calculate delivery time from satellite
            delivery_time = self.network_metrics.calculate_delivery_time(
                cached_content.size_mb, from_satellite=True
            )
            
            # Step 4: Deliver from satellite to user
            steps.append({
                'time': current_time,
                'action': 'satellite_delivery',
                'message': f'Delivering {cached_content.size_mb} MB from satellite to user...',
                'latency_ms': delivery_time * 1000,
                'bandwidth_mbps': self.network_metrics.satellite_bandwidth_mbps,
                'location': f'Satellite {self.satellite_id} → User'
            })
            current_time += delivery_time
            
            steps.append({
                'time': current_time,
                'action': 'delivery_complete',
                'message': f'✓ Content successfully delivered to user!',
                'latency_ms': 0,
                'location': 'User Device',
                'total_time': current_time - request_start_time
            })
            
            log_entry = {
                'timestamp': request_start_time,
                'user_id': user_id,
                'content_id': content_id,
                'content': cached_content,
                'status': 'HIT',
                'source': 'Satellite Cache',
                'delivery_time': delivery_time,
                'total_time': current_time - request_start_time,
                'latency_satellite_ms': 15,
                'latency_ground_ms': 0,
                'steps': steps,
                'performance': {
                    'cache_hit': True,
                    'delivery_source': 'satellite',
                    'speed_advantage': '10x faster than ground station'
                }
            }
            
        else:
            # Cache MISS - fetch from ground station (SLOW PATH)
            steps.append({
                'time': current_time,
                'action': 'cache_miss',
                'message': f'✗ CACHE MISS - Content not in satellite cache',
                'latency_ms': 1,
                'location': f'Satellite {self.satellite_id} Cache'
            })
            current_time += 0.001
            
            content = get_content_by_id(content_id)
            if not content:
                # Content doesn't exist
                steps.append({
                    'time': current_time,
                    'action': 'error',
                    'message': f'✗ ERROR: Content {content_id} not found in catalog',
                    'latency_ms': 0,
                    'location': 'Ground Station'
                })
                
                log_entry = {
                    'timestamp': request_start_time,
                    'user_id': user_id,
                    'content_id': content_id,
                    'content': None,
                    'status': 'ERROR',
                    'source': 'None',
                    'delivery_time': 0,
                    'error': f'Content {content_id} not found in catalog',
                    'steps': steps
                }
            else:
                # Step 4: Request from ground station
                steps.append({
                    'time': current_time,
                    'action': 'ground_request',
                    'message': f'Requesting {content.size_mb} MB from ground station...',
                    'latency_ms': self.network_metrics.ground_latency_ms,
                    'location': f'Satellite {self.satellite_id} → Ground Station'
                })
                current_time += self.network_metrics.ground_latency_ms / 1000.0
                
                # Step 5: Fetch from ground station
                ground_fetch_time = self.network_metrics.calculate_delivery_time(
                    content.size_mb, from_satellite=False
                )
                steps.append({
                    'time': current_time,
                    'action': 'ground_fetch',
                    'message': f'Fetching {content.size_mb} MB from ground station...',
                    'latency_ms': ground_fetch_time * 1000,
                    'bandwidth_mbps': self.network_metrics.ground_bandwidth_mbps,
                    'location': 'Ground Station',
                    'transfer_details': {
                        'size_mb': content.size_mb,
                        'bandwidth_mbps': self.network_metrics.ground_bandwidth_mbps,
                        'time_seconds': ground_fetch_time
                    }
                })
                current_time += ground_fetch_time
                
                # Step 6: Upload to satellite cache
                upload_time = self.network_metrics.calculate_delivery_time(
                    content.size_mb, from_satellite=False
                )
                steps.append({
                    'time': current_time,
                    'action': 'satellite_upload',
                    'message': f'Uploading {content.size_mb} MB to satellite cache...',
                    'latency_ms': upload_time * 1000,
                    'bandwidth_mbps': self.network_metrics.ground_bandwidth_mbps,
                    'location': 'Ground Station → Satellite Cache'
                })
                current_time += upload_time
                
                # Cache the content (with LRU eviction if needed)
                cache_before = len(self.cache.cache)
                self.cache.put(content_id, content)
                cache_after = len(self.cache.cache)
                evicted = cache_before == cache_after and cache_before == self.cache.capacity
                
                steps.append({
                    'time': current_time,
                    'action': 'cache_update',
                    'message': f'✓ Content cached in satellite (LRU algorithm)',
                    'latency_ms': 1,
                    'location': f'Satellite {self.satellite_id} Cache',
                    'cache_info': {
                        'cached_items': len(self.cache.cache),
                        'evicted': evicted,
                        'hit_rate': self.cache.get_stats()['hit_rate']
                    }
                })
                current_time += 0.001
                
                # Step 7: Deliver to user from satellite
                delivery_time = self.network_metrics.calculate_delivery_time(
                    content.size_mb, from_satellite=True
                )
                steps.append({
                    'time': current_time,
                    'action': 'satellite_delivery',
                    'message': f'Delivering {content.size_mb} MB from satellite to user...',
                    'latency_ms': delivery_time * 1000,
                    'bandwidth_mbps': self.network_metrics.satellite_bandwidth_mbps,
                    'location': f'Satellite {self.satellite_id} → User'
                })
                current_time += delivery_time
                
                total_time = current_time - request_start_time
                self.total_content_delivered_mb += content.size_mb
                
                steps.append({
                    'time': current_time,
                    'action': 'delivery_complete',
                    'message': f'✓ Content successfully delivered to user!',
                    'latency_ms': 0,
                    'location': 'User Device',
                    'total_time': total_time,
                    'comparison': {
                        'satellite_only_time': delivery_time,
                        'ground_fetch_time': ground_fetch_time + upload_time,
                        'time_saved_if_cached': (ground_fetch_time + upload_time) - delivery_time
                    }
                })
                
                log_entry = {
                    'timestamp': request_start_time,
                    'user_id': user_id,
                    'content_id': content_id,
                    'content': content,
                    'status': 'MISS',
                    'source': 'Ground Station → Satellite → User',
                    'delivery_time': total_time,
                    'ground_fetch_time': ground_fetch_time,
                    'upload_time': upload_time,
                    'satellite_delivery_time': delivery_time,
                    'total_time': total_time,
                    'latency_satellite_ms': 15,
                    'latency_ground_ms': self.network_metrics.ground_latency_ms,
                    'steps': steps,
                    'performance': {
                        'cache_hit': False,
                        'delivery_source': 'ground_station',
                        'next_request_will_be_faster': True,
                        'speed_comparison': {
                            'from_satellite': f'{delivery_time:.3f}s',
                            'from_ground': f'{ground_fetch_time + upload_time:.3f}s',
                            'advantage': f'{((ground_fetch_time + upload_time) / delivery_time):.1f}x faster from cache'
                        }
                    }
                }
        
        self.request_log.append(log_entry)
        return log_entry
    
    def get_statistics(self) -> Dict:
        """Get comprehensive satellite statistics"""
        cache_stats = self.cache.get_stats()
        return {
            'satellite_id': self.satellite_id,
            'total_requests': self.total_requests,
            'cache_hits': cache_stats['hits'],
            'cache_misses': cache_stats['misses'],
            'cache_hit_rate': cache_stats['hit_rate'],
            'cache_evictions': cache_stats['evictions'],
            'cache_utilization': cache_stats['utilization'],
            'total_content_delivered_mb': self.total_content_delivered_mb,
            'connected': self.connected,
            'signal_strength': self.signal_strength,
            'altitude_km': self.altitude_km
        }

class NTNSimulation:
    """Main NTN simulation controller"""
    
    def __init__(self, cache_size: int = 12):
        self.env = simpy.Environment()
        self.satellite = SatelliteNode(self.env, "LEO-1", cache_size)
        self.content_catalog = REALISTIC_CONTENT_CATALOG
    
    def simulate_request(self, content_id: str, user_id: str) -> Dict:
        """Simulate a single content request"""
        result = self.satellite.request_content(content_id, user_id)
        # Advance simulation time
        if result['delivery_time'] > 0:
            self.env.run(until=self.env.now + result['delivery_time'])
        return result
    
    def get_available_content(self) -> List[Dict]:
        """Get list of available content"""
        return [
            {
                'content_id': item.content_id,
                'title': item.title,
                'type': item.content_type,
                'size_mb': item.size_mb,
                'description': item.description,
                'category': item.category
            }
            for item in self.content_catalog
        ]
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics"""
        return self.satellite.get_statistics()

