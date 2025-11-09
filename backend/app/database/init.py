"""
Database initialization and migration utilities.
"""
from sqlalchemy import text
from app.database.db import engine, SessionLocal
from app.models import User, Tree, Token, Share, Trade, HealthHistory
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Initialize database and create all tables."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def insert_sample_data():
    """Insert sample data for testing."""
    db = SessionLocal()
    try:
        # Check if sample data already exists
        user_count = db.query(User).count()
        if user_count > 0:
            logger.info("Sample data already exists, skipping insertion")
            return
        
        # Create sample users
        from app.auth import hash_password
        
        user1 = User(
            username="alice",
            email="alice@example.com",
            password_hash=hash_password("password123"),
        )
        user2 = User(
            username="bob",
            email="bob@example.com",
            password_hash=hash_password("password123"),
        )
        
        db.add_all([user1, user2])
        db.commit()
        
        logger.info("Sample users inserted")
        
        # Create sample trees
        tree1 = Tree(
            user_id=user1.id,
            species="oak",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="Central Park, NYC",
            health_score=95.0,
            current_value=95.0,
            description="A mighty oak in Central Park",
        )
        tree2 = Tree(
            user_id=user1.id,
            species="pine",
            latitude=34.0522,
            longitude=-118.2437,
            location_name="Griffith Park, LA",
            health_score=88.0,
            current_value=88.0,
            description="Pine tree in LA",
        )
        tree3 = Tree(
            user_id=user2.id,
            species="birch",
            latitude=51.5074,
            longitude=-0.1278,
            location_name="Hyde Park, London",
            health_score=92.0,
            current_value=92.0,
            description="Beautiful birch in Hyde Park",
        )
        
        db.add_all([tree1, tree2, tree3])
        db.commit()
        
        logger.info("Sample trees inserted")
        
        # Create sample tokens
        token1 = Token(
            token_id="TREE-1-ABC12345",
            tree_id=tree1.id,
            owner_id=user1.id,
            image_uri="https://placehold.co/400?text=Oak+Tree",
            metadata_uri="ipfs://QmSampleMetadata1",
            current_value=95.0,
            base_value=100.0,
        )
        token2 = Token(
            token_id="TREE-2-DEF67890",
            tree_id=tree2.id,
            owner_id=user1.id,
            image_uri="https://placehold.co/400?text=Pine+Tree",
            metadata_uri="ipfs://QmSampleMetadata2",
            current_value=88.0,
            base_value=100.0,
        )
        
        db.add_all([token1, token2])
        db.commit()
        
        logger.info("Sample tokens inserted")
        
        # Create sample health history
        from datetime import datetime, timedelta
        
        for i in range(10):
            days_ago = 7 * (10 - i)
            health_record = HealthHistory(
                tree_id=tree1.id,
                health_score=100.0 - (i * 0.5),
                token_value=100.0 - (i * 0.5),
                event_type="growth" if i % 2 == 0 else "maintenance",
                description=f"Week {i} health check",
                recorded_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            db.add(health_record)
        
        db.commit()
        
        logger.info("Sample health history inserted")
        logger.info("Sample data insertion completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting sample data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    insert_sample_data()
