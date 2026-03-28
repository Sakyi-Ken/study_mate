import os
import asyncio
import azure.cognitiveservices.speech as speechsdk
from config import settings

# Usually the same key is used for both if they are the same resource type, but we handle just in case
speech_config = speechsdk.SpeechConfig(
    subscription=settings.azure_speech_key, 
    region=settings.azure_speech_region
)

# Choose a natural sounding English voice (we can pick a Nigerian/Kenyan/South African English voice for localized feel)
# E.g. en-NG-EzinneNeural, en-KE-AsyaNeural, en-TZ-ImaniNeural
speech_config.speech_synthesis_voice_name = "en-NG-EzinneNeural"
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Ogg48Khz16BitMonoOpus)

def synthesize_speech(text: str, output_filepath: str) -> bool:
    """Synchronous function to synthesize speech to a file."""
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filepath)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return True
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonErrorDetails)
        print(f"Speech synthesis canceled: {cancellation_details}")
        return False

async def text_to_speech(text: str, output_filepath: str) -> bool:
    """Async wrapper for TTS"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, synthesize_speech, text, output_filepath)


def recognize_speech_from_file(filepath: str) -> str:
    """Synchronous function to recognize speech from a WAV file."""
    stt_config = speechsdk.SpeechConfig(
        subscription=settings.azure_stt_key, 
        region=settings.azure_speech_region
    )
    # Using default English but could configure "en-GH" if Azure supports it, otherwise en-NG / en-US
    stt_config.speech_recognition_language = "en-NG" 
    
    audio_config = speechsdk.audio.AudioConfig(filename=filepath)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=stt_config, audio_config=audio_config)
    
    result = speech_recognizer.recognize_once_async().get()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    elif result.reason == speechsdk.ResultReason.Canceled:
        print(f"Speech recognition canceled: {result.cancellation_details}")
        return ""
    return ""

async def speech_to_text(filepath: str) -> str:
    """Async wrapper for STT"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, recognize_speech_from_file, filepath)
