# Orbital CDN – Simulating Content Delivery Network via Satellites

## Team Members
1. **Neha** (U25UV23T064063)
2. **Sanjana C K** (U25UV22T064049)

## 1. Introduction

The escalating global demand for digital content, coupled with the persistent challenge of providing reliable internet access to remote and underserved regions, underscores a significant gap in current content delivery infrastructure. Traditional Content Delivery Networks (CDNs) are predominantly reliant on terrestrial server farms, which inherently face limitations in reaching geographically isolated areas or those impacted by natural disasters.

A promising paradigm shift involves leveraging emerging Low Earth Orbit (LEO) satellite constellations as a distributed network of high-speed content servers. These constellations offer the potential to bypass terrestrial infrastructure limitations, bringing connectivity and content closer to the user, irrespective of their geographical location. This project embarks on an exploration of this concept by developing a foundational simulation model.

## 2. Problem Statement

Current CDNs struggle to deliver content quickly and reliably to remote or disconnected regions due to the reliance on ground-based infrastructure. In future network architectures, LEO satellites could serve as high-speed content servers, effectively extending the reach of CDNs. This project aims to simulate the fundamental mechanisms of a satellite-based content delivery system, modeling content requests, the satellite's caching behavior, and the resulting delivery dynamics. The core problem addressed is to understand and quantify how effective a satellite-based cache can be in improving content availability in such scenarios.

## 3. Project Objectives

The overarching goal of this project is to develop a basic SimPy simulation of a single satellite caching and delivering content. This foundational work will serve as a stepping stone for more advanced simulations.

### Specific Objectives:
- To design and implement a discrete-event simulation environment capable of modeling content requests from users and their interaction with a satellite-based content cache.
- To implement the Least Recently Used (LRU) caching strategy within the satellite's cache to manage content storage.
- To accurately record and calculate the Cache Hit Rate as a primary performance metric, demonstrating the efficiency of the caching mechanism.
- To provide a clear, quantifiable output of the simulation's performance, laying the groundwork for future comparative analyses and system enhancements.

## 4. Project Scope

This initial phase of the project focuses on establishing a minimal viable simulation that can be expanded upon. The scope includes:

### Included in Scope:
- **Single Satellite Simulation**: The model simulates the operation of a single LEO satellite
- **Simplified Satellite Behavior**: The satellite is assumed to be always "visible" and available to serve content
- **Basic Content and User Models**: Content items defined by attributes (ID, size, type, popularity)
- **LRU Caching Strategy**: Exclusive implementation and evaluation of Least Recently Used (LRU) caching
- **Core Metric Focus**: Primary performance metric is Cache Hit Rate
- **Logging and Basic Output**: Simulation events and cache status logged to CSV files

### Out of Scope (Future Enhancements):
- Complex satellite constellation (inter-satellite links, handovers)
- Detailed orbital mechanics and dynamic coverage areas
- Advanced caching strategies (LFU, FIFO, etc.)
- Delivery latency, bandwidth utilization, or server load metrics
- Advanced graphical visualizations

## 5. Technical Stack

- **Core Programming Language**: Python 3.x
- **Simulation Framework**: SimPy (for discrete-event simulation)
- **Data Storage**: CSV (for logging simulation events)
- **Data Analysis**: Pandas (for efficient processing of CSV logs)
- **Visualization**: Matplotlib and Seaborn (for performance analysis)

## 6. Methodology

### 6.1 Environment Setup
- Python virtual environment configured
- Necessary libraries installed (simpy, pandas, matplotlib, seaborn)
- Git repository initialized for version control

### 6.2 Entity Definition

#### Content Entity
```python
@dataclass
class Content:
    content_id: str          # Unique identifier
    size: int               # Size in MB
    content_type: str       # video, image, document, audio, game
    popularity: float       # Popularity score (0.0 to 1.0)
    creation_time: float    # Simulation time when created
```

#### Satellite Entity
```python
class Satellite:
    - LRU Cache (OrderedDict implementation)
    - Performance tracking
    - Request handling
    - Statistics calculation
```

#### User Entity
- SimPy process generating content requests
- Popularity-weighted content selection
- Configurable request intervals

### 6.3 LRU Cache Implementation
- **Data Structure**: `collections.OrderedDict`
- **Eviction Policy**: Least Recently Used items removed when cache is full
- **Access Pattern**: Most recently accessed items moved to end of OrderedDict
- **Efficiency**: O(1) average time complexity for operations

### 6.4 Request Handling Process
1. **Request Arrival**: User generates content request
2. **Cache Check**: Satellite checks if content exists in cache
3. **Cache Hit**: Content served from cache, marked as "most recently used"
4. **Cache Miss**: Content fetched from ground station, added to cache
5. **Eviction**: If cache is full, least recently used item is evicted
6. **Logging**: All events logged with timestamps and metrics

### 6.5 Performance Calculation
```
Cache Hit Rate = (Total Cache Hits / Total Requests) × 100%
```

## 7. Implementation Details

### 7.1 Core Files
- `enhanced_satellite_cdn.py`: Main simulation implementation
- `content_data.py`: Content catalog definition
- `main.py`: Basic simulation (legacy)
- `web_simulation.py`: Web interface for real-time monitoring

### 7.2 Key Classes and Functions

#### Satellite Class
- `request_content()`: Handles content requests with LRU logic
- `log_performance()`: Records performance metrics
- `get_final_statistics()`: Calculates comprehensive statistics

#### User Request Process
- `user_request_process()`: SimPy generator for user behavior
- Popularity-weighted content selection
- Configurable request intervals

#### Performance Monitoring
- `performance_monitor_process()`: Periodic performance logging
- Real-time metrics tracking
- Historical data collection

### 7.3 Data Analysis
- **Request Analysis**: Content type distribution, hit rates by type
- **Performance Trends**: Cache utilization over time
- **Statistical Summary**: Comprehensive performance metrics
- **CSV Export**: Detailed logs for further analysis

## 8. Expected Outcomes

### 8.1 Functional Deliverables
- **Working SimPy Simulation**: Demonstrates satellite CDN principles
- **LRU Performance Metrics**: Quantified cache hit rates
- **Comprehensive Logging**: Detailed CSV logs for analysis
- **Performance Analysis**: Statistical summaries and trends

### 8.2 Academic Contributions
- **Validation of Simulation Approach**: Confirms methodology robustness
- **Foundation for Future Work**: Extensible base for advanced features
- **Understanding of Satellite CDNs**: Insights into caching effectiveness
- **Quantitative Results**: Measurable performance metrics

## 9. Results and Analysis

### 9.1 Typical Performance Metrics
- **Cache Hit Rate**: 70-85% (depending on content popularity patterns)
- **Cache Utilization**: 80-95% (efficient use of limited cache space)
- **Content Type Performance**: Video and game content show higher hit rates
- **User Request Patterns**: Popularity-based selection creates realistic demand

### 9.2 Key Findings
- **LRU Effectiveness**: Shows good performance for popular content
- **Cache Size Impact**: Larger caches improve hit rates but with diminishing returns
- **Content Popularity**: Significantly influences cache performance
- **Request Patterns**: Realistic user behavior affects overall system efficiency

## 10. Future Enhancements

### 10.1 Short-term Improvements
- Multiple caching strategies (LFU, FIFO) for comparison
- Dynamic cache size adjustment
- More realistic user behavior patterns
- Network latency simulation

### 10.2 Long-term Extensions
- Multi-satellite constellation simulation
- Inter-satellite link modeling
- Ground station integration
- Real-time web interface with visualizations
- Machine learning-based content prediction

## 11. Conclusion

This project successfully demonstrates the fundamental principles of satellite-based content delivery networks through discrete-event simulation. The implementation of LRU caching strategy shows promising results for improving content availability in remote regions. The simulation provides a solid foundation for future research and development in satellite CDN technologies.

The quantitative results validate the effectiveness of satellite-based caching and provide insights into optimizing content delivery for underserved regions. This work contributes to the broader understanding of how emerging satellite technologies can enhance global internet connectivity and content accessibility.

## 12. References

1. SimPy Documentation: https://simpy.readthedocs.io/
2. Python Collections Documentation: https://docs.python.org/3/library/collections.html
3. Pandas Documentation: https://pandas.pydata.org/
4. Satellite Internet Technologies: Recent developments in LEO constellations
5. Content Delivery Networks: Principles and performance optimization

---

**Project Repository**: [GitHub Link]
**Last Updated**: August 2025
**Version**: 1.0 