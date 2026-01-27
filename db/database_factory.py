"""
Database Factory - Choose your free database!
Supports: SQLite (default, free), MongoDB Atlas (free tier), Supabase (optional)
"""
import os
from typing import Optional

from config import Config


class DatabaseFactory:
    """
    Factory to create database client based on configuration.
    Defaults to SQLite (completely free, no setup).
    """
    
    @staticmethod
    def create_client(db_type: Optional[str] = None):
        """
        Create database client.
        
        Args:
            db_type: Database type ("sqlite", "mongodb", "supabase")
                    If None, auto-detects from environment or defaults to SQLite
        
        Returns:
            Database client instance
        """
        if db_type is None:
            db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        if db_type == "sqlite":
            from .sqlite_client import SQLiteClient
            db_path = os.getenv("SQLITE_DB_PATH", "yoga_coach.db")
            return SQLiteClient(db_path=db_path)
        
        elif db_type == "mongodb":
            from .mongodb_client import MongoDBClient
            return MongoDBClient()
        
        elif db_type == "supabase":
            from .supabase_client import SupabaseClient
            return SupabaseClient()
        
        else:
            raise ValueError(f"Unknown database type: {db_type}. Use 'sqlite', 'mongodb', or 'supabase'")
