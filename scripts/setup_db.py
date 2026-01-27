"""
Database setup script for Supabase
Creates necessary tables and initializes the database
"""
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.supabase_client import SupabaseClient


def create_tables():
    """Create necessary tables in Supabase."""
    client = SupabaseClient()
    
    if not client.is_connected():
        print("❌ Cannot connect to Supabase. Please set SUPABASE_URL and SUPABASE_KEY.")
        return False
    
    print("Creating tables...")
    
    # SQL for creating tables (run these in Supabase SQL editor)
    sql_statements = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    last_period_date DATE,
    cycle_length INTEGER DEFAULT 28,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    session_data JSONB,
    body_state JSONB,
    cycle_phase TEXT,
    duration_minutes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    session_id UUID REFERENCES sessions(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback(session_id);
"""
    
    print("\n" + "="*60)
    print("SQL Statements to run in Supabase SQL Editor:")
    print("="*60)
    print(sql_statements)
    print("="*60)
    print("\nTo create tables:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL above")
    print("4. Run the SQL")
    print("\nAlternatively, you can use the Supabase Python client:")
    print("  client.rpc('exec_sql', {'sql': '...'})")
    
    return True


def test_connection():
    """Test database connection."""
    client = SupabaseClient()
    
    if client.is_connected():
        print("✅ Supabase connection successful!")
        return True
    else:
        print("❌ Supabase connection failed.")
        print("\nPlease set environment variables:")
        print("  export SUPABASE_URL=your_supabase_url")
        print("  export SUPABASE_KEY=your_supabase_key")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Supabase Database Setup")
    print("="*60)
    
    if test_connection():
        create_tables()
    else:
        print("\nSetup instructions:")
        print("1. Get your Supabase URL and API key from:")
        print("   https://app.supabase.com/project/_/settings/api")
        print("2. Set environment variables:")
        print("   export SUPABASE_URL=your_url")
        print("   export SUPABASE_KEY=your_key")
        print("3. Run this script again")
