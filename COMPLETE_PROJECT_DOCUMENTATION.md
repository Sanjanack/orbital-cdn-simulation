# 🛰️ Orbital CDN Simulation - Complete Project Documentation

## Team Members
1. **Neha** (U25UV23T064063) - Lead Developer & Simulation Engineer
2. **Sanjana C K** (U25UV22T064049) - System Architect & UI/UX Designer

---

## 1. Introduction

### 1.1 Background
The global demand for digital content delivery has grown exponentially, with traditional Content Delivery Networks (CDNs) relying primarily on terrestrial infrastructure. However, terrestrial CDNs face significant challenges in reaching remote, underserved, and disaster-affected regions. The emergence of Low Earth Orbit (LEO) satellite constellations presents a revolutionary opportunity to extend CDN capabilities beyond terrestrial limitations.

### 1.2 Problem Statement
Current CDN architectures struggle with:
- **Geographic Limitations**: Inability to reach remote and isolated regions
- **Infrastructure Dependency**: Heavy reliance on ground-based servers and fiber networks
- **Disaster Resilience**: Vulnerability to natural disasters and infrastructure failures
- **Latency Issues**: High latency for users far from data centers
- **Scalability Constraints**: Limited ability to scale in remote areas

### 1.3 Solution Overview
This project simulates a **Satellite-Based Content Delivery Network** using LEO satellites as distributed caching nodes. The system implements intelligent caching strategies, multi-satellite constellations, and real-time collaboration features to demonstrate how satellite networks can revolutionize content delivery.

---

## 2. Project Aim

To design, develop, and demonstrate a comprehensive simulation platform that models a **Non-Terrestrial Network (NTN) based Content Delivery Network** using Low Earth Orbit satellites, showcasing:

1. **Realistic Content Delivery**: Simulate real-world content types and delivery scenarios
2. **Intelligent Caching**: Implement and compare multiple caching strategies
3. **Multi-Satellite Coordination**: Demonstrate inter-satellite communication and load balancing
4. **Real-time Collaboration**: Enable multi-user collaborative simulation sessions
5. **Performance Analysis**: Provide comprehensive analytics and visualization tools

---

## 3. Objectives

### 3.1 Primary Objectives
1. **Simulate Satellite CDN Architecture**
   - Model LEO satellite behavior and orbital mechanics
   - Implement realistic network latency and bandwidth calculations
   - Simulate content delivery from satellite cache vs. ground stations

2. **Implement Advanced Caching Mechanisms**
   - **LRU (Least Recently Used)**: Evict least recently accessed content
   - **LFU (Least Frequently Used)**: Evict least frequently accessed content
   - **FIFO (First In First Out)**: Evict oldest content first
   - **Adaptive Caching**: Automatically switch strategies based on performance

3. **Multi-Satellite Constellation Support**
   - Manage multiple satellites in a constellation
   - Implement inter-satellite communication
   - Load balancing across satellites
   - Geographic distribution and nearest satellite selection

4. **Real-time Collaboration**
   - WebSocket-based real-time communication
   - Multi-user simulation sessions
   - Live cache state updates
   - Collaborative performance monitoring

5. **Comprehensive Analytics**
   - Real-time performance metrics
   - Cache hit/miss rate analysis
   - Content distribution visualization
   - Network performance monitoring

### 3.2 Secondary Objectives
1. **User Management System**: Secure authentication and role-based access
2. **Web-based Interface**: Modern, responsive dashboard
3. **Data Persistence**: Database storage for sessions and analytics
4. **Export Capabilities**: CSV export for further analysis
5. **Documentation**: Complete technical and user documentation

---

## 4. Technical Stack

### 4.1 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Flask** | 3.1.1 | Web framework |
| **Flask-SQLAlchemy** | 3.1.1 | ORM for database operations |
| **Flask-Login** | 0.6.3 | User authentication |
| **Flask-SocketIO** | 5.3.6 | WebSocket support for real-time features |
| **SimPy** | 4.1.1 | Discrete-event simulation framework |
| **SQLite** | - | Database for data persistence |
| **Werkzeug** | 3.1.3 | Security utilities (password hashing) |

### 4.2 Frontend Technologies

| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure and semantic markup |
| **CSS3** | Styling and animations |
| **JavaScript** | Client-side interactivity |
| **Bootstrap 5** | Responsive UI framework |
| **Chart.js** | Data visualization |
| **Font Awesome** | Icon library |
| **Socket.IO Client** | WebSocket client for real-time updates |

### 4.3 Data Analysis & Visualization

| Technology | Version | Purpose |
|------------|---------|---------|
| **Pandas** | 2.3.1 | Data manipulation and analysis |
| **NumPy** | 2.3.1 | Numerical computations |
| **Matplotlib** | 3.10.5 | Static chart generation |
| **Seaborn** | 0.13.2 | Statistical data visualization |

### 4.4 Development Tools

| Technology | Purpose |
|------------|---------|
| **Git** | Version control |
| **Virtual Environment** | Dependency isolation |
| **Pytest** | Testing framework |

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Application Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   User UI    │  │  Admin UI    │  │  Real-time   │      │
│  │  Dashboard   │  │  Dashboard   │  │ Collaboration│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Flask      │  │  SocketIO    │  │  REST APIs   │      │
│  │   Framework  │  │  WebSocket   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Simulation Engine                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SimPy      │  │  Satellite   │  │  Caching     │      │
│  │  Environment │  │ Constellation│  │  Strategies  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite      │  │  Content     │  │  Analytics   │      │
│  │   Database    │  │  Catalog     │  │  Storage     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Component Architecture

#### 5.2.1 Satellite Constellation Module
- **ConstellationSatellite**: Enhanced satellite with inter-satellite communication
- **SatelliteConstellation**: Manages multiple satellites
- **SatellitePosition**: 3D position tracking (latitude, longitude, altitude)
- **Inter-satellite Communication**: Content sharing between satellites

#### 5.2.2 Caching Module
- **LRUCache**: Least Recently Used implementation
- **LFUCache**: Least Frequently Used implementation
- **FIFOCache**: First In First Out implementation
- **AdaptiveCache**: Strategy switching based on performance

#### 5.2.3 Real-time Collaboration Module
- **CollaborationManager**: Manages multi-user sessions
- **WebSocket Handlers**: Real-time event handling
- **Session Management**: User session tracking
- **State Synchronization**: Cache state broadcasting

#### 5.2.4 Network Simulation Module
- **NTNSimulation**: Main simulation controller
- **SatelliteNode**: Individual satellite node
- **NetworkMetrics**: Latency and bandwidth calculations
- **Content Delivery Flow**: Step-by-step delivery tracking

---

## 6. Solution Implementation

### 6.1 Content Delivery Flow

```
User Request
    │
    ▼
┌─────────────────┐
│ Check Local      │
│ Satellite Cache  │
└─────────────────┘
    │
    ├─── Cache HIT ────► Deliver from Satellite (Fast: ~0.15s)
    │
    └─── Cache MISS ────► Check Neighboring Satellites
                            │
                            ├─── Neighbor HIT ────► Inter-satellite Transfer → Deliver
                            │
                            └─── Neighbor MISS ────► Fetch from Ground Station
                                                      │
                                                      ├─── Upload to Satellite Cache
                                                      │
                                                      └─── Deliver to User (Slow: ~1.5s+)
```

### 6.2 Caching Strategy Selection

The system supports four caching strategies:

1. **LRU (Least Recently Used)**
   - Evicts content that hasn't been accessed recently
   - Best for: Temporal locality patterns
   - Implementation: OrderedDict with move-to-end on access

2. **LFU (Least Frequently Used)**
   - Evicts content with lowest access frequency
   - Best for: Popular content patterns
   - Implementation: Frequency buckets with OrderedDict

3. **FIFO (First In First Out)**
   - Evicts oldest content first
   - Best for: Simple, predictable patterns
   - Implementation: OrderedDict maintaining insertion order

4. **Adaptive Caching**
   - Monitors performance of all strategies
   - Automatically switches to best-performing strategy
   - Evaluation window: Every 100 requests
   - Best for: Dynamic, unpredictable access patterns

### 6.3 Multi-Satellite Coordination

1. **Satellite Distribution**
   - Satellites distributed in orbital plane
   - Geographic coverage optimization
   - Altitude: 500-600 km (LEO)

2. **Inter-Satellite Communication**
   - Nearest satellite discovery
   - Content sharing between satellites
   - Load balancing across constellation

3. **User Assignment**
   - Round-robin or geographic assignment
   - Nearest satellite selection
   - Dynamic handover support

### 6.4 Real-time Collaboration

1. **Session Management**
   - Create/join collaboration sessions
   - Multi-user participation
   - Session state synchronization

2. **Real-time Updates**
   - WebSocket-based communication
   - Live cache state updates
   - Performance metrics broadcasting
   - Request history sharing

3. **Collaborative Features**
   - Shared simulation sessions
   - Real-time chat (via messaging system)
   - Content sharing between users
   - Collaborative analytics

---

## 7. Key Features

### 7.1 Core Features

1. **Realistic Content Catalog**
   - 15+ real-world content items
   - Multiple content types (Video, Image, Document, Audio, Application)
   - Categories (News, Education, Sports, Weather, Emergency)
   - Rich metadata (size, popularity, description)

2. **NTN Network Simulation**
   - Realistic latency calculations (15ms satellite, 150ms ground)
   - Bandwidth-aware delivery (100 Mbps satellite, 1000 Mbps ground)
   - Step-by-step delivery visualization
   - Performance metrics tracking

3. **Advanced Caching**
   - Multiple caching strategies
   - Strategy comparison and analysis
   - Adaptive strategy selection
   - Cache performance metrics

4. **Multi-Satellite Support**
   - Constellation management
   - Inter-satellite communication
   - Load balancing
   - Geographic distribution

5. **Real-time Collaboration**
   - WebSocket-based real-time updates
   - Multi-user sessions
   - Live state synchronization
   - Collaborative analytics

### 7.2 User Interface Features

1. **User Dashboard**
   - Content request interface
   - Real-time simulation controls
   - Performance visualization
   - Session history

2. **Admin Dashboard**
   - System overview
   - User management
   - Analytics and reporting
   - System configuration

3. **Real-time Visualization**
   - Live cache status
   - Performance charts
   - Network topology
   - Satellite constellation view

### 7.3 Analytics & Reporting

1. **Performance Metrics**
   - Cache hit/miss rates
   - Cache utilization
   - Delivery times
   - Network performance

2. **Visualizations**
   - Hit rate over time
   - Cache utilization trends
   - Content type distribution
   - Request status comparison

3. **Data Export**
   - CSV export for analysis
   - Session logs
   - Performance data

---

## 8. Technologies & Algorithms

### 8.1 Simulation Technologies

1. **SimPy (Discrete-Event Simulation)**
   - Event-driven simulation framework
   - Process-based modeling
   - Time management
   - Resource management

2. **Network Modeling**
   - Latency calculations
   - Bandwidth modeling
   - Packet loss simulation
   - Network topology

### 8.2 Caching Algorithms

1. **LRU Algorithm**
   - Time complexity: O(1) for get/put
   - Space complexity: O(n)
   - Data structure: OrderedDict

2. **LFU Algorithm**
   - Time complexity: O(1) average case
   - Space complexity: O(n)
   - Data structure: Dictionary + Frequency buckets

3. **FIFO Algorithm**
   - Time complexity: O(1)
   - Space complexity: O(n)
   - Data structure: OrderedDict

4. **Adaptive Algorithm**
   - Performance monitoring
   - Strategy evaluation
   - Dynamic switching
   - Evaluation window: 100 requests

### 8.3 Real-time Communication

1. **WebSocket Protocol**
   - Full-duplex communication
   - Low latency
   - Event-driven architecture
   - Room-based messaging

2. **Socket.IO**
   - Cross-browser compatibility
   - Automatic reconnection
   - Event namespacing
   - Room management

---

## 9. Database Schema

### 9.1 Core Tables

1. **User**
   - id, username, email, password_hash, role, created_at, last_login

2. **SimulationSession**
   - id, user_id, config, results, created_at, status

3. **ContentRequest**
   - id, session_id, timestamp, user_id, content_id, content_type,
     content_size, status, delivery_source, cache_utilization, hit_rate

4. **SatelliteNode**
   - id, satellite_id, name, latitude, longitude, altitude,
     cache_size, cache_utilization, hit_rate, status

5. **UserMessage**
   - id, sender_id, receiver_id, message, content_id, created_at, read

6. **SharedContent**
   - id, sharer_id, receiver_id, content_id, content_type,
     content_size, shared_at, accessed

---

## 10. API Endpoints

### 10.1 Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### 10.2 Simulation
- `POST /start_simulation` - Start simulation
- `GET /simulation_status` - Get simulation status
- `GET /simulation_results` - Get simulation results
- `POST /api/request_content` - Request content on-demand

### 10.3 Advanced Features
- `POST /api/enable_multi_satellite` - Enable multi-satellite mode
- `POST /api/set_caching_strategy` - Set caching strategy
- `GET /api/get_caching_strategies` - Get available strategies
- `POST /api/multi_satellite_request` - Multi-satellite content request

### 10.4 Collaboration
- `POST /api/create_collaboration_session` - Create collaboration session
- `POST /api/join_collaboration_session` - Join session
- `GET /api/collaboration_session/<id>` - Get session details

### 10.5 Analytics
- `GET /api/analytics` - Get analytics data
- `GET /api/satellite_status` - Get satellite status
- `GET /api/constellation_stats` - Get constellation statistics

---

## 11. Installation & Setup

### 11.1 Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### 11.2 Installation Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd orbital_cdn_simulation

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python app.py
```

### 11.3 Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **User**: Register new account or use existing

---

## 12. Usage Guide

### 12.1 Basic Usage

1. **Login/Register**
   - Access the application at `http://localhost:5000`
   - Login with credentials or register new account

2. **Request Content**
   - Navigate to User Dashboard
   - Select content from catalog
   - Click "Request Content"
   - View delivery details and performance

3. **Run Simulation**
   - Configure simulation parameters
   - Start simulation
   - View results and analytics

### 12.2 Advanced Features

1. **Multi-Satellite Mode**
   - Enable via API: `POST /api/enable_multi_satellite`
   - Specify number of satellites
   - Make requests through constellation

2. **Caching Strategy Selection**
   - Select strategy: `POST /api/set_caching_strategy`
   - Available: LRU, LFU, FIFO, Adaptive
   - Monitor performance differences

3. **Real-time Collaboration**
   - Create collaboration session
   - Invite other users
   - Share real-time updates
   - Monitor collaborative analytics

---

## 13. Performance Metrics

### 13.1 Typical Performance

- **Cache Hit Rate**: 70-85% (depending on strategy and content patterns)
- **Cache Utilization**: 80-95%
- **Delivery Time (Cache Hit)**: ~0.15 seconds
- **Delivery Time (Cache Miss)**: ~1.5+ seconds
- **Inter-satellite Hit Rate**: 10-20% (with multi-satellite)

### 13.2 Strategy Comparison

| Strategy | Best For | Hit Rate | Complexity |
|----------|----------|----------|------------|
| LRU | Temporal locality | 75-85% | Low |
| LFU | Popular content | 70-80% | Medium |
| FIFO | Simple patterns | 65-75% | Low |
| Adaptive | Dynamic patterns | 75-90% | High |

---

## 14. Future Enhancements

### 14.1 Planned Features
1. **Machine Learning Integration**
   - Predictive caching
   - Content popularity prediction
   - Anomaly detection

2. **Advanced Analytics**
   - Geographic heatmaps
   - Predictive analytics
   - Custom report generation

3. **Enhanced Visualization**
   - 3D satellite orbit visualization
   - Real-time network topology
   - Interactive charts

4. **API Enhancements**
   - RESTful API documentation
   - API rate limiting
   - Webhook support

### 14.2 Scalability Improvements
1. **Database Migration**
   - PostgreSQL support
   - Database replication
   - Query optimization

2. **Caching Layer**
   - Redis integration
   - Distributed caching
   - Cache warming

3. **Deployment**
   - Docker containerization
   - Cloud deployment
   - Load balancing

---

## 15. References

### 15.1 Academic References

1. **Satellite Networks**
   - Low Earth Orbit (LEO) Satellite Constellations
   - Non-Terrestrial Networks (NTN) in 5G/6G
   - Inter-satellite Communication Protocols

2. **Caching Strategies**
   - Least Recently Used (LRU) Algorithm
   - Least Frequently Used (LFU) Algorithm
   - Adaptive Caching Mechanisms

3. **Content Delivery Networks**
   - CDN Architecture and Design
   - Edge Computing and Caching
   - Network Performance Optimization

### 15.2 Technical Documentation

1. **SimPy Documentation**
   - https://simpy.readthedocs.io/
   - Discrete-event simulation framework

2. **Flask Documentation**
   - https://flask.palletsprojects.com/
   - Web framework documentation

3. **Socket.IO Documentation**
   - https://socket.io/docs/
   - Real-time communication library

4. **Bootstrap Documentation**
   - https://getbootstrap.com/
   - UI framework documentation

### 15.3 Standards & Specifications

1. **3GPP NTN Specifications**
   - Non-Terrestrial Network standards
   - Satellite communication protocols

2. **WebSocket Protocol**
   - RFC 6455: The WebSocket Protocol
   - Real-time communication standard

3. **HTTP/2 and HTTP/3**
   - Modern web protocols
   - Performance optimization

---

## 16. Conclusion

This project successfully demonstrates a comprehensive **Satellite-Based Content Delivery Network** simulation platform with:

- ✅ **Realistic NTN Simulation**: Accurate modeling of satellite networks
- ✅ **Advanced Caching**: Multiple strategies with adaptive selection
- ✅ **Multi-Satellite Support**: Constellation management and coordination
- ✅ **Real-time Collaboration**: WebSocket-based multi-user sessions
- ✅ **Comprehensive Analytics**: Performance monitoring and visualization

The platform provides a solid foundation for:
- Research in satellite CDN technologies
- Education in network simulation
- Demonstration of NTN capabilities
- Performance analysis and optimization

**Future work** can extend this platform with machine learning, advanced analytics, and production-ready deployment features.

---

## 17. Project Statistics

- **Total Lines of Code**: ~5000+
- **Modules**: 10+
- **API Endpoints**: 20+
- **Database Tables**: 6
- **Caching Strategies**: 4
- **Content Items**: 15+
- **Development Time**: Multiple iterations
- **Version**: 4.0 (Advanced Features)

---

**Last Updated**: January 2025  
**Project Status**: ✅ Complete with Advanced Features  
**License**: Educational/Research Use

---

*Made with ❤️ by Team Orbital CDN*
