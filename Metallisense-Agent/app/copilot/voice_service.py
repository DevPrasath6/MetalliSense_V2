"""
Voice Services for AI Copilot
Handles Speech-to-Text and Text-to-Speech
"""
import os
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional, Dict
import io

# Speech-to-Text: Groq Whisper API
from groq import Groq

# Text-to-Speech: gTTS (Google Text-to-Speech - Free)
from gtts import gTTS


class VoiceService:
    """
    Voice interaction service for AI Copilot
    
    Features:
    - Speech-to-Text using Groq Whisper
    - Text-to-Speech using gTTS
    - Multiple language support
    - Audio file handling
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice service
        
        Args:
            api_key: Groq API key for Whisper
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("Groq API key required for voice services")
        
        self.client = Groq(api_key=self.api_key)
        self.whisper_model = "whisper-large-v3"
    
    def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: str = "en"
    ) -> Dict[str, str]:
        """
        Convert speech to text using Groq Whisper
        
        Args:
            audio_file: Audio file (WAV, MP3, etc.)
            language: Language code (en, es, fr, etc.)
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            # Use Groq Whisper API
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.whisper_model,
                language=language,
                response_format="json"
            )
            
            return {
                "text": transcription.text,
                "language": language,
                "success": True
            }
            
        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "success": False
            }
    
    def text_to_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> bytes:
        """
        Convert text to speech using gTTS
        
        Args:
            text: Text to convert
            language: Language code
            slow: Speak slowly
            
        Returns:
            MP3 audio bytes
        """
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            # Return empty audio on error
            print(f"TTS Error: {e}")
            return b""
    
    def text_to_speech_file(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        slow: bool = False
    ) -> bool:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert
            output_path: Path to save MP3 file
            language: Language code
            slow: Speak slowly
            
        Returns:
            Success status
        """
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"TTS File Error: {e}")
            return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages for TTS
        
        Returns:
            Dictionary of language codes and names
        """
        return {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "hi": "Hindi",
            "ar": "Arabic"
        }


# Singleton instance
_voice_service_instance = None

def get_voice_service() -> VoiceService:
    """Get or create voice service instance"""
    global _voice_service_instance
    
    if _voice_service_instance is None:
        _voice_service_instance = VoiceService()
    
    return _voice_service_instance
