from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.db import get_db
from app.models import User, Tree, Token
from app.schemas import TokenResponse, TokenDetailResponse, MintTokenResponse
from app.services.business_logic import TokenService, TreeService
from app.services.external_services import CardGenerationService
from app.auth import get_current_user
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tokens"])


@router.post("/trees/{tree_id}/mint", response_model=MintTokenResponse)
def mint_token(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mint an NFT token for a tree.
    
    Triggers card generation (Role C) and creates token record.
    """
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mint this tree",
        )
    
    # Check if token already exists
    existing_token = db.query(Token).filter(Token.tree_id == tree_id).first()
    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already minted for this tree",
        )
    
    # Call card generation service
    card_data = CardGenerationService.generate_nft_card(
        tree_id=tree_id,
        species=tree.species,
        latitude=tree.latitude,
        longitude=tree.longitude,
        health_score=tree.health_score,
    )
    
    # Generate unique token ID
    token_id = f"TREE-{tree_id}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create token record
    token = TokenService.create_token(
        db=db,
        token_id=token_id,
        tree_id=tree_id,
        owner_id=current_user.id,
        image_uri=card_data["image_uri"],
        metadata_uri=card_data["metadata_uri"],
        base_value=100.0,
    )
    
    logger.info(f"Minted token {token_id} for tree {tree_id}")
    
    return MintTokenResponse(
        token_id=token_id,
        tree_id=tree_id,
        image_uri=card_data["image_uri"],
        metadata_uri=card_data["metadata_uri"],
        message="Token successfully minted",
    )


@router.get("/tokens/{token_id}", response_model=TokenDetailResponse)
def get_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get token details by token ID.
    
    Includes tree information, metadata, and current value.
    """
    token = TokenService.get_token(db, token_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )
    
    if token.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this token",
        )
    
    return token


@router.get("/tokens", response_model=list[TokenResponse])
def list_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List all tokens owned by the current user.
    
    - **limit**: Maximum number of tokens to return
    - **offset**: Number of tokens to skip
    """
    tokens = TokenService.get_user_tokens(db, current_user.id)
    
    # Apply pagination
    paginated_tokens = tokens[offset:offset + limit]
    
    return paginated_tokens
