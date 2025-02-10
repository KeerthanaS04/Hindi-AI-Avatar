from fastapi import FastAPI, WebSocket
import logging
from fastapi.middleware.cors import CORSMiddleware
import json
from backend.tts.tts_service import text_to_speech
# from backend.tts.tts_service import text_to_speech
from backend.avatar.avatar_animation import avatar_animation
import logging
import speech_recognition as sr
import io

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins (replace with your frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"], # Expose headers to support WebSockets
)

@app.get("/")  # This will fix the "Not Found" error
async def root():
    return {"message": "FastAPI WebSocket server is running!"}

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connection Established!")

    recognizer = sr.Recognizer()

    while True:
        try:
            # Receive raw audio bytes
            audio_chunk = await websocket.receive_bytes()
            print(f"📩 Received {len(audio_chunk)} bytes")

            # Convert raw audio to a format usable by SpeechRecognition
            audio_file = io.BytesIO(audio_chunk)
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="hi-IN")  # Convert speech to text
                print(f"🎙️ Recognized Text: {text}")

                # Generate Hindi speech (TTS)
                audio_base64, phonemes = text_to_speech(text, "hi")
                if not audio_base64:
                    await websocket.send_text(json.dumps({"error": "TTS failed"}))
                    continue

                # Send generated speech to frontend
                response = json.dumps({"audio": audio_base64, "phonemes": phonemes})
                await websocket.send_text(response)
                print("✅ Sent TTS Audio & Phonemes")

        except Exception as e:
            print(f"❌ WebSocket Error: {e}")
            await websocket.close() # Ensures the websocket is closed properly
            break

    print("🔴 WebSocket Disconnected")
