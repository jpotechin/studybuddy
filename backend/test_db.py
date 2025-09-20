#!/usr/bin/env python3
"""
Simple database connection test for StudyBuddy.
Run this to verify your DATABASE_URL is working correctly.
"""

import os
from dotenv import load_dotenv
from database import get_db_connection, init_db

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔍 Testing database connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        print("   Please set it in your .env file")
        return False
    
    print(f"✅ DATABASE_URL is set: {database_url[:20]}...")
    
    try:
        # Test connection
        print("🔌 Testing database connection...")
        conn = get_db_connection()
        print("✅ Database connection successful!")
        
        # Test basic query
        print("📊 Testing basic query...")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        result = cur.fetchone()
        if result:
            # Handle both dict and tuple results
            if isinstance(result, dict):
                version = result['version']
            else:
                version = result[0]
            print(f"✅ PostgreSQL version: {version}")
        else:
            print("❌ No result from version query")
            return False
        
        # Initialize database
        print("🏗️  Initializing database tables...")
        init_db()
        print("✅ Database tables initialized!")
        
        # Test table access (reconnect to get fresh cursor)
        print("📋 Testing table access...")
        conn.close()  # Close the old connection
        conn = get_db_connection()  # Get new connection
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        result = cur.fetchone()
        if result:
            # Handle both dict and tuple results
            if isinstance(result, dict):
                user_count = result['count']
            else:
                user_count = result[0]
            print(f"✅ Users table accessible, current count: {user_count}")
        else:
            print("❌ No result from users count query")
            return False
        
        conn.close()
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed with error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 StudyBuddy Database Test")
    print("=" * 40)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Database is ready! You can now run the application.")
        print("   Next steps:")
        print("   1. Run: uv run python init_db.py (to create admin user)")
        print("   2. Run: uv run uvicorn main:app --reload")
    else:
        print("\n❌ Database setup failed. Please check your DATABASE_URL.")
        print("   Make sure you have:")
        print("   1. Set up a PostgreSQL database (Neon, Supabase, etc.)")
        print("   2. Copied the connection string to your .env file")
        print("   3. The connection string is in format: postgresql://user:pass@host:port/db")
