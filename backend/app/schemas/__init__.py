from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List


# ==================== USER SCHEMAS ====================
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str
    user_id: int
    username: str


# ==================== TREE SCHEMAS ====================
class TreeCreate(BaseModel):
    """Schema for creating a new tree."""
    species: str
    latitude: float
    longitude: float
    nickname: str  # REQUIRED - User-given name for the tree (must be unique per user)
    location_name: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None  # URL to the captured photo
    
    @field_validator('species')
    @classmethod
    def validate_species(cls, v: str) -> str:
        """Validate that species is one of the allowed values."""
        valid_species = ['oak', 'pine', 'birch', 'maple', 'elm', 'spruce']
        if v.lower() not in valid_species:
            raise ValueError(f'Species must be one of: {", ".join(valid_species)}')
        return v.lower()


class TreeUpdate(BaseModel):
    """Schema for updating a tree."""
    species: Optional[str] = None
    location_name: Optional[str] = None
    description: Optional[str] = None


class TreeResponse(BaseModel):
    """Schema for tree response."""
    id: int
    user_id: int
    species: str
    nickname: Optional[str]
    latitude: float
    longitude: float
    location_name: Optional[str]
    planting_date: datetime
    health_score: float
    current_value: float
    description: Optional[str]
    photo_url: Optional[str]
    nft_image_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TreeListResponse(BaseModel):
    """Schema for listing trees."""
    id: int
    user_id: int
    species: str
    nickname: Optional[str]
    latitude: float
    longitude: float
    location_name: Optional[str]
    planting_date: datetime
    health_score: float
    current_value: float
    photo_url: Optional[str]
    nft_image_url: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== TOKEN SCHEMAS ====================
class TokenCreate(BaseModel):
    """Schema for creating an NFT token (minting)."""
    tree_id: int
    image_uri: str
    metadata_uri: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    id: int
    token_id: str
    tree_id: int
    owner_id: int
    image_uri: Optional[str]
    metadata_uri: Optional[str]
    current_value: float
    base_value: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenDetailResponse(BaseModel):
    """Schema for detailed token response with tree info."""
    id: int
    token_id: str
    tree_id: int
    owner_id: int
    image_uri: Optional[str]
    metadata_uri: Optional[str]
    current_value: float
    base_value: float
    tree: TreeResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== HEALTH HISTORY SCHEMAS ====================
class HealthHistoryResponse(BaseModel):
    """Schema for health history response."""
    id: int
    tree_id: int
    health_score: float
    token_value: Optional[float]
    event_type: Optional[str]
    description: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class HealthUpdateRequest(BaseModel):
    """Schema for updating health score."""
    health_score: float
    event_type: Optional[str] = None
    description: Optional[str] = None


# ==================== TRADE SCHEMAS ====================
class TradeCreate(BaseModel):
    """Schema for creating a trade."""
    trade_type: str  # "buy" or "sell"
    quantity: float
    price_per_unit: float


class TradeResponse(BaseModel):
    """Schema for trade response."""
    id: int
    token_id: int
    user_id: int
    trade_type: str
    quantity: float
    price_per_unit: float
    total_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PORTFOLIO SCHEMAS ====================
class PortfolioItem(BaseModel):
    """Schema for portfolio item."""
    tree: TreeListResponse
    token: Optional[TokenResponse]
    health_score: float
    current_value: float


class PortfolioResponse(BaseModel):
    """Schema for portfolio response."""
    user_id: int
    total_trees: int
    total_value: float
    items: List[PortfolioItem]


# ==================== RESPONSE SCHEMAS ====================
class MintTokenResponse(BaseModel):
    """Schema for mint token response."""
    token_id: str
    tree_id: int
    image_uri: str
    metadata_uri: str
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    status_code: int


# ==================== AI PERSONALITY SCHEMAS ====================
class TreePersonalityCreate(BaseModel):
    """Schema for creating tree personality."""
    name: str
    tone: str  # e.g., "humorous", "wise", "educational", "poetic", "sarcastic"
    background: str
    traits: Optional[dict] = None


class TreePersonalityResponse(BaseModel):
    """Schema for tree personality response."""
    id: int
    tree_id: int
    name: str
    tone: str
    background: str
    traits: Optional[dict]
    voice_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CHAT MESSAGE SCHEMAS ====================
class ChatMessageCreate(BaseModel):
    """Schema for creating chat message."""
    content: str
    include_audio: bool = False  # Generate audio response from tree


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: int
    tree_id: int
    user_id: int
    role: str
    content: str
    audio_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history."""
    tree_id: int
    tree_name: str
    personality: TreePersonalityResponse
    messages: List[ChatMessageResponse]


class InteractionResponse(BaseModel):
    """Schema for tree interaction response."""
    user_message: str
    tree_response: str
    audio_url: Optional[str]
    tree_name: str
    tree_personality: TreePersonalityResponse
