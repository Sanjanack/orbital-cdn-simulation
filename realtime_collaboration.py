"""
Real-time Collaboration Module for Satellite CDN
================================================

This module provides WebSocket-based real-time collaboration features:
- Multi-user simulation sessions
- Real-time cache updates
- Live performance metrics sharing
- Collaborative content requests

Team Members:
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json
from typing import Dict, List, Optional
from collections import defaultdict

class CollaborationManager:
    """Manages real-time collaboration sessions"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.user_sessions: Dict[int, str] = {}  # user_id -> session_id
        self.session_participants: Dict[str, List[int]] = defaultdict(list)  # session_id -> [user_ids]
        self.session_cache_state: Dict[str, Dict] = {}  # session_id -> cache_state
        
    def create_session(self, session_id: str, creator_id: int, config: Dict) -> Dict:
        """Create a new collaboration session"""
        session_data = {
            'session_id': session_id,
            'creator_id': creator_id,
            'config': config,
            'participants': [creator_id],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'cache_state': {},
            'request_history': [],
            'performance_metrics': {
                'total_requests': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'hit_rate': 0.0
            }
        }
        
        self.active_sessions[session_id] = session_data
        self.user_sessions[creator_id] = session_id
        self.session_participants[session_id] = [creator_id]
        
        return session_data
    
    def join_session(self, session_id: str, user_id: int) -> Optional[Dict]:
        """Add user to collaboration session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        if user_id not in session['participants']:
            session['participants'].append(user_id)
            self.session_participants[session_id].append(user_id)
            self.user_sessions[user_id] = session_id
        
        return session
    
    def leave_session(self, session_id: str, user_id: int):
        """Remove user from collaboration session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if user_id in session['participants']:
                session['participants'].remove(user_id)
                if session_id in self.session_participants:
                    if user_id in self.session_participants[session_id]:
                        self.session_participants[session_id].remove(user_id)
            
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
    
    def update_cache_state(self, session_id: str, cache_state: Dict):
        """Update cache state for a session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['cache_state'] = cache_state
            self.session_cache_state[session_id] = cache_state
            
            # Broadcast to all participants
            self.broadcast_to_session(session_id, 'cache_update', {
                'cache_state': cache_state,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def add_request(self, session_id: str, request_data: Dict):
        """Add a content request to session history"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['request_history'].append(request_data)
            
            # Update performance metrics
            if request_data.get('status') == 'HIT':
                session['performance_metrics']['cache_hits'] += 1
            else:
                session['performance_metrics']['cache_misses'] += 1
            
            session['performance_metrics']['total_requests'] += 1
            total = session['performance_metrics']['total_requests']
            hits = session['performance_metrics']['cache_hits']
            session['performance_metrics']['hit_rate'] = (hits / total * 100) if total > 0 else 0
            
            # Broadcast request to all participants
            self.broadcast_to_session(session_id, 'new_request', {
                'request': request_data,
                'performance': session['performance_metrics'],
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def broadcast_to_session(self, session_id: str, event: str, data: Dict):
        """Broadcast event to all participants in a session"""
        self.socketio.emit(event, data, room=session_id)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.active_sessions.get(session_id)
    
    def get_user_session(self, user_id: int) -> Optional[str]:
        """Get session ID for a user"""
        return self.user_sessions.get(user_id)

# Global collaboration manager instance
collaboration_manager: Optional[CollaborationManager] = None

def init_collaboration(socketio: SocketIO):
    """Initialize collaboration manager"""
    global collaboration_manager
    collaboration_manager = CollaborationManager(socketio)
    return collaboration_manager

def register_socketio_handlers(socketio: SocketIO, collaboration_manager: CollaborationManager):
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        emit('connected', {'status': 'success', 'message': 'Connected to real-time collaboration'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        pass
    
    @socketio.on('join_session')
    def handle_join_session(data):
        """Handle user joining a collaboration session"""
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if not session_id or not user_id:
            emit('error', {'message': 'Session ID and User ID required'})
            return
        
        session = collaboration_manager.join_session(session_id, user_id)
        if session:
            join_room(session_id)
            emit('joined_session', {
                'session_id': session_id,
                'session_data': session,
                'message': 'Successfully joined collaboration session'
            })
            
            # Notify other participants
            collaboration_manager.broadcast_to_session(session_id, 'user_joined', {
                'user_id': user_id,
                'participants': session['participants'],
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            emit('error', {'message': 'Session not found'})
    
    @socketio.on('leave_session')
    def handle_leave_session(data):
        """Handle user leaving a collaboration session"""
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if session_id and user_id:
            collaboration_manager.leave_session(session_id, user_id)
            leave_room(session_id)
            emit('left_session', {'session_id': session_id})
            
            # Notify other participants
            collaboration_manager.broadcast_to_session(session_id, 'user_left', {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    @socketio.on('request_content')
    def handle_content_request(data):
        """Handle content request from a user"""
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        content_id = data.get('content_id')
        
        if not all([session_id, user_id, content_id]):
            emit('error', {'message': 'Missing required parameters'})
            return
        
        # This will be handled by the main app, but we acknowledge it here
        emit('request_received', {
            'session_id': session_id,
            'user_id': user_id,
            'content_id': content_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('get_session_state')
    def handle_get_session_state(data):
        """Handle request for current session state"""
        session_id = data.get('session_id')
        
        if session_id:
            session = collaboration_manager.get_session(session_id)
            if session:
                emit('session_state', {
                    'session': session,
                    'cache_state': collaboration_manager.session_cache_state.get(session_id, {}),
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                emit('error', {'message': 'Session not found'})
