"""
Session repository for yoga session logging
"""
from typing import Dict, List, Optional
from datetime import datetime

from .database_factory import DatabaseFactory


class SessionRepository:
    """
    Repository for yoga session operations.
    Uses DatabaseFactory to support multiple database backends.
    """
    
    def __init__(self, db_type: Optional[str] = None):
        """
        Initialize session repository.
        
        Args:
            db_type: Database type ("sqlite", "mongodb", "supabase")
                    If None, auto-detects from environment or defaults to SQLite
        """
        self.db = DatabaseFactory.create_client(db_type)
    
    def save_session(
        self,
        user_id: str,
        session_data: Dict
    ) -> bool:
        """
        Save a yoga session.
        
        Args:
            user_id: User identifier
            session_data: Complete session data including sequence, cues, etc.
        
        Returns:
            True if successful
        """
        session_record = {
            "user_id": user_id,
            "session_data": session_data,
            "created_at": datetime.now().isoformat(),
            "cycle_phase": session_data.get("body_state", {}).get("cycle_phase"),
            "duration_minutes": session_data.get("body_state", {}).get("duration_minutes")
        }
        return self.db.save_session(user_id, session_record)
    
    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get user's recent sessions.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
        
        Returns:
            List of session dictionaries
        """
        if not self.db.is_connected():
            return []
        
        # Placeholder implementation
        # Future: Implement actual Supabase query
        # response = self.client.table("sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return []
    
    def save_feedback(
        self,
        user_id: str,
        session_id: str,
        feedback: Dict
    ) -> bool:
        """
        Save user feedback for a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            feedback: Feedback data (rating, notes, etc.)
        
        Returns:
            True if successful
        """
        if not self.db.is_connected():
            return False
        
        # Placeholder implementation
        return True
