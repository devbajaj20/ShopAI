"""
Speech-to-Text Processing Module
Handles voice input conversion to text using various speech recognition engines.
"""

from typing import Optional, Dict, Any
import logging

# Make speech recognition optional
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

class SpeechProcessor:
    """Handles speech-to-text conversion with multiple engine support."""
    
    def __init__(self, engine: str = "google"):
        """
        Initialize speech processor.
        
        Args:
            engine: Speech recognition engine ('google', 'sphinx', 'wit')
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Warning: speech_recognition not available. Voice input disabled.")
            self.recognizer = None
            self.microphone = None
            self.engine = None
            self.logger = logging.getLogger(__name__)
            return
            
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        
        # Adjust for ambient noise
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.microphone = None
    
    def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for voice command and convert to text.
        
        Args:
            timeout: Maximum time to wait for speech
            
        Returns:
            Recognized text or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE or not self.microphone:
            print("Speech recognition not available")
            return None
            
        try:
            with self.microphone as source:
                self.logger.info("Listening for command...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Convert speech to text
            text = self._recognize_speech(audio)
            self.logger.info(f"Recognized: {text}")
            return text
            
        except Exception as e:
            self.logger.warning(f"Listening timeout or error: {e}")
            return None
    
    def _recognize_speech(self, audio) -> str:
        """Convert audio to text using selected engine."""
        if self.engine == "google":
            return self.recognizer.recognize_google(audio)
        elif self.engine == "sphinx":
            return self.recognizer.recognize_sphinx(audio)
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")
    
    def process_audio_file(self, file_path: str) -> Optional[str]:
        """
        Process audio file and extract text.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Recognized text or None if failed
        """
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            return self._recognize_speech(audio)
        except Exception as e:
            self.logger.error(f"Audio file processing error: {e}")
            return None