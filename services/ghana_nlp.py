import httpx
from config import settings
import os

GHANA_NLP_API_URL = "https://translation-api.ghananlp.org"
SUBSCRIPTION_KEY = settings.ghana_nlp_subscription_key

async def speech_to_text_twi(audio_filepath: str) -> str:
    """
    Transcribes Twi audio to text using Ghana NLP ASR v2.
    """
    url = f"{GHANA_NLP_API_URL}/asr/v2/transcribe?language=tw"
    
    headers = {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    
    try:
        with open(audio_filepath, "rb") as f:
            audio_data = f.read()
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, content=audio_data)
            
            response.raise_for_status()
            
            # The API might return plain text or JSON. For safety:
            try:
                data = response.json()
                # Guessing typical schema: {"transcription": "..."} or {"text": "..."}
                # If it's plain text, json() will fail
                return data.get("text") or data.get("transcription", response.text)
            except:
                return response.text
                
    except Exception as e:
        print(f"Error in Ghana NLP STT: {e}")
        return ""

async def text_to_speech_twi(text: str, output_filepath: str) -> bool:
    """
    Synthesizes text to Twi audio using Ghana NLP TTS v1.
    """
    url = f"{GHANA_NLP_API_URL}/tts/v1/synthesize"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    
    payload = {
        "text": text,
        "language": "tw",
        "speaker_id": "twi_speaker_4"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            with open(output_filepath, "wb") as f:
                f.write(response.content)
            return True
                
    except Exception as e:
        print(f"Error in Ghana NLP TTS: {e}")
        return False

