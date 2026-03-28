import os
import uuid
import asyncio
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from services.telegram import send_text_message, send_voice_message, process_voice_note, get_file_path, download_file
from services.groq_ai import get_nurse_response
from services.azure_speech import speech_to_text, text_to_speech
from services.rag_api import ingest_document, retrieve_chunks

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Track the current mode per user
user_modes = {}
user_courses = {}

WELCOME_MSG = (
    "Hello! I am your Study Mate. I help you study better \n\n"
    "Please choose a mode to get started:\n\n"
    "/conversational  — Chat with me about any health concern\n"
    "/read_slide      — Send me a slide and I'll read it for you\n"
    "/audio_to_notes — Send me a voice note and I'll convert it into clean, structured notes\n"
    "/course_advising — Get advice on your course or study plan\n"
)

MODE_CONFIRMATIONS = {
    "conversational": "💬 Conversational mode activated. Go ahead, ask me anything! If you want to use customized study materials, please upload a PDF with the course name as the caption.",
    "read_slide": "📖 Read Slide mode activated. Please send me your slide (image or file).",
    "/audio_to_notes": "🎙️ Audio to Notes mode activated. Send me a voice note and I'll convert it into clean, structured notes.",
    "course_advising": "📚 Course Advising mode activated. Tell me about your course or what you need help with.",
}

SLASH_COMMANDS = {
    "/conversational": "conversational",
    "/read_slide": "read_slide",
    "/audio_to_notes" : "audio_to_notes",
    "/course_advising": "course_advising",
}


async def handle_update(update: dict):
    try:
        if "message" not in update:
            logger.debug("Update has no message field")
            return

        message = update["message"]
        chat_id = message["chat"]["id"]
        logger.info(f"Received update from chat {chat_id}")

        current_mode = user_modes.get(chat_id, None)

        if "document" in message:
            if current_mode != "conversational":
                 await send_text_message(chat_id, "Please switch to /conversational mode to upload course documents.")
                 return

            doc = message["document"]
            caption = message.get("caption", "").strip()

            if not caption:
                await send_text_message(chat_id, "Please upload the document again with a caption containing the course name (e.g., 'Bio101').")
                return

            if doc.get("mime_type", "") != "application/pdf":
                await send_text_message(chat_id, "Sorry, I only accept PDF documents for now.")
                return

            file_id = doc["file_id"]
            file_name = doc.get('file_name', 'document.pdf')
            await send_text_message(chat_id, f"📥 Receiving '{file_name}' for course '{caption}'... This might take a moment.")

            local_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            try:
                tg_file_path = await get_file_path(file_id)
                await download_file(tg_file_path, local_path)
                
                # Ingest document
                await ingest_document(local_path, namespace=caption)
                user_courses[chat_id] = caption
                await send_text_message(chat_id, f"✅ Successfully ingested '{file_name}' under course '{caption}'. You can now ask questions about it!")
            except Exception as e:
                logger.error(f"Error ingesting document: {e}")
                await send_text_message(chat_id, "❌ Failed to process the document. Please ensure the backend is running and try again.")
            finally:
                if os.path.exists(local_path):
                    os.remove(local_path)
            return

        # 1. Handle Voice Note
        elif "voice" in message:
            if not current_mode:
                await send_text_message(chat_id, "Please select a mode first:\n\n" + WELCOME_MSG)
                return

            file_id = message["voice"]["file_id"]
            await send_text_message(chat_id, "🎙️ Listening to your message...")

            audio_path = await process_voice_note(file_id)
            if not audio_path:
                await send_text_message(chat_id, "Sorry, I couldn't process your audio. Could you try typing or sending it again?")
                return

            user_text = await speech_to_text(audio_path)

            if os.path.exists(audio_path):
                os.remove(audio_path)

            if not user_text:
                await send_text_message(chat_id, "I couldn't hear you clearly. Could you repeat that or type it?")
                return

            await send_text_message(chat_id, f"📝 You said: '{user_text}'")
            
            # In audio_to_notes mode, let the user know notes are being generated
            if current_mode == "audio_to_notes":
                await send_text_message(chat_id, "📋 Generating your notes...")

            # Context retrieval
            context = ""
            if current_mode == "conversational" and chat_id in user_courses:
                course = user_courses[chat_id]
                try:
                    context = await retrieve_chunks(user_text, namespace=course)
                except Exception as e:
                    logger.error(f"Error retrieving context for voice message: {e}")

            ai_response = await get_nurse_response(user_text, mode=current_mode, context=context)

            out_ogg_path = f"/tmp/{uuid.uuid4().hex}_out.ogg"
            success = await text_to_speech(ai_response, out_ogg_path)

            if success:
                await send_voice_message(chat_id, out_ogg_path)
                await send_text_message(chat_id, ai_response)
            else:
                await send_text_message(chat_id, ai_response)

            if os.path.exists(out_ogg_path):
                os.remove(out_ogg_path)

        # 2. Handle Text Message
        elif "text" in message:
            user_text = message["text"]

            # /start command
            if user_text == "/start":
                await send_text_message(chat_id, WELCOME_MSG)
                return

            # Mode selection commands
            if user_text in SLASH_COMMANDS:
                selected_mode = SLASH_COMMANDS[user_text]
                user_modes[chat_id] = selected_mode
                await send_text_message(chat_id, MODE_CONFIRMATIONS[selected_mode])
                return

            # Guard: no mode selected yet
            if not current_mode:
                await send_text_message(chat_id, "Please select a mode first:\n\n" + WELCOME_MSG)
                return

            # Context retrieval
            context = ""
            if current_mode == "conversational" and chat_id in user_courses:
                course = user_courses[chat_id]
                try:
                    context = await retrieve_chunks(user_text, namespace=course)
                except Exception as e:
                    logger.error(f"Error retrieving context for text message: {e}")

            # Pass mode context to AI
            ai_response = await get_nurse_response(user_text, mode=current_mode, context=context)
            await send_text_message(chat_id, ai_response)

    except Exception as e:
        logger.error(f"Error in handle_update: {e}", exc_info=True)
        try:
            await send_text_message(chat_id, "Sorry, something went wrong. Please try again.")
        except:
            logger.error(f"Failed to send error message to chat {chat_id}")


@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint that Telegram will hit with updates.
    We process them in the background to return 200 OK fast.
    """
    try:
        update = await request.json()
        logger.info(f"Received webhook update: {update}")
    except Exception as e:
        logger.error(f"Failed to parse webhook JSON: {e}")
        return {"status": "error", "message": "Invalid JSON body"}

    background_tasks.add_task(handle_update, update)
    return {"status": "ok"}

@app.get("/")
def health_check():
    return {"status": "ok"}
