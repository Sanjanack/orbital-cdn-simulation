# 🛰️ Orbital CDN Simulation - Advanced Satellite Content Delivery Network

A comprehensive web-based simulation platform for modeling satellite-based content delivery networks using Low Earth Orbit (LEO) satellites with intelligent caching strategies.

## 🌟 Features

### 🔐 User Authentication & Management
- **Secure Login/Registration System**: Role-based access control with encrypted passwords
- **User Dashboard**: Personalized simulation interface for regular users
- **Admin Dashboard**: Advanced administrative controls and system monitoring
- **Session Management**: Track user activity and simulation sessions

### 🚀 Advanced Simulation Engine
- **LEO Satellite Modeling**: Realistic simulation of Low Earth Orbit satellites
- **Intelligent Caching**: LRU (Least Recently Used) caching algorithms
- **Configurable Parameters**: Adjustable simulation duration, cache size, user count, etc.
- **Real-time Monitoring**: Live performance metrics and status updates
- **Background Processing**: Non-blocking simulation execution

### 📊 Comprehensive Analytics
- **Real-time Charts**: Cache hit rates, utilization, content distribution
- **Performance Metrics**: Request statistics, cache efficiency, delivery sources
- **Data Export**: CSV export functionality for further analysis
- **Historical Data**: Session history and performance tracking

### 🎨 Modern User Interface
- **Responsive Design**: Mobile-friendly interface across all devices
- **Dark Theme**: Professional dark mode with modern aesthetics
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Bootstrap 5**: Latest Bootstrap framework for consistent styling

## 🏗️ Architecture

### Backend
- **Flask Web Framework**: Python-based web application
- **SQLAlchemy ORM**: Database management and object-relational mapping
- **SimPy**: Discrete-event simulation framework
- **Background Threading**: Asynchronous simulation execution

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Bootstrap 5**: Responsive CSS framework
- **Chart.js**: Interactive data visualization
- **Font Awesome**: Professional icon library

### Database
- **SQLite**: Lightweight database for development
- **User Management**: User accounts, roles, and authentication
- **Simulation Data**: Session logs, performance metrics, and results

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Sanjanack/orbital-cdn-simulation.git
   cd orbital-cdn-simulation
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your browser and navigate to `http://localhost:5000`
   - Default admin credentials: `admin` / `admin123`

## 📖 Usage Guide

### For Regular Users

1. **Registration & Login**
   - Create a new account or login with existing credentials
   - Access your personalized dashboard

2. **Running Simulations (Multi-user, Time-based)**
   - What it does: runs a short scenario where multiple users request content over time
   - Why: observe trends like cache hit rate, cache utilization, content mix, hits vs misses
   - How:
     - Set Duration, Request Interval, Cache Size, Catalog Size, Number of Users, Logging Interval
     - Click "Start Simulation" and wait for completion
     - Results section shows charts once done

3. **Viewing Results**
   - Access comprehensive charts and analytics
   - Review session history
   - Export data for further analysis

4. **Request Content On-Demand (Single request)**
   - What it does: sends one content request and instantly reports Hit/Miss and delivery details
   - How:
     - Choose Content Type, Size (MB), Speed (x), optional Content ID
     - Click "Send Request"
     - See: Hit/Miss, Delivery Source (Cache or Ground), Satellite, Delivery time (s)
   - Tips:
     - Repeat the same Content ID to see first Miss then Hits
     - Small Cache Size + many unique items = evictions (LRU); re-request evicted items to see Miss
     - Increase Speed to reduce reported delivery time

### For Administrators

1. **System Overview**
   - Monitor total users, sessions, and system performance
   - View real-time analytics and trends

2. **User Management**
   - View all registered users
   - Monitor user activity and sessions
   - Export user data

3. **System Analytics**
   - Track user growth over time
   - Monitor session activity patterns
   - Analyze system performance metrics

## 🔧 Configuration

### Simulation Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `simulation_duration` | Total simulation time in units | 200 | 50-1000 |
| `request_interval` | Time between user requests | 3.0 | 1-20 |
| `cache_size` | Maximum cache items | 12 | 5-50 |
| `content_catalog_size` | Available content items | 20 | 10-100 |
| `user_count` | Number of simulated users | 4 | 1-20 |
| `log_interval` | Performance logging frequency | 10.0 | 5-50 |

### Environment Variables

```bash
# Flask Configuration
export FLASK_ENV=development
export FLASK_DEBUG=1
export SECRET_KEY=your-secret-key-here

# Database Configuration
export DATABASE_URL=sqlite:///orbital_cdn.db
```

## 📊 Simulation Features

### Content Types
- **Video Content**: High-bandwidth streaming media
- **Audio Content**: Music, podcasts, and audio files
- **Image Content**: Photos, graphics, and visual media
- **Document Content**: Text files, PDFs, and documents
- **Game Content**: Interactive gaming applications

### Caching Strategy
- **LRU Algorithm**: Least Recently Used eviction policy
- **Cache Hit Optimization**: Maximize content availability
- **Performance Monitoring**: Real-time cache efficiency tracking
- **Adaptive Sizing**: Configurable cache capacity

### Performance Metrics
- **Cache Hit Rate**: Percentage of requests served from cache
- **Cache Utilization**: Current cache capacity usage
- **Request Latency**: Response time for content delivery
- **Throughput**: Content delivery volume over time

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

### Simulation Sessions
```sql
CREATE TABLE simulation_session (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    config TEXT NOT NULL,
    results TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Content Requests
```sql
CREATE TABLE content_request (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    timestamp FLOAT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    content_id VARCHAR(100) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    content_size INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    delivery_source VARCHAR(50) NOT NULL,
    cache_utilization FLOAT NOT NULL,
    hit_rate FLOAT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES simulation_session (id)
);
```

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **Role-based Access**: Separate user and admin privileges
- **Input Validation**: Form validation and sanitization
- **CSRF Protection**: Built-in Flask security features

## 📱 Responsive Design

- **Mobile-First Approach**: Optimized for mobile devices
- **Bootstrap Grid System**: Responsive layout across screen sizes
- **Touch-Friendly Interface**: Optimized for touch devices
- **Cross-Browser Compatibility**: Works on all modern browsers

## 🚀 Performance Optimization

- **Background Processing**: Non-blocking simulation execution
- **Efficient Caching**: Optimized LRU algorithm implementation
- **Database Indexing**: Fast query performance
- **Lazy Loading**: Load data on-demand for better performance

## 🧪 Testing

### Manual Testing
1. **User Registration**: Test account creation and validation
2. **Login System**: Verify authentication and session management
3. **Simulation Execution**: Test various parameter combinations
4. **Results Display**: Verify chart generation and data accuracy

### Automated Testing (Future Enhancement)
- Unit tests for core simulation logic
- Integration tests for web endpoints
- Performance tests for simulation engine
- UI automation tests

## 🔮 Future Enhancements

### Planned Features
- **Multi-Satellite Support**: Simulate satellite constellations
- **Advanced Caching**: Machine learning-based cache optimization
- **Real-time Collaboration**: Multi-user simulation sessions
- **API Integration**: RESTful API for external applications
- **Cloud Deployment**: Docker containerization and cloud hosting

### Technical Improvements
- **WebSocket Support**: Real-time communication
- **Redis Integration**: High-performance caching
- **PostgreSQL**: Production-ready database
- **Microservices**: Scalable architecture design

## 👥 Team

- **Neha** (U25UV23T064063) - Lead Developer & Simulation Engineer
- **Sanjana C K** (U25UV22T064049) - System Architect & UI/UX Designer

## 📄 License

This project is developed for educational and research purposes. All rights reserved.

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔗 Related Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SimPy Documentation](https://simpy.readthedocs.io/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [Chart.js Documentation](https://www.chartjs.org/)

---

**Made with ❤️ by Team Orbital CDN**

*Exploring the future of satellite-based content delivery networks through advanced simulation technology.*
