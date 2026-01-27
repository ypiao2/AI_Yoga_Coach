"""
SQLite client - Free, local database (no setup required!)
Perfect for development and small-scale production.
"""
import sqlite3
import json
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path


class SQLiteClient:
    """
    SQLite client - completely free, no API keys needed.
    Data is stored in a local file.
    """
    
    def __init__(self, db_path: str = "yoga_coach.db"):
        """
        Initialize SQLite client.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        
        # Create tables
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                last_period_date TEXT,
                cycle_length INTEGER DEFAULT 28,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                session_data TEXT,
                body_state TEXT,
                cycle_phase TEXT,
                duration_minutes INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
            ON sessions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_created_at 
            ON sessions(created_at DESC)
        """)
        
        self.conn.commit()
        print(f"✓ SQLite database initialized: {self.db_path}")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.conn is not None
    
    def save_user_data(self, user_id: str, data: dict) -> bool:
        """
        Save user data.
        
        Args:
            user_id: User identifier
            data: Data to save
        
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            # Upsert user data
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (id, last_period_date, cycle_length, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                data.get("last_period_date"),
                data.get("cycle_length", 28),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[dict]:
        """
        Retrieve user data.
        
        Args:
            user_id: User identifier
        
        Returns:
            User data dictionary or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error retrieving user data: {e}")
            return None
    
    def save_session(self, user_id: str, session_data: dict) -> bool:
        """
        Save yoga session.
        
        Args:
            user_id: User identifier
            session_data: Session data dictionary
        
        Returns:
            True if successful
        """
        try:
            import uuid
            session_id = str(uuid.uuid4())
            
            body_state = session_data.get("body_state", {})
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions 
                (id, user_id, session_data, body_state, cycle_phase, duration_minutes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                json.dumps(session_data),
                json.dumps(body_state),
                body_state.get("cycle_phase"),
                body_state.get("duration_minutes"),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get user's recent sessions.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
        
        Returns:
            List of session dictionaries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                session = dict(row)
                # Parse JSON fields
                if session.get("session_data"):
                    session["session_data"] = json.loads(session["session_data"])
                if session.get("body_state"):
                    session["body_state"] = json.loads(session["body_state"])
                sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"Error retrieving sessions: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
