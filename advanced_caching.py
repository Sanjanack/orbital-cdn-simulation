"""
Advanced Caching Mechanisms for Satellite CDN
==============================================

This module implements multiple caching strategies beyond LRU:
- LFU (Least Frequently Used)
- FIFO (First In First Out)
- Adaptive Caching (switches between strategies based on performance)

Team Members:
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Dict, Optional, Any
from datetime import datetime
import time

@dataclass
class CacheItem:
    """Cache item with metadata"""
    content_id: str
    content: Any
    access_count: int = 0
    last_access_time: float = 0.0
    insert_time: float = 0.0

class LRUCache:
    """Least Recently Used Cache Implementation"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, content_id: str) -> Optional[Any]:
        """Get content from cache"""
        if content_id in self.cache:
            # Move to end (most recently used)
            item = self.cache[content_id]
            item.last_access_time = time.time()
            self.cache.move_to_end(content_id)
            self.hits += 1
            return item.content
        self.misses += 1
        return None
    
    def put(self, content_id: str, content: Any):
        """Add content to cache"""
        current_time = time.time()
        
        if content_id in self.cache:
            # Update existing
            item = self.cache[content_id]
            item.last_access_time = current_time
            self.cache.move_to_end(content_id)
        else:
            # Check if cache is full
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
                self.evictions += 1
            
            # Add new content
            item = CacheItem(
                content_id=content_id,
                content=content,
                last_access_time=current_time,
                insert_time=current_time
            )
            self.cache[content_id] = item
    
    def contains(self, content_id: str) -> bool:
        """Check if content is in cache"""
        return content_id in self.cache
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'strategy': 'LRU',
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'size': len(self.cache),
            'capacity': self.capacity,
            'utilization': len(self.cache) / self.capacity * 100 if self.capacity > 0 else 0
        }

class LFUCache:
    """Least Frequently Used Cache Implementation"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[str, CacheItem] = {}
        self.frequency_map: Dict[int, OrderedDict[str, CacheItem]] = defaultdict(OrderedDict)
        self.min_frequency = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, content_id: str) -> Optional[Any]:
        """Get content from cache"""
        if content_id not in self.cache:
            self.misses += 1
            return None
        
        item = self.cache[content_id]
        old_freq = item.access_count
        
        # Update frequency
        item.access_count += 1
        item.last_access_time = time.time()
        
        # Remove from old frequency bucket
        if old_freq in self.frequency_map:
            if content_id in self.frequency_map[old_freq]:
                del self.frequency_map[old_freq][content_id]
                if not self.frequency_map[old_freq] and old_freq == self.min_frequency:
                    self.min_frequency += 1
        
        # Add to new frequency bucket
        new_freq = item.access_count
        self.frequency_map[new_freq][content_id] = item
        
        self.hits += 1
        return item.content
    
    def put(self, content_id: str, content: Any):
        """Add content to cache"""
        current_time = time.time()
        
        if content_id in self.cache:
            # Update existing
            self.get(content_id)  # This updates frequency
            self.cache[content_id].content = content
        else:
            # Check if cache is full
            if len(self.cache) >= self.capacity:
                # Remove least frequently used
                while self.min_frequency not in self.frequency_map or not self.frequency_map[self.min_frequency]:
                    self.min_frequency += 1
                
                # Remove LRU from min frequency bucket
                lfu_item_id, _ = self.frequency_map[self.min_frequency].popitem(last=False)
                del self.cache[lfu_item_id]
                self.evictions += 1
            
            # Add new content
            item = CacheItem(
                content_id=content_id,
                content=content,
                access_count=1,
                last_access_time=current_time,
                insert_time=current_time
            )
            self.cache[content_id] = item
            self.frequency_map[1][content_id] = item
            self.min_frequency = 1
    
    def contains(self, content_id: str) -> bool:
        """Check if content is in cache"""
        return content_id in self.cache
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'strategy': 'LFU',
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'size': len(self.cache),
            'capacity': self.capacity,
            'utilization': len(self.cache) / self.capacity * 100 if self.capacity > 0 else 0
        }

class FIFOCache:
    """First In First Out Cache Implementation"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, content_id: str) -> Optional[Any]:
        """Get content from cache"""
        if content_id in self.cache:
            item = self.cache[content_id]
            item.last_access_time = time.time()
            item.access_count += 1
            # Don't move items in FIFO - order is based on insertion
            self.hits += 1
            return item.content
        self.misses += 1
        return None
    
    def put(self, content_id: str, content: Any):
        """Add content to cache"""
        current_time = time.time()
        
        if content_id not in self.cache:
            # Check if cache is full
            if len(self.cache) >= self.capacity:
                # Remove first item (oldest)
                self.cache.popitem(last=False)
                self.evictions += 1
            
            # Add new content at the end
            item = CacheItem(
                content_id=content_id,
                content=content,
                last_access_time=current_time,
                insert_time=current_time
            )
            self.cache[content_id] = item
        else:
            # Update existing content
            self.cache[content_id].content = content
            self.cache[content_id].last_access_time = current_time
    
    def contains(self, content_id: str) -> bool:
        """Check if content is in cache"""
        return content_id in self.cache
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'strategy': 'FIFO',
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'size': len(self.cache),
            'capacity': self.capacity,
            'utilization': len(self.cache) / self.capacity * 100 if self.capacity > 0 else 0
        }

class AdaptiveCache:
    """Adaptive Cache that switches between strategies based on performance"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.lru_cache = LRUCache(capacity)
        self.lfu_cache = LFUCache(capacity)
        self.fifo_cache = FIFOCache(capacity)
        
        # Current strategy
        self.current_strategy = 'LRU'
        self.strategy_history = []
        self.evaluation_window = 100  # Evaluate every 100 requests
        self.request_count = 0
        
        # Strategy performance tracking
        self.strategy_performance = {
            'LRU': {'hits': 0, 'misses': 0},
            'LFU': {'hits': 0, 'misses': 0},
            'FIFO': {'hits': 0, 'misses': 0}
        }
    
    def get(self, content_id: str) -> Optional[Any]:
        """Get content from cache using current strategy"""
        self.request_count += 1
        
        if self.current_strategy == 'LRU':
            result = self.lru_cache.get(content_id)
            if result:
                self.strategy_performance['LRU']['hits'] += 1
            else:
                self.strategy_performance['LRU']['misses'] += 1
        elif self.current_strategy == 'LFU':
            result = self.lfu_cache.get(content_id)
            if result:
                self.strategy_performance['LFU']['hits'] += 1
            else:
                self.strategy_performance['LFU']['misses'] += 1
        else:  # FIFO
            result = self.fifo_cache.get(content_id)
            if result:
                self.strategy_performance['FIFO']['hits'] += 1
            else:
                self.strategy_performance['FIFO']['misses'] += 1
        
        # Evaluate and potentially switch strategy
        if self.request_count % self.evaluation_window == 0:
            self._evaluate_and_switch()
        
        return result
    
    def put(self, content_id: str, content: Any):
        """Add content to cache using current strategy"""
        if self.current_strategy == 'LRU':
            self.lru_cache.put(content_id, content)
        elif self.current_strategy == 'LFU':
            self.lfu_cache.put(content_id, content)
        else:  # FIFO
            self.fifo_cache.put(content_id, content)
    
    def contains(self, content_id: str) -> bool:
        """Check if content is in cache"""
        if self.current_strategy == 'LRU':
            return self.lru_cache.contains(content_id)
        elif self.current_strategy == 'LFU':
            return self.lfu_cache.contains(content_id)
        else:
            return self.fifo_cache.contains(content_id)
    
    def _evaluate_and_switch(self):
        """Evaluate performance and switch to best strategy"""
        best_strategy = self.current_strategy
        best_hit_rate = 0.0
        
        for strategy in ['LRU', 'LFU', 'FIFO']:
            perf = self.strategy_performance[strategy]
            total = perf['hits'] + perf['misses']
            if total > 0:
                hit_rate = (perf['hits'] / total) * 100
                if hit_rate > best_hit_rate:
                    best_hit_rate = hit_rate
                    best_strategy = strategy
        
        if best_strategy != self.current_strategy:
            self.strategy_history.append({
                'from': self.current_strategy,
                'to': best_strategy,
                'hit_rate': best_hit_rate,
                'request_count': self.request_count
            })
            self.current_strategy = best_strategy
            # Reset performance tracking
            for strategy in self.strategy_performance:
                self.strategy_performance[strategy] = {'hits': 0, 'misses': 0}
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if self.current_strategy == 'LRU':
            stats = self.lru_cache.get_stats()
        elif self.current_strategy == 'LFU':
            stats = self.lfu_cache.get_stats()
        else:
            stats = self.fifo_cache.get_stats()
        
        stats['adaptive'] = True
        stats['current_strategy'] = self.current_strategy
        stats['strategy_history'] = self.strategy_history[-5:]  # Last 5 switches
        stats['strategy_performance'] = {
            k: {
                'hits': v['hits'],
                'misses': v['misses'],
                'hit_rate': (v['hits'] / (v['hits'] + v['misses']) * 100) if (v['hits'] + v['misses']) > 0 else 0
            }
            for k, v in self.strategy_performance.items()
        }
        
        return stats
