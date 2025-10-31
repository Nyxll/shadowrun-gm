"""
Session Management for Game Sessions
"""

from typing import Dict, List, Optional
from datetime import datetime
from fastapi import WebSocket


class GameSession:
    """Manages a single game session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict] = []
        self.active_characters: List[str] = []
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 20 messages to manage token usage
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def add_character(self, character_name: str):
        """Add character to active session"""
        if character_name not in self.active_characters:
            self.active_characters.append(character_name)


class SessionManager:
    """Manages all game sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.websockets: Dict[str, WebSocket] = {}
    
    def create_session(self, session_id: str) -> GameSession:
        """Create new game session"""
        session = GameSession(session_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def register_websocket(self, session_id: str, websocket: WebSocket):
        """Register websocket for session"""
        self.websockets[session_id] = websocket
    
    def unregister_websocket(self, session_id: str):
        """Unregister websocket"""
        if session_id in self.websockets:
            del self.websockets[session_id]
