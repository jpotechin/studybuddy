#!/usr/bin/env python3
"""
Database initialization script for StudyBuddy.
This script creates the admin user with a hashed password.
"""

import os
import sys
from dotenv import load_dotenv
from auth import get_password_hash, ADMIN_USERNAME, ADMIN_PASSWORD
from database import init_db, get_db_connection, execute_query

def create_admin_user():
    """Create the admin user with hashed password"""
    print("Creating admin user...")
    
    # Check if admin user already exists
    existing_user = execute_query("SELECT id FROM users WHERE username = %s", (ADMIN_USERNAME,), fetch_one=True)
    
    if existing_user:
        print(f"Admin user '{ADMIN_USERNAME}' already exists!")
        return
    
    # Hash the password
    hashed_password = get_password_hash(ADMIN_PASSWORD)
    
    # Create admin user
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO users (id, username, email, hashed_password) VALUES (%s, %s, %s, %s)", 
                   (1, ADMIN_USERNAME, "admin@studybuddy.local", hashed_password))
        conn.commit()
        
        print(f"✅ Admin user '{ADMIN_USERNAME}' created successfully!")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Email: admin@studybuddy.local")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("\n🔐 Change the password by setting ADMIN_PASSWORD environment variable")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Failed to create admin user: {e}")
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing StudyBuddy Database...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database tables
    print("Creating database tables...")
    init_db()
    print("✅ Database tables created!")
    
    # Create admin user
    create_admin_user()
    
    print("\n🎉 Database initialization complete!")
    print("\nNext steps:")
    print("1. Set ADMIN_USERNAME and ADMIN_PASSWORD environment variables")
    print("2. Run the application: uvicorn main:app --reload")

if __name__ == "__main__":
    main()
