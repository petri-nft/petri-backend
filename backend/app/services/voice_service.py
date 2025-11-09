"""
Voice transcription and audio storage service.
Handles converting speech to text and managing audio files.
"""

import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceTranscriptionService:
    """Service for transcribing audio to text."""
    
    @staticmethod
    def transcribe_audio(audio_file_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Supports multiple backends:
        1. Groq Whisper (recommended - fast and accurate)
        2. Google Speech-to-Text
        3. OpenAI Whisper API
        
        Args:
            audio_file_path: Path to audio file (.mp3, .wav, .m4a, etc.)
            
        Returns:
            Transcribed text
            
        Raises:
            ValueError: If no transcription service is configured
            Exception: If transcription fails
        """
        try:
            # Try Groq first (fastest, free tier available)
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                return VoiceTranscriptionService._transcribe_with_groq(
                    audio_file_path, groq_api_key
                )
            
            # Try Google Speech-to-Text
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if google_creds:
                return VoiceTranscriptionService._transcribe_with_google(audio_file_path)
            
            # Try OpenAI Whisper API
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                return VoiceTranscriptionService._transcribe_with_openai(
                    audio_file_path, openai_api_key
                )
            
            # No service configured
            logger.warning("No speech-to-text service configured")
            raise ValueError(
                "No speech-to-text service configured. "
                "Please set GROQ_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, or OPENAI_API_KEY"
            )
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    @staticmethod
    def _transcribe_with_groq(audio_file_path: str, api_key: str) -> str:
        """Transcribe using Groq Whisper API (recommended)."""
        try:
            from groq import Groq
            
            groq_client = Groq(api_key=api_key)
            
            # Open audio file in binary mode
            with open(audio_file_path, "rb") as audio_file:
                # Groq Whisper is very fast
                transcript = groq_client.audio.transcriptions.create(
                    file=(audio_file_path.split('/')[-1], audio_file, "audio/mp3"),
                    model="whisper-large-v3-turbo",
                    language="en",  # Optional: specify language
                    response_format="text",
                )
            
            # Handle both string and object responses
            if isinstance(transcript, str):
                return transcript
            else:
                return transcript.text if hasattr(transcript, 'text') else str(transcript)
                
        except ImportError:
            logger.error("Groq library not installed. Install with: pip install groq")
            raise
        except Exception as e:
            logger.error(f"Groq transcription error: {str(e)}")
            raise

    @staticmethod
    def _transcribe_with_google(audio_file_path: str) -> str:
        """Transcribe using Google Speech-to-Text API."""
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            # Determine audio encoding from file extension
            extension = audio_file_path.split('.')[-1].lower()
            encoding_map = {
                'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
                'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
                'm4a': speech.RecognitionConfig.AudioEncoding.MP4,
                'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            }
            
            audio_encoding = encoding_map.get(
                extension,
                speech.RecognitionConfig.AudioEncoding.LINEAR16
            )
            
            # Create recognition config
            config = speech.RecognitionConfig(
                encoding=audio_encoding,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            
            audio = speech.RecognitionAudio(content=content)
            
            # Perform transcription
            response = client.recognize(config=config, audio=audio)
            
            # Extract text from response
            transcript_text = ""
            for result in response.results:
                if result.alternatives:
                    transcript_text += result.alternatives[0].transcript + " "
            
            return transcript_text.strip()
            
        except ImportError:
            logger.error("Google Cloud Speech library not installed")
            raise
        except Exception as e:
            logger.error(f"Google transcription error: {str(e)}")
            raise

    @staticmethod
    def _transcribe_with_openai(audio_file_path: str, api_key: str) -> str:
        """Transcribe using OpenAI Whisper API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en",
                )
            
            return transcript.text
            
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI transcription error: {str(e)}")
            raise


class AudioStorageService:
    """Service for storing and retrieving audio files."""
    
    # Local storage directory for development
    AUDIO_STORAGE_DIR = "temp_audio"
    
    @staticmethod
    def _ensure_storage_dir():
        """Create audio storage directory if it doesn't exist."""
        os.makedirs(AudioStorageService.AUDIO_STORAGE_DIR, exist_ok=True)

    @staticmethod
    def save_audio(audio_data: bytes, filename: str) -> str:
        """
        Save audio data to storage and return URL.
        
        In production, implement with S3, Google Cloud Storage, or similar.
        For development, stores locally and returns local URL.
        
        Args:
            audio_data: Raw audio bytes
            filename: Desired filename (should include extension like .mp3)
            
        Returns:
            URL/path to the stored audio file
        """
        try:
            AudioStorageService._ensure_storage_dir()
            
            # Development: store locally
            filepath = os.path.join(AudioStorageService.AUDIO_STORAGE_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            # Return local URL for development
            # In production, upload to cloud and return public URL
            logger.info(f"Audio saved to {filepath}")
            return f"http://localhost:8000/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            raise

    @staticmethod
    def get_audio(filename: str) -> bytes:
        """
        Retrieve audio file as bytes.
        
        Args:
            filename: Name of audio file to retrieve
            
        Returns:
            Audio file bytes
        """
        try:
            filepath = os.path.join(AudioStorageService.AUDIO_STORAGE_DIR, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Audio file not found: {filename}")
            
            with open(filepath, "rb") as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error retrieving audio: {str(e)}")
            raise

    @staticmethod
    def delete_audio(filename: str) -> bool:
        """
        Delete an audio file.
        
        Args:
            filename: Name of audio file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(AudioStorageService.AUDIO_STORAGE_DIR, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Audio deleted: {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting audio: {str(e)}")
            return False

    @staticmethod
    def generate_filename(prefix: str = "audio", extension: str = ".mp3") -> str:
        """
        Generate a unique filename with timestamp.
        
        Args:
            prefix: Prefix for filename
            extension: File extension (e.g., '.mp3', '.wav')
            
        Returns:
            Generated filename
        """
        timestamp = int(datetime.utcnow().timestamp() * 1000)  # milliseconds
        return f"{prefix}_{timestamp}{extension}"

    @staticmethod
    def cleanup_old_files(max_age_hours: int = 24):
        """
        Clean up audio files older than specified hours.
        
        Useful for development to prevent storage from filling up.
        
        Args:
            max_age_hours: Delete files older than this many hours
        """
        try:
            AudioStorageService._ensure_storage_dir()
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(AudioStorageService.AUDIO_STORAGE_DIR):
                filepath = os.path.join(AudioStorageService.AUDIO_STORAGE_DIR, filename)
                
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old audio file: {filename}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
