#!/usr/bin/env python3
"""
Initialize Supabase tables for AI features
Runs SQLAlchemy models to create tables
"""
import sys
sys.path.insert(0, '/home/admin/Desktop/Petri/backend')

# Set environment to use Supabase
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres.uzodglaesnusjlitzlut:sb_secret_UmV_jlSmbF9nSJclpDEdAw_Nt-DDp0T@db.uzodglaesnusjlitzlut.supabase.co:5432/postgres'

from app.database.db import engine, Base
from app.models import User, Tree, Token, Share, Trade, HealthHistory, TreePersonality, ChatMessage

print("🔌 Connecting to Supabase PostgreSQL...")
try:
    # Test connection
    with engine.connect() as connection:
        print("✅ Connected to Supabase!\n")
    
    print("📝 Creating database tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ All tables created successfully!\n")
    
    print("📊 Tables created:")
    print("   ✓ users")
    print("   ✓ trees")
    print("   ✓ tokens")
    print("   ✓ shares")
    print("   ✓ trades")
    print("   ✓ health_history")
    print("   ✓ tree_personalities")
    print("   ✓ chat_messages")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
