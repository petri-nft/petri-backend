from sqlalchemy.orm import Session
from app.models import User, Tree, Token, HealthHistory, Trade, TreeSpecies
from app.schemas import TreeResponse, PortfolioResponse, PortfolioItem, TreeListResponse
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TreeService:
    """Service for tree operations."""
    
    @staticmethod
    def create_tree(db: Session, user_id: int, species: str, latitude: float, 
                    longitude: float, location_name: Optional[str] = None,
                    description: Optional[str] = None, nickname: Optional[str] = None,
                    photo_url: Optional[str] = None) -> Tree:
        """Create a new tree record."""
        # Check if nickname is unique per user (if provided)
        if nickname:
            existing = db.query(Tree).filter(
                Tree.user_id == user_id,
                Tree.nickname == nickname
            ).first()
            if existing:
                raise ValueError(f"You already have a tree named '{nickname}'. Please choose a different name.")
        
        tree = Tree(
            user_id=user_id,
            species=species,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            description=description,
            nickname=nickname,
            photo_url=photo_url,
            health_score=100.0,
            current_value=100.0,
        )
        db.add(tree)
        db.commit()
        db.refresh(tree)
        
        # Record initial health
        health_record = HealthHistory(
            tree_id=tree.id,
            health_score=100.0,
            token_value=100.0,
            event_type="planting",
            description="Tree planted",
        )
        db.add(health_record)
        db.commit()
        
        logger.info(f"Created tree {tree.id} for user {user_id}")
        return tree
    
    @staticmethod
    def get_tree(db: Session, tree_id: int) -> Optional[Tree]:
        """Get a tree by ID."""
        return db.query(Tree).filter(Tree.id == tree_id).first()
    
    @staticmethod
    def get_user_trees(db: Session, user_id: int) -> List[Tree]:
        """Get all trees for a user."""
        return db.query(Tree).filter(Tree.user_id == user_id).all()
    
    @staticmethod
    def update_tree_health(db: Session, tree_id: int, health_score: float, 
                          token_value: float, event_type: Optional[str] = None,
                          description: Optional[str] = None) -> Tree:
        """Update tree health score and record history."""
        tree = db.query(Tree).filter(Tree.id == tree_id).first()
        if not tree:
            return None
        
        tree.health_score = health_score
        tree.current_value = token_value
        tree.updated_at = datetime.utcnow()
        
        # Update token value if exists
        token = db.query(Token).filter(Token.tree_id == tree_id).first()
        if token:
            token.current_value = token_value
            token.updated_at = datetime.utcnow()
        
        # Record health history
        health_record = HealthHistory(
            tree_id=tree_id,
            health_score=health_score,
            token_value=token_value,
            event_type=event_type,
            description=description,
        )
        
        db.add(health_record)
        db.commit()
        db.refresh(tree)
        
        logger.info(f"Updated health for tree {tree_id}: score={health_score}")
        return tree
    
    @staticmethod
    def get_health_history(db: Session, tree_id: int, limit: int = 50) -> List[HealthHistory]:
        """Get health history for a tree."""
        return db.query(HealthHistory)\
            .filter(HealthHistory.tree_id == tree_id)\
            .order_by(HealthHistory.recorded_at.desc())\
            .limit(limit)\
            .all()


class TokenService:
    """Service for token/NFT operations."""
    
    @staticmethod
    def create_token(db: Session, token_id: str, tree_id: int, owner_id: int,
                    image_uri: str, metadata_uri: str, base_value: float = 100.0) -> Token:
        """Create a new NFT token."""
        token = Token(
            token_id=token_id,
            tree_id=tree_id,
            owner_id=owner_id,
            image_uri=image_uri,
            metadata_uri=metadata_uri,
            current_value=base_value,
            base_value=base_value,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        
        logger.info(f"Created token {token_id} for tree {tree_id}")
        return token
    
    @staticmethod
    def get_token(db: Session, token_id: str) -> Optional[Token]:
        """Get a token by token ID."""
        return db.query(Token).filter(Token.token_id == token_id).first()
    
    @staticmethod
    def get_token_by_tree(db: Session, tree_id: int) -> Optional[Token]:
        """Get token for a specific tree."""
        return db.query(Token).filter(Token.tree_id == tree_id).first()
    
    @staticmethod
    def get_user_tokens(db: Session, user_id: int) -> List[Token]:
        """Get all tokens owned by a user."""
        return db.query(Token).filter(Token.owner_id == user_id).all()


class TradeService:
    """Service for trading operations."""
    
    @staticmethod
    def create_trade(db: Session, token_id: int, user_id: int, trade_type: str,
                    quantity: float, price_per_unit: float) -> Trade:
        """Create a new trade record."""
        total_value = quantity * price_per_unit
        
        trade = Trade(
            token_id=token_id,
            user_id=user_id,
            trade_type=trade_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_value=total_value,
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        logger.info(f"Created {trade_type} trade for token {token_id}: qty={quantity}, price={price_per_unit}")
        return trade
    
    @staticmethod
    def get_token_trades(db: Session, token_id: int, limit: int = 50) -> List[Trade]:
        """Get trades for a specific token."""
        return db.query(Trade)\
            .filter(Trade.token_id == token_id)\
            .order_by(Trade.created_at.desc())\
            .limit(limit)\
            .all()


class PortfolioService:
    """Service for portfolio operations."""
    
    @staticmethod
    def get_user_portfolio(db: Session, user_id: int) -> PortfolioResponse:
        """Get complete portfolio for a user."""
        trees = db.query(Tree).filter(Tree.user_id == user_id).all()
        
        items = []
        total_value = 0.0
        
        for tree in trees:
            token = db.query(Token).filter(Token.tree_id == tree.id).first()
            
            item = PortfolioItem(
                tree=TreeListResponse.from_orm(tree),
                token=TokenService.get_token_by_tree(db, tree.id),
                health_score=tree.health_score,
                current_value=tree.current_value,
            )
            items.append(item)
            total_value += tree.current_value
        
        return PortfolioResponse(
            user_id=user_id,
            total_trees=len(trees),
            total_value=total_value,
            items=items,
        )
