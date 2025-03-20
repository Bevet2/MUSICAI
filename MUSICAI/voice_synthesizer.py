import os
from pathlib import Path
import numpy as np
from gtts import gTTS
import pyttsx3
from typing import List, Dict

class VoiceSynthesizer:
    def __init__(self):
        """Initialize voice synthesizer with multiple voice options"""
        self.engine = pyttsx3.init()
        self._setup_voices()
        
    def _setup_voices(self):
        """Setup available voices"""
        self.voices = self.engine.getProperty('voices')
        self.available_voices = {
            'male': [v for v in self.voices if v.gender == 'VoiceGenderMale'],
            'female': [v for v in self.voices if v.gender == 'VoiceGenderFemale']
        }
        
    def get_available_voices(self) -> List[str]:
        """Get list of available voice styles"""
        return ['male_1', 'male_2', 'female_1', 'female_2', 'gtts']
    
    async def generate_vocals(self, lyrics: str, voice_style: str, output_path: str, 
                            tempo: float = 120.0, key: str = "C") -> str:
        """
        Generate vocals from lyrics using specified voice style
        
        Args:
            lyrics: Lyrics to synthesize
            voice_style: Voice style to use
            output_path: Path to save the generated audio
            tempo: Tempo in BPM (only affects pyttsx3 voices)
            key: Musical key (not used in this implementation)
        """
        output_file = Path(output_path) / f"vocals_{voice_style}.wav"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if voice_style == 'gtts':
                # Use Google Text-to-Speech
                tts = gTTS(text=lyrics, lang='en')
                tts.save(str(output_file))
            else:
                # Use pyttsx3
                gender = voice_style.split('_')[0]
                index = int(voice_style.split('_')[1]) - 1
                
                if gender in self.available_voices and index < len(self.available_voices[gender]):
                    voice = self.available_voices[gender][index]
                    self.engine.setProperty('voice', voice.id)
                    
                    # Adjust rate based on tempo
                    rate = int(self.engine.getProperty('rate') * (tempo/120.0))
                    self.engine.setProperty('rate', rate)
                    
                    self.engine.save_to_file(lyrics, str(output_file))
                    self.engine.runAndWait()
                else:
                    raise ValueError(f"Voice style {voice_style} not available")
            
            return str(output_file)
            
        except Exception as e:
            raise Exception(f"Error generating vocals: {str(e)}")
