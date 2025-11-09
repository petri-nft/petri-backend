from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import User
from app.schemas import PortfolioResponse
from app.services.business_logic import PortfolioService
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/me", response_model=PortfolioResponse)
def get_my_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get complete portfolio for the current user.
    
    Includes all trees, tokens, health scores, and total value.
    """
    portfolio = PortfolioService.get_user_portfolio(db, current_user.id)
    return portfolio
