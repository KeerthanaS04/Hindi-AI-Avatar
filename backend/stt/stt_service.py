import whisper
import sys
import sounddevice as sd
from google.cloud import speech
import numpy as np
import queue
import torch
import tempfile
import wave
import os
import time
import io
import google.api_core.exceptions

# Get the root directory of the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))) 

from backend.llm.llm_service import send_to_llm
from backend.tts.tts_service import text_to_speech

# # Set credentials explicitly in Python (Optional if ENV variable is set)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/keert/OneDrive/Desktop/hindi-ai-avatar/coastal-range-450206-q9-d1b9880cbb8f.json"


class LiveSTT:
    def __init__(self, language_code = "hi-IN"):
        """
        Initialize the Google Cloud Speech-To-Text API.
        """
        # print(f"Loading Whisper Model: {model_size}...")
        # self.model = whisper.load_model(model_size)
        self.client = speech.SpeechClient()
        self.language_code = language_code
        
        # Queue to hold audio chunks
        self.audio_queue = queue.Queue()
        
        # Audio Settings
        self.samplerate = 16000  # Whisper expects 16kHz audio
        self.channels = 1
        self.dtype = np.int16  # 16-bit PCM audio
        # self.blocksize = 4096  # Process small chunks
        self.blocksize = int(self.samplerate*3) # 3 seconds of audio (48000 samples)
        # self.max_audio_length = 3 # limit to 3 seconds of audio
        self.client = speech.SpeechClient(client_options={"api_endpoint": "speech.googleapis.com"})
        
    def audio_callback(self, indata, frames, time, status):
        """Callback function to process live audio"""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
        
    def transcribe_live(self):
        """Start live speech-to-text transcription"""
        print("Listening... (Speak in Hindi) 🎤")
        
        with sd.InputStream(
            samplerate = self.samplerate,
            channels = self.channels,
            dtype = self.dtype,
            callback = self.audio_callback,
            blocksize = self.blocksize,
        ):
            try:
                while True:
                    self.process_audio()
            except KeyboardInterrupt:
                print("\nLive Transcription stopped.")
                
    def process_audio(self):
        """Processes queued audio and transcribes it using Google STT"""
        try:
            audio_chunk = self.audio_queue.get(timeout=0.5) # Timeout after 500ms
        except queue.Empty:
            return  # Skip processing if no audio is available
        
        # # Convert to float32 for whisper and normalize audio
        # audio_data = audio_chunk.astype(np.float32) / np.iinfo(np.int16).max
        # audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Convert NumPy array to bytes
        # audio_data = audio_chunk.astype(np.int16).tobytes()
        audio_data = np.frombuffer(audio_chunk, dtype=np.int16).tobytes()
        
        # Prepare audio config for Google STT
        # Create RecognitioAudio object
        # audio = speech.RecognitionAudio(content=audio_data)
        
        # Split into smaller chunks (eg, 512 ms per request)
        chunk_size = int(0.5 * self.samplerate) # 0.5 seconds of audio
        audio_chunks = [audio_data[i:i+chunk_size] for i in range(0, len(audio_data), chunk_size)]
        
        requests = [speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in audio_chunks]
        
        # Configure recognition settings
        config = speech.StreamingRecognitionConfig(
            config = speech.RecognitionConfig(
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz = self.samplerate,
                language_code = self.language_code,
            ),
            interim_results = False, # Allow partial results
            single_utterance = True, # Keep Listening
        )
        
        response = None
        
        # Perform Transcription
        # response = self.client.streaming_recognize(config=config, requests=iter(requests))
        # Retry if Google API returns an error
        for attempt in range(3):  
            try:
                response = self.client.streaming_recognize(config=config, requests=requests)
                break  # Exit loop if successful
            except google.api_core.exceptions.InternalServerError as e:
                print(f"Retrying due to Google API error... (Attempt {attempt+1})")
                time.sleep(1)  # Wait before retrying
                
        # If all retries fail, return early
        if response is None:
            print("Error: Failed to get response from Google STT after multiple retries.")
            return

        
        for result in response:
            for alternative in result.results:
                user_input = alternative.alternatives[0].transcript
                print("You Said:", user_input, flush=True)
            
                if user_input.strip():
                    # Send the transcribed text to LLM
                    ai_response = send_to_llm(user_input)
                    print("AI Response:", ai_response)
            
                    # Convert AI response to speech
                    text_to_speech(ai_response)
            
        # # Save and transcribe
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        #     tmpfile_path = tmpfile.name # Store the filename
        #     tmpfile.close() # Close it to prevent permission issues
            
        #     # Now re-open the file in write mode
        #     with wave.open(tmpfile.name, "wb") as wf:
        #         wf.setnchannels(self.channels)
        #         wf.setsampwidth(2) # 16-bit PCM
        #         wf.setframerate(self.samplerate)
        #         wf.writeframes(audio_chunk.tobytes())
                
        #     # Transcribe using Whisper
        #     result = self.model.transcribe(tmpfile.name, language="hi")
        #     # os.remove(tmpfile_path)
            
        #     user_input = result["text"]
        #     print("You said:", user_input)
            
        #     if user_input.strip():
        #         response = send_to_llm(user_input) # Use LLM service here
        #         print("AI Response:", response)
            
        #     # Convert response to speech
        #     text_to_speech(response)
        # # # Add a small delay to avoid overflow
        # # time.sleep(1) # 100ms delay between processing each chunk
            
        # # Clean up temp file after transcription
        # os.remove(tmpfile_path)
            
if __name__ == "__main__":
    stt = LiveSTT()
    stt.transcribe_live()