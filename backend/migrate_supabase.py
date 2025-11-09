#!/usr/bin/env python3
"""
Supabase Database Migration Script
Applies SQL migrations to Supabase PostgreSQL database
"""
import psycopg2
import os
import sys

# Supabase credentials
SUPABASE_URL = "uzodglaesnusjlitzlut"
DB_HOST = "db.uzodglaesnusjlitzlut.supabase.co"
DB_USER = "postgres"
DB_PASSWORD = "sb_secret_UmV_jlSmbF9nSJclpDEdAw_Nt-DDp0T"
DB_NAME = "postgres"
DB_PORT = 5432

def run_migration(migration_file):
    """Execute SQL migration file against Supabase"""
    try:
        # Connect to Supabase PostgreSQL
        print(f"📡 Connecting to Supabase PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        print("✅ Connected to Supabase!\n")
        
        # Read migration file
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        print(f"📝 Executing migration: {migration_file}")
        print("=" * 60)
        
        # Execute the SQL
        cursor.execute(sql)
        conn.commit()
        
        print("=" * 60)
        print("✅ Migration completed successfully!\n")
        
        # Show tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        print("📊 Tables in database:")
        for row in cursor.fetchall():
            print(f"   • {row[0]}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migration_file = "/home/admin/Desktop/Petri/backend/migrations/002_add_ai_features.sql"
    run_migration(migration_file)
