from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import User, Token, Trade
from app.schemas import TradeCreate, TradeResponse
from app.services.business_logic import TokenService, TradeService
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tokens", tags=["trades"])


@router.post("/{token_id}/trade", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def create_trade(
    token_id: str,
    trade_data: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a trade (buy/sell) for a token.
    
    Simulates fractional share trading.
    - **trade_type**: "buy" or "sell"
    - **quantity**: Amount of shares to trade
    - **price_per_unit**: Price per share
    """
    token = TokenService.get_token(db, token_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    
    # Validate trade type
    if trade_data.trade_type not in ["buy", "sell"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trade_type must be 'buy' or 'sell'",
        )
    
    # For sell, check user owns shares
    if trade_data.trade_type == "sell" and token.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only sell tokens you own",
        )
    
    # Get token ID from database
    db_token = db.query(Token).filter(Token.token_id == token_id).first()
    
    # Create trade record
    trade = TradeService.create_trade(
        db=db,
        token_id=db_token.id,
        user_id=current_user.id,
        trade_type=trade_data.trade_type,
        quantity=trade_data.quantity,
        price_per_unit=trade_data.price_per_unit,
    )
    
    logger.info(f"Created {trade.trade_type} trade: user={current_user.id}, token={token_id}, qty={trade.quantity}")
    
    return trade


@router.get("/{token_id}/trades", response_model=list[TradeResponse])
def get_token_trades(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get all trades for a token.
    
    Used to show trade history/activity.
    """
    token = TokenService.get_token(db, token_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    
    # Get database token to get its ID
    db_token = db.query(Token).filter(Token.token_id == token_id).first()
    
    trades = TradeService.get_token_trades(db, db_token.id, limit)
    
    return trades
