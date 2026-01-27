"""
User repository for user data operations
"""
from typing import Optional, Dict
from .database_factory import DatabaseFactory


class UserRepository:
    """
    Repository for user data operations.
    Uses DatabaseFactory to support multiple database backends.
    """
    
    def __init__(self, db_type: Optional[str] = None):
        """
        Initialize user repository.
        
        Args:
            db_type: Database type ("sqlite", "mongodb", "supabase")
                    If None, auto-detects from environment or defaults to SQLite
        """
        self.db = DatabaseFactory.create_client(db_type)
    
    def save_user_cycle_info(
        self,
        user_id: str,
        last_period_date: str,
        cycle_length: int
    ) -> bool:
        """
        Save user's cycle information.
        
        Args:
            user_id: User identifier
            last_period_date: Last period date (YYYY-MM-DD)
            cycle_length: Typical cycle length in days
        
        Returns:
            True if successful
        """
        data = {
            "user_id": user_id,
            "last_period_date": last_period_date,
            "cycle_length": cycle_length,
            "updated_at": "now()"
        }
        return self.db.save_user_data(user_id, data)
    
    def get_user_cycle_info(self, user_id: str) -> Optional[Dict]:
        """
        Get user's cycle information.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with cycle info or None
        """
        user_data = self.db.get_user_data(user_id)
        if user_data:
            return {
                "last_period_date": user_data.get("last_period_date"),
                "cycle_length": user_data.get("cycle_length", 28)
            }
        return None
