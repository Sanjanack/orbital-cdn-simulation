"""
Simple Database Viewer
======================
Run this script to view all data in your database.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

def view_database():
    """View all database contents"""
    
    db_path = 'instance/orbital_cdn.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("   Run the application first to create the database.")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        print("=" * 70)
        print("🗄️  ORBITAL CDN DATABASE VIEWER")
        print("=" * 70)
        print(f"Database Location: {os.path.abspath(db_path)}")
        print(f"Viewing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Show all tables
        print("\n📋 AVAILABLE TABLES:")
        print("-" * 70)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        if not tables.empty:
            for idx, row in tables.iterrows():
                count = pd.read_sql(f"SELECT COUNT(*) as count FROM {row['name']}", conn)
                print(f"  {idx+1}. {row['name']:<25} ({count.iloc[0]['count']} records)")
        else:
            print("  No tables found!")
        
        # Show Users
        print("\n👥 USERS TABLE:")
        print("-" * 70)
        try:
            users = pd.read_sql("""
                SELECT id, username, email, role, 
                       datetime(created_at) as created_at,
                       datetime(last_login) as last_login
                FROM user
                ORDER BY id
            """, conn)
            if not users.empty:
                print(users.to_string(index=False))
            else:
                print("  No users found!")
        except Exception as e:
            print(f"  Error reading users: {e}")
        
        # Show Simulation Sessions
        print("\n📊 SIMULATION SESSIONS:")
        print("-" * 70)
        try:
            sessions = pd.read_sql("""
                SELECT id, user_id, status, 
                       datetime(created_at) as created_at
                FROM simulation_session
                ORDER BY created_at DESC
                LIMIT 10
            """, conn)
            if not sessions.empty:
                print(sessions.to_string(index=False))
            else:
                print("  No simulation sessions found!")
        except Exception as e:
            print(f"  Error reading sessions: {e}")
        
        # Show Content Requests
        print("\n📥 CONTENT REQUESTS (Last 10):")
        print("-" * 70)
        try:
            requests = pd.read_sql("""
                SELECT id, session_id, user_id, content_id, 
                       content_type, content_size, status, 
                       delivery_source, hit_rate,
                       datetime(timestamp, 'unixepoch') as request_time
                FROM content_request
                ORDER BY timestamp DESC
                LIMIT 10
            """, conn)
            if not requests.empty:
                print(requests.to_string(index=False))
            else:
                print("  No content requests found!")
        except Exception as e:
            print(f"  Error reading requests: {e}")
        
        # Show Satellites
        print("\n🛰️  SATELLITE NODES:")
        print("-" * 70)
        try:
            satellites = pd.read_sql("""
                SELECT id, satellite_id, name, latitude, longitude, 
                       altitude, cache_size, cache_utilization, 
                       hit_rate, status
                FROM satellite_node
                ORDER BY id
            """, conn)
            if not satellites.empty:
                print(satellites.to_string(index=False))
            else:
                print("  No satellites found!")
        except Exception as e:
            print(f"  Error reading satellites: {e}")
        
        # Show User Messages
        print("\n💬 USER MESSAGES (Last 10):")
        print("-" * 70)
        try:
            messages = pd.read_sql("""
                SELECT id, sender_id, receiver_id, 
                       substr(message, 1, 50) as message_preview,
                       read, datetime(created_at) as created_at
                FROM user_message
                ORDER BY created_at DESC
                LIMIT 10
            """, conn)
            if not messages.empty:
                print(messages.to_string(index=False))
            else:
                print("  No messages found!")
        except Exception as e:
            print(f"  Error reading messages: {e}")
        
        # Show Shared Content
        print("\n📤 SHARED CONTENT (Last 10):")
        print("-" * 70)
        try:
            shared = pd.read_sql("""
                SELECT id, sharer_id, receiver_id, content_id, 
                       content_type, content_size, accessed,
                       datetime(shared_at) as shared_at
                FROM shared_content
                ORDER BY shared_at DESC
                LIMIT 10
            """, conn)
            if not shared.empty:
                print(shared.to_string(index=False))
            else:
                print("  No shared content found!")
        except Exception as e:
            print(f"  Error reading shared content: {e}")
        
        # Statistics Summary
        print("\n📈 DATABASE STATISTICS:")
        print("-" * 70)
        try:
            stats = {}
            
            # Count users
            result = pd.read_sql("SELECT COUNT(*) as count FROM user", conn)
            stats['Total Users'] = result.iloc[0]['count']
            
            # Count sessions
            result = pd.read_sql("SELECT COUNT(*) as count FROM simulation_session", conn)
            stats['Total Sessions'] = result.iloc[0]['count']
            
            # Count requests
            result = pd.read_sql("SELECT COUNT(*) as count FROM content_request", conn)
            stats['Total Requests'] = result.iloc[0]['count']
            
            # Count satellites
            result = pd.read_sql("SELECT COUNT(*) as count FROM satellite_node", conn)
            stats['Total Satellites'] = result.iloc[0]['count']
            
            # Average hit rate
            result = pd.read_sql("SELECT AVG(hit_rate) as avg_hit_rate FROM content_request WHERE hit_rate > 0", conn)
            if result.iloc[0]['avg_hit_rate']:
                stats['Average Hit Rate'] = f"{result.iloc[0]['avg_hit_rate']:.2f}%"
            else:
                stats['Average Hit Rate'] = "N/A"
            
            for key, value in stats.items():
                print(f"  {key:<25}: {value}")
                
        except Exception as e:
            print(f"  Error calculating statistics: {e}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Database viewing complete!")
        print("=" * 70)
        print("\n💡 Tip: Use DB Browser for SQLite for a visual interface:")
        print("   https://sqlitebrowser.org/")
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print(f"   Make sure the database file exists at: {db_path}")

if __name__ == "__main__":
    view_database()
