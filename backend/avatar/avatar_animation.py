import json
from fastapi import WebSocket
from backend.tts.tts_service import text_to_speech # Ensure this generates viseme/phoneme data

class AvatarAnimation:
    def __init__(self):
        self.clients = []
        
    async def connect(self, websocket: WebSocket):
        # await websocket.accept()
        self.clients.append(websocket)
        
    async def send_animation_data(self, text):
        """ Generate speech and send animation data to the frontend """
        audio_base64, phoneme_data = await text_to_speech(text, None)
        
        # Send response with audio URL and phonemes for lip-sync
        data = {"audio": audio_base64, "phonemes": phoneme_data}
        for client in self.clients:
            await client.send_text(json.dumps(data))
            
avatar_animation = AvatarAnimation()