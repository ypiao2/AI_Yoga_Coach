"""
Test database connection - Works with SQLite, MongoDB, or Supabase
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database_factory import DatabaseFactory
from db.user_repo import UserRepository
from db.session_repo import SessionRepository


def test_database():
    """Test database connection and operations."""
    print("="*60)
    print("Database Connection Test")
    print("="*60)
    
    # Detect database type
    import os
    db_type = os.getenv("DB_TYPE", "sqlite")
    print(f"\nUsing database: {db_type}")
    
    # Test connection
    print("\n1. Testing connection...")
    try:
        db = DatabaseFactory.create_client(db_type)
        if db.is_connected():
            print("✅ Database connected successfully!")
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test user repository
    print("\n2. Testing user repository...")
    try:
        user_repo = UserRepository(db_type=db_type)
        
        # Save test user
        test_user_id = "test_user_123"
        success = user_repo.save_user_cycle_info(
            test_user_id,
            "2026-01-20",
            28
        )
        
        if success:
            print("✅ User data saved successfully")
        else:
            print("❌ Failed to save user data")
            return False
        
        # Retrieve user
        user_data = user_repo.get_user_cycle_info(test_user_id)
        if user_data:
            print(f"✅ User data retrieved: {user_data}")
        else:
            print("❌ Failed to retrieve user data")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test session repository
    print("\n3. Testing session repository...")
    try:
        session_repo = SessionRepository(db_type=db_type)
        
        test_session = {
            "body_state": {
                "cycle_phase": "menstrual",
                "intensity": "low",
                "duration_minutes": 20
            },
            "sequence": {"poses": []},
            "cues": {"instructions": []}
        }
        
        success = session_repo.save_session(test_user_id, test_session)
        if success:
            print("✅ Session saved successfully")
        else:
            print("❌ Failed to save session")
            return False
        
        # Retrieve sessions
        sessions = session_repo.get_user_sessions(test_user_id, limit=5)
        print(f"✅ Retrieved {len(sessions)} sessions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ All database tests passed!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
