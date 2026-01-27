"""
MongoDB client - Free tier available (MongoDB Atlas)
512MB free storage, perfect for small projects.
"""
from typing import Optional, Dict, List
import os
from datetime import datetime
import json


class MongoDBClient:
    """
    MongoDB client using MongoDB Atlas free tier.
    Free tier: 512MB storage, shared cluster
    """
    
    def __init__(self):
        """
        Initialize MongoDB client.
        Requires MONGODB_URI environment variable.
        """
        self.uri = os.getenv("MONGODB_URI")
        self.client = None
        self.db = None
        
        if self.uri:
            try:
                from pymongo import MongoClient
                self.client = MongoClient(self.uri)
                self.db = self.client.yoga_coach
                print("✓ MongoDB connected successfully")
            except ImportError:
                print("Warning: pymongo not installed. Install with: pip install pymongo")
            except Exception as e:
                print(f"Warning: Failed to connect to MongoDB: {e}")
        else:
            print("Warning: MONGODB_URI not set. MongoDB features disabled.")
            print("Get free MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register")
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        return self.db is not None
    
    def save_user_data(self, user_id: str, data: dict) -> bool:
        """Save user data."""
        if not self.is_connected():
            return False
        
        try:
            self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        **data,
                        "updated_at": datetime.now()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[dict]:
        """Retrieve user data."""
        if not self.is_connected():
            return None
        
        try:
            return self.db.users.find_one({"id": user_id})
        except Exception as e:
            print(f"Error retrieving user data: {e}")
            return None
    
    def save_session(self, user_id: str, session_data: dict) -> bool:
        """Save yoga session."""
        if not self.is_connected():
            return False
        
        try:
            session_record = {
                "user_id": user_id,
                "session_data": session_data,
                "body_state": session_data.get("body_state", {}),
                "cycle_phase": session_data.get("body_state", {}).get("cycle_phase"),
                "duration_minutes": session_data.get("body_state", {}).get("duration_minutes"),
                "created_at": datetime.now()
            }
            
            self.db.sessions.insert_one(session_record)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's recent sessions."""
        if not self.is_connected():
            return []
        
        try:
            sessions = list(
                self.db.sessions
                .find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            return sessions
        except Exception as e:
            print(f"Error retrieving sessions: {e}")
            return []
