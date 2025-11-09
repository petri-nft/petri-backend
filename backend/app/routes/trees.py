from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.db import get_db
from app.models import User, Tree
from app.schemas import TreeCreate, TreeResponse, TreeListResponse, HealthUpdateRequest, HealthHistoryResponse
from app.services.business_logic import TreeService
from app.services.external_services import CardGenerationService, HealthScoringService
from app.auth import get_current_user
import logging
from math import ceil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trees", tags=["trees"])


@router.post("", response_model=TreeResponse, status_code=status.HTTP_201_CREATED)
def plant_tree(
    tree_data: TreeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Plant a new tree.
    
    - **species**: Species of tree (oak, pine, birch, maple, elm, spruce)
    - **latitude**: GPS latitude
    - **longitude**: GPS longitude
    - **location_name**: Optional location name
    - **description**: Optional description
    """
    tree = TreeService.create_tree(
        db=db,
        user_id=current_user.id,
        species=tree_data.species,
        latitude=tree_data.latitude,
        longitude=tree_data.longitude,
        location_name=tree_data.location_name,
        description=tree_data.description,
    )
    
    return tree


@router.get("/{tree_id}", response_model=TreeResponse)
def get_tree(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tree details by ID."""
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    if tree.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this tree",
        )
    
    return tree


@router.get("", response_model=list[TreeListResponse])
def list_trees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List all trees for the current user.
    
    - **limit**: Maximum number of trees to return
    - **offset**: Number of trees to skip
    """
    trees = TreeService.get_user_trees(db, current_user.id)
    
    # Apply pagination
    paginated_trees = trees[offset:offset + limit]
    
    return paginated_trees


@router.post("/{tree_id}/updateHealth", response_model=TreeResponse)
def update_health(
    tree_id: int,
    health_data: HealthUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update tree health score.
    
    Called by Role D (Health Scoring Service).
    Updates the health score and records history.
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
            detail="Not authorized to update this tree",
        )
    
    # Calculate token value based on health score
    # Formula: token_value = base_value * (health_score / 100)
    token_value = 100.0 * (health_data.health_score / 100.0)
    
    updated_tree = TreeService.update_tree_health(
        db=db,
        tree_id=tree_id,
        health_score=health_data.health_score,
        token_value=token_value,
        event_type=health_data.event_type,
        description=health_data.description,
    )
    
    return updated_tree


@router.get("/{tree_id}/health-history", response_model=list[HealthHistoryResponse])
def get_health_history(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get health history for a tree (timeline data).
    
    Used for displaying charts and timeline on frontend.
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
            detail="Not authorized to view this tree",
        )
    
    history = TreeService.get_health_history(db, tree_id, limit)
    
    return history
