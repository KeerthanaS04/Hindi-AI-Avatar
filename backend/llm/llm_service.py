import os
import requests
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# DeepSeek API Config
# API_URL = "https://api.deepseek.com/v1/chat/completions" # Update if needed
# OpenAI API Config
# API_KEY = os.getenv("OPENAI_API_KEY")  # Ensure the environment variable is set
# Together.ai API Config
API_URL = "https://api.together.xyz/v1/chat/completions"
API_KEY = os.getenv("TOGETHER_AI_KEY")  # Set this in your .env file

# # Set your OpenAI API key
# openai.api_key = API_KEY

def send_to_llm(user_text):
    """
    Sends user input to the LLaMA 3 API (via Together.ai) and returns the response.
    """
    if not API_KEY:
        raise ValueError("API key is missing")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": [{"role": "user", "content": user_text}],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} {response.reason}"
    
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"