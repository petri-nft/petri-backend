from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base


class TreeSpecies(str, enum.Enum):
    """Enum for tree species."""
    OAK = "oak"
    PINE = "pine"
    BIRCH = "birch"
    MAPLE = "maple"
    ELM = "elm"
    SPRUCE = "spruce"


class TradeType(str, enum.Enum):
    """Enum for trade types."""
    BUY = "buy"
    SELL = "sell"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trees = relationship("Tree", back_populates="owner", cascade="all, delete-orphan")
    tokens = relationship("Token", back_populates="owner")
    trades = relationship("Trade", back_populates="user")


class Tree(Base):
    """Tree model."""
    __tablename__ = "trees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    species = Column(Enum(TreeSpecies), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(255))
    planting_date = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Float, default=100.0)
    current_value = Column(Float, default=0.0)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="trees")
    token = relationship("Token", back_populates="tree", uselist=False)
    health_history = relationship("HealthHistory", back_populates="tree", cascade="all, delete-orphan")


class Token(Base):
    """NFT Token model."""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(255), unique=True, index=True, nullable=False)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metadata_uri = Column(String(255))  # IPFS or cloud URL
    image_uri = Column(String(255))  # URL to generated NFT card image
    current_value = Column(Float, default=0.0)
    base_value = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tree = relationship("Tree", back_populates="token")
    owner = relationship("User", back_populates="tokens")
    shares = relationship("Share", back_populates="token", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="token")


class Share(Base):
    """Fractional share of a token."""
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # Percentage of ownership
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    token = relationship("Token", back_populates="shares")
    owner = relationship("User")


class Trade(Base):
    """Trade/transaction model for buying/selling shares."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trade_type = Column(Enum(TradeType), nullable=False)
    quantity = Column(Float, nullable=False)  # Share quantity
    price_per_unit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    token = relationship("Token", back_populates="trades")
    user = relationship("User", back_populates="trades")


class HealthHistory(Base):
    """Health score history for timeline visualization."""
    __tablename__ = "health_history"
    
    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False)
    health_score = Column(Float, nullable=False)
    token_value = Column(Float)
    event_type = Column(String(50))  # e.g., "growth", "drought", "pest", "recovery"
    description = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tree = relationship("Tree", back_populates="health_history")
