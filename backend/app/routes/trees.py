from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.db import get_db
from app.models import User, Tree, Token
from app.schemas import TreeCreate, TreeResponse, TreeListResponse, HealthUpdateRequest, HealthHistoryResponse
from app.services.business_logic import TreeService
from app.services.external_services import CardGenerationService, HealthScoringService
from app.services.ai_service import TreePersonalityService, AIConversationService, TTSService, PublicTreeService
from app.services.nft_service import NFTGenerationService
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
    - **nickname**: Optional user-given name for the tree (must be unique per user)
    - **photo_url**: Optional URL to the captured photo
    """
    try:
        tree = TreeService.create_tree(
            db=db,
            user_id=current_user.id,
            species=tree_data.species,
            latitude=tree_data.latitude,
            longitude=tree_data.longitude,
            location_name=tree_data.location_name,
            description=tree_data.description,
            nickname=tree_data.nickname,
            photo_url=tree_data.photo_url,
        )
        
        # Auto-create a default personality for the tree so chat is available immediately
        try:
            default_tone = "wise" if tree_data.species == "oak" else "enthusiastic"
            default_name = f"{tree_data.species.capitalize()}"
            if tree_data.nickname:
                default_name = tree_data.nickname
            
            default_background = f"A beautiful {tree_data.species} tree. Loves to share stories and help others grow."
            
            personality = TreePersonalityService.create_personality(
                db=db,
                tree_id=tree.id,
                name=default_name,
                tone=default_tone,
                background=default_background,
                traits={"age": "young", "wisdom": "growing"},
                voice_id=TTSService.select_voice_for_tone(default_tone)
            )
            logger.info(f"Auto-created default personality for tree {tree.id}")
        except Exception as e:
            logger.warning(f"Could not auto-create personality for tree {tree.id}: {e}")
            # Continue anyway - personality can be set later
        
        return tree
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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


@router.get("/voices", response_model=dict)
def get_available_voices():
    """Get list of available ElevenLabs voices for trees."""
    voices = TTSService.get_available_voices()
    return {
        "voices": [
            {
                "name": name,
                "voice_id": info["voice_id"],
                "description": info["description"]
            }
            for name, info in voices.items()
        ]
    }


@router.get("/marketplace/trees", response_model=dict)
def get_public_trees(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Browse public trees in the marketplace.
    
    No authentication required - anyone can browse.
    """
    trees = PublicTreeService.list_public_trees(db, limit, offset)
    
    return {
        "count": len(trees),
        "limit": limit,
        "offset": offset,
        "trees": [
            {
                "id": tree.id,
                "species": tree.species,
                "location_name": tree.location_name,
                "health_score": tree.health_score,
                "current_value": tree.current_value,
                "owner": tree.owner.username if tree.owner else "Unknown",
                "personality": {
                    "name": tree.personality.name if tree.personality else "Unknown",
                    "tone": tree.personality.tone if tree.personality else "unknown",
                } if tree.personality else None,
                "created_at": tree.created_at
            }
            for tree in trees
        ]
    }


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


# ==================== AI PERSONALITY & INTERACTION ROUTES ====================

@router.post("/{tree_id}/personality", response_model=dict, status_code=status.HTTP_201_CREATED)
def set_tree_personality(
    tree_id: int,
    personality_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set or update tree personality and AI traits.
    
    Only the tree owner can set personality.
    
    Request body example:
    {
        "name": "Wise Oak",
        "tone": "humorous",
        "background": "An old oak tree with a funny personality...",
        "traits": {
            "loves_jokes": true,
            "favorite_topic": "nature"
        }
    }
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
            detail="Only tree owner can set personality",
        )
    
    # Select appropriate voice based on tone
    voice_id = TTSService.select_voice_for_tone(personality_data.get("tone", ""))
    
    personality = TreePersonalityService.create_personality(
        db=db,
        tree_id=tree_id,
        name=personality_data.get("name"),
        tone=personality_data.get("tone"),
        background=personality_data.get("background"),
        traits=personality_data.get("traits"),
        voice_id=voice_id
    )
    
    # Update tree personality reference
    tree.personality_id = personality.id
    db.commit()
    
    return {
        "status": "success",
        "message": f"Personality set for {tree.species}",
        "personality_id": personality.id,
        "voice_id": voice_id,
        "available_voices": list(TTSService.AVAILABLE_VOICES.keys())
    }


@router.get("/{tree_id}/personality", response_model=dict)
def get_tree_personality(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tree personality settings. Auto-creates a default if none exists."""
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    # Allow viewing if owner or tree is public
    if tree.user_id != current_user.id and not tree.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this tree",
        )
    
    personality = TreePersonalityService.get_personality(db, tree_id)
    
    # Auto-create a default personality if none exists
    if not personality:
        try:
            logger.info(f"Creating default personality for tree {tree_id} ({tree.species})")
            default_tone = "wise" if tree.species == "oak" else "enthusiastic"
            default_name = tree.nickname if tree.nickname else f"{tree.species.capitalize()}"
            default_background = f"A beautiful {tree.species} tree. Loves to share stories and help others grow."
            
            personality = TreePersonalityService.create_personality(
                db=db,
                tree_id=tree_id,
                name=default_name,
                tone=default_tone,
                background=default_background,
                traits={"age": "young", "wisdom": "growing"},
                voice_id=TTSService.select_voice_for_tone(default_tone)
            )
            logger.info(f"Default personality created for tree {tree_id}")
        except Exception as e:
            logger.error(f"Failed to create default personality: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create default personality for tree",
            )
    
    return {
        "id": personality.id,
        "tree_id": personality.tree_id,
        "name": personality.name,
        "tone": personality.tone,
        "background": personality.background,
        "traits": personality.traits,
        "voice_id": personality.voice_id,
        "created_at": personality.created_at,
        "updated_at": personality.updated_at
    }


@router.post("/{tree_id}/chat", response_model=dict)
def chat_with_tree(
    tree_id: int,
    message_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat with tree AI personality.
    
    Request body:
    {
        "content": "Hey tree, how are you?",
        "include_audio": true
    }
    
    Returns AI response with optional audio.
    """
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    # Allow interaction if owner or tree is public
    if tree.user_id != current_user.id and not tree.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This tree is private",
        )
    
    personality = TreePersonalityService.get_personality(db, tree_id)
    if not personality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree has no personality set",
        )
    
    try:
        interaction = AIConversationService.chat_with_tree(
            db=db,
            tree_id=tree_id,
            user_id=current_user.id,
            user_message=message_data.get("content"),
            include_audio=message_data.get("include_audio", False)
        )
        
        return {
            "status": "success",
            "user_message": interaction.user_message,
            "tree_response": interaction.tree_response,
            "audio_url": interaction.audio_url,
            "tree_name": interaction.tree_name,
            "tree_personality": {
                "name": interaction.tree_personality.name,
                "tone": interaction.tree_personality.tone,
                "background": interaction.tree_personality.background
            }
        }
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.post("/{tree_id}/transcribe-voice", response_model=dict)
async def transcribe_voice_message(
    tree_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe user's voice message to text.
    
    Accepts audio file (mp3, wav, m4a, etc.) and returns transcribed text.
    Uses Groq Whisper API or alternative speech-to-text service.
    
    Request:
    - audio_file: Binary audio file (multipart form data)
    
    Response:
    {
        "success": true,
        "transcribed_text": "Hello tree, how are you?",
        "original_filename": "voice_message.mp3",
        "size": 12345
    }
    """
    from app.services.voice_service import VoiceTranscriptionService, AudioStorageService
    import tempfile
    
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    # Allow interaction if owner or tree is public
    if tree.user_id != current_user.id and not tree.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to interact with this tree",
        )
    
    try:
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            # Read uploaded file
            contents = await audio_file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Transcribe audio
        try:
            transcribed_text = VoiceTranscriptionService.transcribe_audio(tmp_path)
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        return {
            "success": True,
            "transcribed_text": transcribed_text,
            "original_filename": audio_file.filename,
            "size": len(contents)
        }
    
    except Exception as e:
        logger.error(f"Voice transcription error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "transcribed_text": ""
        }


@router.get("/{tree_id}/chat-history", response_model=dict)
def get_chat_history(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
):
    """Get chat history with a tree."""
    tree = TreeService.get_tree(db, tree_id)
    
    if not tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree not found",
        )
    
    # Allow viewing if owner or tree is public
    if tree.user_id != current_user.id and not tree.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this tree",
        )
    
    personality = TreePersonalityService.get_personality(db, tree_id)
    if not personality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No personality set for this tree",
        )
    
    messages = AIConversationService.get_conversation_history(db, tree_id, limit)
    
    return {
        "tree_id": tree_id,
        "tree_name": tree.species,
        "personality": {
            "name": personality.name,
            "tone": personality.tone,
        },
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "audio_url": msg.audio_url,
                "created_at": msg.created_at
            }
            for msg in reversed(messages)
        ]
    }


@router.post("/{tree_id}/set-public", response_model=dict)
def set_tree_public_status(
    tree_id: int,
    public_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Make tree public (for marketplace) so others can interact with it.
    
    Request body:
    {
        "is_public": true
    }
    """
    tree = PublicTreeService.set_tree_public(
        db=db,
        tree_id=tree_id,
        user_id=current_user.id,
        is_public=public_data.get("is_public", False)
    )
    
    return {
        "status": "success",
        "tree_id": tree.id,
        "is_public": tree.is_public,
        "message": f"Tree is now {'public' if tree.is_public else 'private'}"
    }


@router.post("/{tree_id}/generate-nft")
def generate_nft(
    tree_id: int,
    user_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate NFT image and metadata for a tree.
    
    - **tree_id**: ID of the tree
    - **user_image**: Image file to be used for the NFT
    
    Returns:
    - **imageUrl**: URL to the generated NFT image
    - **metadataUrl**: URL to the generated metadata JSON
    - **token_id**: ID of the created token in the database
    """
    try:
        # Get the tree from database
        tree = db.query(Tree).filter(
            Tree.id == tree_id,
            Tree.user_id == current_user.id
        ).first()
        
        if not tree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tree not found or you don't have permission to modify it"
            )
        
        # Check if NFT already exists for this tree
        existing_token = db.query(Token).filter(Token.tree_id == tree_id).first()
        if existing_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NFT already exists for this tree"
            )
        
        # Generate NFT image
        nft_service = NFTGenerationService()
        image_path = nft_service.generate_nft_image(user_image.file, str(tree_id))
        
        # Generate metadata
        # Hardcoded values for now - you can add these as optional parameters later
        metadata_path = nft_service.generate_metadata(
            tree_id=str(tree_id),
            species=tree.species.value,
            health_score=tree.health_score,
            planting_date=tree.planting_date,
            base_url="http://localhost:8000",
            description=tree.description or f"A living digital asset for a {tree.species.value} tree"
        )
        
        # Get base URL from request (you should pass this from frontend or config)
        base_url = "http://localhost:8000"  # TODO: Make this configurable
        image_url = nft_service.get_image_url(str(tree_id), base_url)
        metadata_url = nft_service.get_metadata_url(str(tree_id), base_url)
        
        # Create Token record in database
        token = Token(
            token_id=f"TREE_{tree_id}_{datetime.utcnow().timestamp()}",
            tree_id=tree_id,
            owner_id=current_user.id,
            image_uri=image_url,
            metadata_uri=metadata_url,
            base_value=100.0,
            current_value=100.0
        )
        db.add(token)
        
        # Also save the NFT image URL to the tree
        tree.nft_image_url = image_url
        db.commit()
        db.refresh(token)
        db.refresh(tree)
        
        logger.info(f"Generated NFT for tree {tree_id}, token {token.id}")
        
        return {
            "status": "success",
            "imageUrl": image_url,
            "metadataUrl": metadata_url,
            "token_id": token.id,
            "message": "NFT generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating NFT for tree {tree_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating NFT: {str(e)}"
        )
