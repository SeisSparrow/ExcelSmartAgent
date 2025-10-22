"""
Audio Processing Module
Handles voice input processing and speech-to-text conversion
"""
from typing import Optional
import io
import logging

# Try to import speech_recognition, make it optional
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None
    logging.warning("speech_recognition not available. Voice input will be disabled.")

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Process audio input and convert to text"""
    
    def __init__(self):
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("AudioProcessor initialized without speech recognition support")
            self.recognizer = None
            return
            
        self.recognizer = sr.Recognizer()
        # Configure recognizer
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def audio_to_text(self, audio_data: bytes, language: str = "zh-CN") -> Optional[str]:
        """
        Convert audio bytes to text using Google Speech Recognition
        
        Args:
            audio_data: Audio data in bytes (WAV format from browser)
            language: Language code (default: zh-CN for Chinese)
            
        Returns:
            Transcribed text or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE or self.recognizer is None:
            logger.error("Speech recognition not available")
            return None
            
        try:
            # Frontend now sends proper WAV format (16000Hz, 16-bit, mono)
            # Parse WAV header to get the actual audio data
            if len(audio_data) < 44:
                logger.error("Audio data too short (no WAV header)")
                return None
            
            # Skip WAV header (44 bytes) and get raw PCM data
            pcm_data = audio_data[44:]
            
            # Create AudioData object with proper parameters
            # Frontend sends: 16000Hz sample rate, 16-bit (2 bytes per sample), mono
            audio = sr.AudioData(pcm_data, sample_rate=16000, sample_width=2)
            
            logger.info(f"Processing audio: {len(audio_data)} bytes total, {len(pcm_data)} bytes PCM data")
            
            # Try Google Speech Recognition (free)
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                logger.info(f"✅ Transcribed successfully: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def audio_file_to_text(self, file_path: str, language: str = "zh-CN") -> Optional[str]:
        """
        Convert audio file to text
        
        Args:
            file_path: Path to audio file
            language: Language code
            
        Returns:
            Transcribed text or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE or self.recognizer is None:
            logger.error("Speech recognition not available")
            return None
            
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                
            text = self.recognizer.recognize_google(audio, language=language)
            logger.info(f"Transcribed from file: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return None
    
    def process_webrtc_audio(self, audio_blob: bytes) -> Optional[str]:
        """
        Process audio from WebRTC (browser recording)
        
        Args:
            audio_blob: Audio blob from browser
            
        Returns:
            Transcribed text
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.error("Speech recognition not available")
            return None
            
        # WebRTC typically sends audio as opus or webm
        # We need to handle conversion if necessary
        return self.audio_to_text(audio_blob)

