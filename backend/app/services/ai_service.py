"""
AI Service for tree personality and interactions.
Integrates with Google Gemini 2.5 Flash for conversations
and ElevenLabs for realistic text-to-speech audio generation.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

from app.models import TreePersonality, ChatMessage, Tree, User
from app.schemas import TreePersonalityResponse, ChatMessageResponse, InteractionResponse

logger = logging.getLogger(__name__)

# Initialize APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


class TreePersonalityService:
    """Service for managing tree personalities."""
    
    @staticmethod
    def create_personality(
        db: Session,
        tree_id: int,
        name: str,
        tone: str,
        background: str,
        traits: Optional[Dict[str, Any]] = None,
        voice_id: Optional[str] = None
    ) -> TreePersonality:
        """Create or update tree personality."""
        # Check if personality already exists
        existing = db.query(TreePersonality).filter(
            TreePersonality.tree_id == tree_id
        ).first()
        
        if existing:
            existing.name = name
            existing.tone = tone
            existing.background = background
            existing.traits = traits or {}
            existing.voice_id = voice_id
            existing.updated_at = datetime.utcnow()
            db.commit()
            return existing
        
        personality = TreePersonality(
            tree_id=tree_id,
            name=name,
            tone=tone,
            background=background,
            traits=traits or {},
            voice_id=voice_id,
        )
        db.add(personality)
        db.commit()
        db.refresh(personality)
        return personality
    
    @staticmethod
    def get_personality(db: Session, tree_id: int) -> Optional[TreePersonality]:
        """Get tree personality."""
        return db.query(TreePersonality).filter(
            TreePersonality.tree_id == tree_id
        ).first()
    
    @staticmethod
    def build_system_prompt(personality: TreePersonality, tree: Tree) -> str:
        """Build system prompt for Gemini based on tree personality."""
        return f"""You are {personality.name}, a {tree.species} tree with a unique personality.

PERSONALITY TRAITS:
- Name: {personality.name}
- Tone: {personality.tone}
- Background: {personality.background}
- Species: {tree.species}
- Age: {(datetime.utcnow() - tree.planting_date).days} days old
- Health Status: {tree.health_score}% healthy
- Location: {tree.location_name or 'Unknown'}

TRAITS:
{json.dumps(personality.traits, indent=2)}

INSTRUCTIONS:
1. Always stay in character as {personality.name}
2. Respond with a {personality.tone} tone
3. Be creative and entertaining
4. Reference your nature as a {tree.species} tree
5. Make responses concise (2-3 sentences typically)
6. Use emojis where appropriate (🌳🌿🌲🍃☀️💧)

IMPORTANT: Keep responses under 150 words. Be engaging and memorable."""


class AIConversationService:
    """Service for AI conversations with trees."""
    
    @staticmethod
    def get_conversation_history(db: Session, tree_id: int, limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation history."""
        return db.query(ChatMessage).filter(
            ChatMessage.tree_id == tree_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def generate_tree_response(
        db: Session,
        tree_id: int,
        user_message: str,
        include_audio: bool = False
    ) -> Dict[str, Any]:
        """Generate AI response from tree using Gemini 2.5 Flash."""
        try:
            # Get tree and personality
            tree = db.query(Tree).filter(Tree.id == tree_id).first()
            if not tree:
                raise ValueError(f"Tree {tree_id} not found")
            
            personality = TreePersonalityService.get_personality(db, tree_id)
            if not personality:
                raise ValueError(f"No personality set for tree {tree_id}")
            
            # Build system prompt
            system_prompt = TreePersonalityService.build_system_prompt(personality, tree)
            
            # Get recent conversation history for context
            history = AIConversationService.get_conversation_history(db, tree_id, limit=5)
            
            # Build messages for Gemini
            messages = []
            
            # Add conversation history (reversed to chronological order)
            for msg in reversed(history):
                messages.append({
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [msg.content]
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "parts": [user_message]
            })
            
            # Initialize Gemini model
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_prompt
            )
            
            # Generate response
            response = model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=200,
                )
            )
            
            tree_response = response.text.strip()
            
            # Generate audio if requested
            audio_url = None
            if include_audio:
                audio_url = TTSService.generate_speech(
                    text=tree_response,
                    voice_id=personality.voice_id or "Rachel",
                    speed=1.0
                )
            
            return {
                "user_message": user_message,
                "tree_response": tree_response,
                "audio_url": audio_url,
                "tree_name": personality.name,
                "personality": personality
            }
        
        except Exception as e:
            logger.error(f"Error generating tree response: {str(e)}")
            raise
    
    @staticmethod
    def save_message(
        db: Session,
        tree_id: int,
        user_id: int,
        role: str,
        content: str,
        audio_url: Optional[str] = None
    ) -> ChatMessage:
        """Save chat message to database."""
        message = ChatMessage(
            tree_id=tree_id,
            user_id=user_id,
            role=role,
            content=content,
            audio_url=audio_url
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def chat_with_tree(
        db: Session,
        tree_id: int,
        user_id: int,
        user_message: str,
        include_audio: bool = False
    ) -> InteractionResponse:
        """Complete chat interaction: save user message, generate response, save response."""
        # Save user message
        AIConversationService.save_message(
            db=db,
            tree_id=tree_id,
            user_id=user_id,
            role="user",
            content=user_message
        )
        
        # Generate tree response
        response_data = AIConversationService.generate_tree_response(
            db=db,
            tree_id=tree_id,
            user_message=user_message,
            include_audio=include_audio
        )
        
        # Save tree response
        AIConversationService.save_message(
            db=db,
            tree_id=tree_id,
            user_id=user_id,
            role="assistant",
            content=response_data["tree_response"],
            audio_url=response_data["audio_url"]
        )
        
        return InteractionResponse(
            user_message=response_data["user_message"],
            tree_response=response_data["tree_response"],
            audio_url=response_data["audio_url"],
            tree_name=response_data["tree_name"],
            tree_personality=TreePersonalityResponse.from_orm(response_data["personality"])
        )


class TTSService:
    """Service for text-to-speech using ElevenLabs."""
    
    # Available ElevenLabs voices with different characteristics
    AVAILABLE_VOICES = {
        "Rachel": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "description": "Warm, friendly, natural - good for all tones"
        },
        "Bella": {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "description": "Cute, youthful - great for playful/humorous"
        },
        "Clyde": {
            "voice_id": "2EiwWnXFnvU5JabPnXlx",
            "description": "Deep, authoritative - good for wise/educational"
        },
        "Grace": {
            "voice_id": "JZ8chara1Hjw9IUgr9eb",
            "description": "Professional, clear - versatile"
        },
        "River": {
            "voice_id": "SAz9YHcvj6GT2YYXdXnW",
            "description": "Energetic, enthusiastic"
        },
        "Ember": {
            "voice_id": "cgSgspJ2msm6clMCkdW9",
            "description": "Warm and engaging"
        }
    }
    
    @staticmethod
    def get_available_voices() -> Dict[str, Any]:
        """Get list of available voices."""
        return TTSService.AVAILABLE_VOICES
    
    @staticmethod
    def generate_speech(
        text: str,
        voice_id: Optional[str] = None,
        speed: float = 1.0
    ) -> str:
        """Generate speech audio from text using ElevenLabs."""
        try:
            # Use default voice if not specified
            if not voice_id or voice_id not in [v["voice_id"] for v in TTSService.AVAILABLE_VOICES.values()]:
                voice_id = TTSService.AVAILABLE_VOICES["Rachel"]["voice_id"]
            
            # Generate audio
            audio = elevenlabs_client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                ),
                optimize_streaming_latency=4,
            )
            
            # For now, return a placeholder URL
            # In production, you'd upload this to cloud storage (S3, etc.) and return the URL
            # This is a mock implementation - you should implement proper storage
            timestamp = datetime.utcnow().timestamp()
            return f"https://audio.example.com/tree_audio_{timestamp}.mp3"
        
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
    
    @staticmethod
    def select_voice_for_tone(tone: str) -> str:
        """Select appropriate voice based on personality tone."""
        tone_lower = tone.lower()
        
        if tone_lower in ["humorous", "sarcastic", "playful"]:
            return TTSService.AVAILABLE_VOICES["Bella"]["voice_id"]
        elif tone_lower in ["wise", "educational", "scholarly"]:
            return TTSService.AVAILABLE_VOICES["Clyde"]["voice_id"]
        elif tone_lower in ["poetic", "romantic", "artistic"]:
            return TTSService.AVAILABLE_VOICES["Ember"]["voice_id"]
        elif tone_lower in ["energetic", "enthusiastic", "fun"]:
            return TTSService.AVAILABLE_VOICES["River"]["voice_id"]
        else:
            return TTSService.AVAILABLE_VOICES["Rachel"]["voice_id"]


class PublicTreeService:
    """Service for managing public trees and discovery."""
    
    @staticmethod
    def list_public_trees(
        db: Session,
        limit: int = 20,
        offset: int = 0
    ) -> List[Tree]:
        """List all public trees available for interaction."""
        return db.query(Tree).filter(
            Tree.is_public == True,
            Tree.personality_id != None
        ).order_by(Tree.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def set_tree_public(
        db: Session,
        tree_id: int,
        user_id: int,
        is_public: bool
    ) -> Tree:
        """Set tree visibility in public marketplace."""
        tree = db.query(Tree).filter(
            Tree.id == tree_id,
            Tree.user_id == user_id
        ).first()
        
        if not tree:
            raise ValueError("Tree not found or unauthorized")
        
        tree.is_public = is_public
        db.commit()
        db.refresh(tree)
        return tree
