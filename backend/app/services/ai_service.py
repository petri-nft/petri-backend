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
from groq import Groq
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

from app.models import TreePersonality, ChatMessage, Tree, User
from app.schemas import TreePersonalityResponse, ChatMessageResponse, InteractionResponse
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize APIs
GROQ_API_KEY = settings.GROQ_API_KEY
ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    logger.warning("GROQ_API_KEY not configured")
    groq_client = None

if ELEVENLABS_API_KEY:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
else:
    logger.warning("ELEVENLABS_API_KEY not configured")
    elevenlabs_client = None


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
        """Build concise system prompt for Groq LLM with JSON output format."""
        return f"""You are {personality.name}, a {tree.species} tree. Tone: {personality.tone}.
Background: {personality.background}

RESPOND ONLY WITH VALID JSON IN THIS EXACT FORMAT (no markdown, no extra text):
{{"response": "your response here in 1-3 sentences", "emotions": ["emotion1", "emotion2"], "action": "optional action description"}}

Requirements:
- Stay in character as {personality.name} with {personality.tone} tone
- Use emojis sparingly (🌳💧☀️)
- Keep response under 100 words
- Use nature/tree references naturally
- emotions: feelings the tree expresses (e.g. ["joyful", "contemplative", "wise"])
- action: optional physical action (e.g. "rustles leaves", "stretches branches")

RESPOND ONLY WITH JSON. NO OTHER TEXT."""


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
        """Generate AI response from tree using Groq LLM with JSON parsing.
        
        Pipeline:
        1. Build concise prompt: personality + chat history summary + user message
        2. Request Groq to respond with JSON format
        3. Parse JSON response to extract only the "response" field
        4. Send response text to ElevenLabs for voice generation
        5. Return everything to frontend with fallbacks if anything fails
        """
        # Get tree and personality first (before try block so we always have it)
        tree = db.query(Tree).filter(Tree.id == tree_id).first()
        if not tree:
            raise ValueError(f"Tree {tree_id} not found")
        
        personality = TreePersonalityService.get_personality(db, tree_id)
        if not personality:
            raise ValueError(f"No personality set for tree {tree_id}")
        
        try:
            if not groq_client:
                raise ValueError("Groq API not configured")
            
            # Get recent conversation history for context summary
            recent_messages = AIConversationService.get_conversation_history(db, tree_id, limit=2)
            recent_messages.reverse()  # Oldest first
            
            # Build chat history summary (concise)
            history_summary = ""
            if recent_messages:
                history_summary = "\nRecent context: "
                for msg in recent_messages:
                    role = "User" if msg.role == "user" else "Tree"
                    # Truncate long messages
                    content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    history_summary += f"{role}: {content} | "
            
            # Build the full prompt - CONCISE with JSON instructions
            full_prompt = f"""System: You are {personality.name}, a {tree.species} tree with {personality.tone} tone.
{personality.background}{history_summary}

User: {user_message}

Respond ONLY with valid JSON (no markdown, no extra text):
{{"response": "your 1-3 sentence response", "emotions": ["emotion1"], "action": "optional"}}"""

            logger.info(f"Sending to Groq - Tree {tree_id}, Message: {user_message[:50]}...")
            
            # Call Groq API - try multiple models in order of availability
            response = None
            models_to_try = [
                "mixtral-8x7b-32768",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "llama2-70b-4096",
            ]
            
            groq_error = None
            for model in models_to_try:
                try:
                    logger.info(f"Trying Groq model: {model}")
                    response = groq_client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "user",
                                "content": full_prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=200,
                        top_p=0.9,
                    )
                    logger.info(f"Success with model: {model}")
                    break  # Success, exit loop
                except Exception as e:
                    logger.warning(f"Model {model} failed: {str(e)[:100]}")
                    groq_error = e
                    continue
            
            if not response:
                raise Exception(f"All Groq models failed. Last error: {groq_error}")
            
            # Extract response text
            groq_response = response.choices[0].message.content.strip()
            logger.info(f"Groq raw response: {groq_response[:150]}")
            
            # Parse JSON response
            tree_response = None
            try:
                # Try to parse as JSON
                import json
                response_obj = json.loads(groq_response)
                tree_response = response_obj.get("response", "").strip()
                logger.info(f"Parsed JSON response: {tree_response[:100]}")
            except json.JSONDecodeError:
                # If not valid JSON, use the whole response
                logger.warning(f"Could not parse JSON, using raw response")
                tree_response = groq_response.strip()
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            # Use dummy response if Groq fails
            tree_response = None
            
        # Fallback if response is empty or too short
        if not tree_response or len(tree_response) < 5:
            logger.warning(f"Using fallback response for tree {tree_id}")
            tree_response = f"*{personality.name} rustles thoughtfully* That's an interesting thought! 🌳"
        
        logger.info(f"Final response for voice: {tree_response[:100]}")
        
        # Generate audio if requested
        audio_url = None
        if include_audio:
            try:
                logger.info(f"Generating audio with voice: {personality.voice_id}")
                audio_url = TTSService.generate_speech(
                    text=tree_response,
                    voice_id=personality.voice_id or "21m00Tcm4TlvDq8ikWAM",  # Rachel default
                    speed=1.0
                )
                logger.info(f"Audio generated: {audio_url}")
            except Exception as e:
                logger.error(f"Audio generation error: {e}")
                # Use dummy audio URL or just return without audio
                audio_url = None
        
        return {
            "user_message": user_message,
            "tree_response": tree_response,
            "audio_url": audio_url,
            "tree_name": personality.name,
            "personality": personality
        }
    
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
