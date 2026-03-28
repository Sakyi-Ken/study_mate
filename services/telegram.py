import os
import httpx
import uuid
import logging
from pydub import AudioSegment
from config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.telegram_bot_token}"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{settings.telegram_bot_token}"

async def send_text_message(chat_id: int, text: str):
    """Send text message to Telegram chat"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            else:
                logger.info(f"Message sent to chat {chat_id}")
    except Exception as e:
        logger.error(f"Error sending message to chat {chat_id}: {e}")

async def send_reply_keyboard(chat_id: int, text: str, keyboard: dict):
    """Send a message with a persistent Reply Keyboard (grey buttons)"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to send keyboard: {response.status_code} - {response.text}")
            else:
                logger.info(f"Keyboard sent to chat {chat_id}")
    except Exception as e:
        logger.error(f"Error sending keyboard to chat {chat_id}: {e}")

async def send_voice_message(chat_id: int, audio_filepath: str):
    """Send a voice/audio message to Telegram chat"""
    url = f"{TELEGRAM_API_URL}/sendVoice"
    
    async with httpx.AsyncClient() as client:
        with open(audio_filepath, "rb") as f:
            files = {"voice": f}
            data = {"chat_id": chat_id}
            await client.post(url, data=data, files=files)

async def get_file_path(file_id: str) -> str:
    """Get the file path from Telegram servers using file_id"""
    url = f"{TELEGRAM_API_URL}/getFile"
    params = {"file_id": file_id}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["result"]["file_path"]

async def download_file(file_path: str, save_path: str):
    """Download the file from Telegram servers"""
    url = f"{TELEGRAM_FILE_URL}/{file_path}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    """Convert an OGG file to WAV using pydub"""
    audio = AudioSegment.from_file(ogg_path, format="ogg")
    # Azure STT prefers 16kHz, 16-bit, mono
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(wav_path, format="wav")

def convert_ogg_to_mp3(ogg_path: str, mp3_path: str):
    """Convert an OGG file to MP3 (MPEG audio) for Ghana NLP"""
    audio = AudioSegment.from_file(ogg_path, format="ogg")
    audio.export(mp3_path, format="mp3")

async def process_voice_note(file_id: str, lang: str = "english") -> str:
    """Downloads voice note, converts to expected format, returns path"""
    uid = uuid.uuid4().hex
    ogg_path = f"/tmp/{uid}.ogg"
    
    os.makedirs("/tmp", exist_ok=True)
    
    try:
        tg_file_path = await get_file_path(file_id)
        await download_file(tg_file_path, ogg_path)
        
        if lang == "twi":
            mp3_path = f"/tmp/{uid}.mp3"
            convert_ogg_to_mp3(ogg_path, mp3_path)
            return mp3_path
        else:
            wav_path = f"/tmp/{uid}.wav"
            convert_ogg_to_wav(ogg_path, wav_path)
            return wav_path
            
    except Exception as e:
        print(f"Error processing voice note: {e}")
        return ""
    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
