"""Session manager for conversation memory"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import OrderedDict
from threading import Lock

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger(__name__)


# Maximum number of sessions to keep in memory
MAX_SESSIONS = 100

# Maximum messages per session
MAX_MESSAGES_PER_SESSION = 10


class Session:
    """Represents a study session with conversation history"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_activity = self.created_at
        self.messages: List[BaseMessage] = []
        self.doc_ids: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the session, maintaining max limit"""
        self.messages.append(message)
        self.last_activity = datetime.now(timezone.utc).isoformat()
        
        # Trim to max messages (keep most recent)
        if len(self.messages) > MAX_MESSAGES_PER_SESSION * 2:
            # Keep pairs of human/ai messages
            self.messages = self.messages[-MAX_MESSAGES_PER_SESSION * 2:]
    
    def add_human_message(self, content: str) -> None:
        """Add a human message"""
        self.add_message(HumanMessage(content=content))
    
    def add_ai_message(self, content: str) -> None:
        """Add an AI message"""
        self.add_message(AIMessage(content=content))
    
    def add_doc_id(self, doc_id: str) -> None:
        """Track a document used in this session"""
        if doc_id and doc_id not in self.doc_ids:
            self.doc_ids.append(doc_id)
    
    def get_messages(self) -> List[BaseMessage]:
        """Get conversation messages"""
        return self.messages.copy()
    
    def get_message_count(self) -> int:
        """Get number of messages"""
        return len(self.messages)
    
    def clear_messages(self) -> None:
        """Clear conversation history"""
        self.messages = []
        self.last_activity = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages),
            "doc_ids": self.doc_ids,
            "metadata": self.metadata
        }


class SessionManager:
    """
    Manages study sessions with LRU eviction.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, max_sessions: int = MAX_SESSIONS):
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = Lock()
        
        logger.info(f"SessionManager initialized (max sessions: {max_sessions})")
    
    def create_session(self) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session = Session(session_id)
        
        with self._lock:
            # Evict oldest session if at capacity
            while len(self._sessions) >= self.max_sessions:
                evicted_id, _ = self._sessions.popitem(last=False)
                logger.info(f"Evicted session '{evicted_id}' (LRU)")
            
            self._sessions[session_id] = session
        
        logger.info(f"Created new session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID, moving it to end (most recently used)"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions.move_to_end(session_id)
                return self._sessions[session_id]
        return None
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create new one"""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        return self.create_session()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        with self._lock:
            return [session.to_dict() for session in self._sessions.values()]
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        with self._lock:
            return len(self._sessions)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours"""
        cutoff = datetime.now(timezone.utc)
        removed = 0
        
        with self._lock:
            sessions_to_remove = []
            for session_id, session in self._sessions.items():
                last_activity = datetime.fromisoformat(session.last_activity)
                age_hours = (cutoff - last_activity).total_seconds() / 3600
                if age_hours > max_age_hours:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
                removed += 1
        
        if removed:
            logger.info(f"Cleaned up {removed} old sessions")
        
        return removed
