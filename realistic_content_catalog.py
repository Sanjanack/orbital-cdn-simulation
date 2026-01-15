"""
Realistic Content Catalog for NTN Satellite CDN
===============================================

This module provides a comprehensive catalog of real-world content types
that would be delivered through a satellite CDN network.

Team Members:
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class ContentItem:
    """Real content item with all necessary metadata"""
    content_id: str
    title: str
    content_type: str  # video, image, document, audio, application
    size_mb: int
    description: str
    popularity_score: float  # 0.0 to 1.0
    category: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Real-world content catalog
REALISTIC_CONTENT_CATALOG = [
    # Video Content
    ContentItem(
        content_id="video_news_bulletin_1080p",
        title="Daily News Bulletin",
        content_type="video",
        size_mb=450,
        description="1080p news broadcast - 30 minutes",
        popularity_score=0.85,
        category="news",
        metadata={"duration_minutes": 30, "resolution": "1920x1080", "format": "mp4"}
    ),
    ContentItem(
        content_id="video_educational_tutorial",
        title="Python Programming Tutorial",
        content_type="video",
        size_mb=320,
        description="Educational video tutorial - 45 minutes",
        popularity_score=0.75,
        category="education",
        metadata={"duration_minutes": 45, "resolution": "1280x720", "format": "mp4"}
    ),
    ContentItem(
        content_id="video_sports_highlights",
        title="Sports Highlights Reel",
        content_type="video",
        size_mb=280,
        description="Sports highlights compilation - 20 minutes",
        popularity_score=0.90,
        category="sports",
        metadata={"duration_minutes": 20, "resolution": "1920x1080", "format": "mp4"}
    ),
    ContentItem(
        content_id="video_weather_forecast",
        title="Weather Forecast",
        content_type="video",
        size_mb=120,
        description="Daily weather forecast - 5 minutes",
        popularity_score=0.70,
        category="weather",
        metadata={"duration_minutes": 5, "resolution": "1280x720", "format": "mp4"}
    ),
    
    # Image Content
    ContentItem(
        content_id="image_satellite_map",
        title="Satellite Imagery Map",
        content_type="image",
        size_mb=45,
        description="High-resolution satellite map",
        popularity_score=0.65,
        category="maps",
        metadata={"resolution": "4096x4096", "format": "png"}
    ),
    ContentItem(
        content_id="image_news_photo",
        title="Breaking News Photo",
        content_type="image",
        size_mb=12,
        description="High-quality news photograph",
        popularity_score=0.80,
        category="news",
        metadata={"resolution": "2048x1536", "format": "jpg"}
    ),
    ContentItem(
        content_id="image_infographic",
        title="Data Visualization Infographic",
        content_type="image",
        size_mb=8,
        description="Educational infographic",
        popularity_score=0.60,
        category="education",
        metadata={"resolution": "1920x1080", "format": "png"}
    ),
    
    # Document Content
    ContentItem(
        content_id="doc_emergency_protocol",
        title="Emergency Response Protocol",
        content_type="document",
        size_mb=5,
        description="Emergency procedures document",
        popularity_score=0.55,
        category="emergency",
        metadata={"pages": 25, "format": "pdf"}
    ),
    ContentItem(
        content_id="doc_weather_report",
        title="Detailed Weather Report",
        content_type="document",
        size_mb=3,
        description="Comprehensive weather analysis",
        popularity_score=0.70,
        category="weather",
        metadata={"pages": 10, "format": "pdf"}
    ),
    ContentItem(
        content_id="doc_news_article",
        title="Breaking News Article",
        content_type="document",
        size_mb=2,
        description="Latest news article",
        popularity_score=0.85,
        category="news",
        metadata={"pages": 5, "format": "pdf"}
    ),
    
    # Audio Content
    ContentItem(
        content_id="audio_news_podcast",
        title="News Podcast Episode",
        content_type="audio",
        size_mb=35,
        description="Daily news podcast - 30 minutes",
        popularity_score=0.75,
        category="news",
        metadata={"duration_minutes": 30, "format": "mp3", "bitrate": "128kbps"}
    ),
    ContentItem(
        content_id="audio_emergency_alert",
        title="Emergency Alert Broadcast",
        content_type="audio",
        size_mb=2,
        description="Emergency alert message",
        popularity_score=0.95,
        category="emergency",
        metadata={"duration_minutes": 2, "format": "mp3"}
    ),
    ContentItem(
        content_id="audio_educational_lecture",
        title="Educational Lecture",
        content_type="audio",
        size_mb=45,
        description="University lecture recording - 60 minutes",
        popularity_score=0.65,
        category="education",
        metadata={"duration_minutes": 60, "format": "mp3"}
    ),
    
    # Application/Software Content
    ContentItem(
        content_id="app_emergency_guide",
        title="Emergency Response App",
        content_type="application",
        size_mb=25,
        description="Mobile emergency response application",
        popularity_score=0.80,
        category="emergency",
        metadata={"platform": "android", "version": "2.1"}
    ),
    ContentItem(
        content_id="app_weather_monitor",
        title="Weather Monitoring Tool",
        content_type="application",
        size_mb=18,
        description="Real-time weather monitoring application",
        popularity_score=0.70,
        category="weather",
        metadata={"platform": "cross-platform", "version": "1.5"}
    ),
]

def get_content_by_id(content_id: str) -> ContentItem:
    """Get content item by ID"""
    for item in REALISTIC_CONTENT_CATALOG:
        if item.content_id == content_id:
            return item
    return None

def get_content_by_type(content_type: str) -> List[ContentItem]:
    """Get all content items of a specific type"""
    return [item for item in REALISTIC_CONTENT_CATALOG if item.content_type == content_type]

def get_popular_content(limit: int = 10) -> List[ContentItem]:
    """Get most popular content items"""
    sorted_content = sorted(REALISTIC_CONTENT_CATALOG, key=lambda x: x.popularity_score, reverse=True)
    return sorted_content[:limit]

def search_content(query: str) -> List[ContentItem]:
    """Search content by title or description"""
    query_lower = query.lower()
    return [
        item for item in REALISTIC_CONTENT_CATALOG
        if query_lower in item.title.lower() or query_lower in item.description.lower()
    ]

