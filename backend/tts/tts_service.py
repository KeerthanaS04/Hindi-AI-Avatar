import os
from gtts import gTTS
from fastapi.responses import FileResponse
from fastapi import FastAPI
import uuid
import base64
from fastapi import WebSocket
import io
import pygame

import os
import base64
import io
from gtts import gTTS
import pygame
# from phonemizer import phonemize

# def text_to_speech(text, lang="hi"):
#     """
#     Converts AI-generated text into speech using Google TTS (gTTS).
#     """
    
#     if not text:
#         print("⚠️ Warning: Empty text received in text_to_speech()")
#         return None, []

#     if lang is None:
#         print("⚠️ Warning: lang is None, defaulting to 'hi'")
#         lang = "hi"  # Set a default language to prevent NoneType error
        
        
#     try:
#         # Generate speech in memory
#         tts = gTTS(text=text, lang=lang)
#         audio_stream = io.BytesIO()
#         tts.write_to_fp(audio_stream)
#         audio_stream.seek(0)

#         # Convert to base64
#         audio_base64 = base64.b64encode(audio_stream.read()).decode("utf-8")

#         # Placeholder phoneme data
#         phonemes = [
#             {"time": 0, "viseme": "A"},
#             {"time": 500, "viseme": "E"},
#             {"time": 1000, "viseme": "O"},
#         ]

#         # # Play the generated speech
#         # pygame.init()
#         # pygame.mixer.init()
#         # pygame.mixer.music.load(io.BytesIO(base64.b64decode(audio_base64)))
#         # pygame.mixer.music.play()

#         # # Wait for the audio to finish playing
#         # while pygame.mixer.music.get_busy():
#         #     continue

#         # # Clean up
#         # pygame.mixer.quit()
#         # pygame.quit()

#         return audio_base64, phonemes

#     except Exception as e:
#         print(f"Error in TTS: {e}")
#         return None, []

    

def text_to_speech(text, lang="hi"):
    """
    Converts AI-generated text into speech using Google TTS (gTTS).
    """
    try:
        # Generate speech file
        tts = gTTS(text=text, lang=lang)
        audio_file = "output.mp3"
        tts.save(audio_file)
        
        # Play the generated speech
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            continue
        
        # Clean up
        pygame.mixer.quit()
        pygame.quit()
        os.remove(audio_file)
        
    except Exception as e:
        print(f"Error in TTS: {e}")
        