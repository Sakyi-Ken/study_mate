import os
import uuid
import asyncio
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from services.telegram import send_text_message, send_long_text_message, send_voice_message, process_voice_note, process_audio_file, get_file_path, download_file
from services.groq_ai import get_study_response
from services.azure_speech import speech_to_text, text_to_speech
from services.rag_api import ingest_document, retrieve_chunks
from services.slide_reader import parse_page_range, extract_text_from_pdf

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
    "/conversational  — Chat with me about any study topic\n"
    "/read_slide      — Send me a slide PDF and I'll read it aloud\n"
    "/audio_to_notes — Send me lecture audio and I'll convert it into detailed notes\n"
    "/course_advising — Get advice on your course or study plan\n"
)

MODE_CONFIRMATIONS = {
    "conversational": "💬 Conversational mode activated. Go ahead, ask me anything! If you want to use customized study materials, please upload a PDF with the course name as the caption.",
    "read_slide": "📖 Read Slide mode activated. Please send me your slide as a PDF document. Optional caption: '2' or '1-3' to read specific pages.",
    "audio_to_notes": "🎙️ Audio to Notes mode activated. Send a voice note or lecture audio file and I'll convert it into detailed, structured notes.",
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
            if current_mode == "read_slide":
                doc = message["document"]
                if doc.get("mime_type", "") != "application/pdf":
                    await send_text_message(chat_id, "For now, please upload slides as a PDF document only.")
                    return

                caption = message.get("caption", "").strip()
                start_page, end_page, page_error = parse_page_range(caption)
                if page_error:
                    await send_text_message(chat_id, f"❌ {page_error}")
                    return

                file_id = doc["file_id"]
                file_name = doc.get("file_name", "slides.pdf")
                await send_text_message(chat_id, f"📥 Receiving '{file_name}'... extracting slide text now.")

                local_path = f"/tmp/{uuid.uuid4().hex}.pdf"
                out_ogg_path = f"/tmp/{uuid.uuid4().hex}_slide.ogg"

                try:
                    tg_file_path = await get_file_path(file_id)
                    await download_file(tg_file_path, local_path)

                    slide_text, total_pages = extract_text_from_pdf(local_path, start_page=start_page, end_page=end_page)
                    if start_page and start_page > total_pages:
                        await send_text_message(chat_id, f"❌ This PDF has only {total_pages} pages. Please choose a valid page range.")
                        return

                    if not slide_text.strip():
                        if start_page and end_page:
                            await send_text_message(chat_id, "❌ I could not extract readable text from the selected pages. Try a different range or a clearer/exported PDF.")
                        else:
                            await send_text_message(chat_id, "❌ I could not extract readable text from this slide PDF. Please try a clearer/exported PDF.")
                        return

                    if start_page and end_page:
                        await send_text_message(chat_id, f"📄 Reading pages {start_page}-{min(end_page, total_pages)} out of {total_pages}.")

                    speech_text = slide_text[:3200]
                    if len(slide_text) > 3200:
                        await send_text_message(chat_id, "📖 The slide is long, so I will read the first part now.")

                    await send_text_message(chat_id, "🔊 Reading your slide aloud...")
                    success = await text_to_speech(speech_text, out_ogg_path)

                    if success:
                        await send_voice_message(chat_id, out_ogg_path)
                    else:
                        await send_text_message(chat_id, "❌ I extracted the slide text, but audio generation failed. Please try again.")
                except Exception as e:
                    logger.error(f"Error processing read_slide PDF: {e}")
                    await send_text_message(chat_id, "❌ Failed to process your slide PDF. Please try again.")
                finally:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    if os.path.exists(out_ogg_path):
                        os.remove(out_ogg_path)
                return

            if current_mode == "audio_to_notes":
                doc = message["document"]
                mime_type = doc.get("mime_type", "")

                if not mime_type.startswith("audio/"):
                    await send_text_message(chat_id, "For audio_to_notes, please upload a lecture audio file or send a voice note.")
                    return

                file_id = doc["file_id"]
                file_name = doc.get("file_name", "lecture_audio")
                file_ext = file_name.split(".")[-1].lower() if "." in file_name else "bin"
                await send_text_message(chat_id, f"🎧 Received '{file_name}'. Transcribing your lecture audio...")

                audio_path = await process_audio_file(file_id, file_ext=file_ext)
                if not audio_path:
                    await send_text_message(chat_id, "❌ I couldn't process that audio file. Please try MP3, M4A, WAV, or OGG.")
                    return

                user_text = await speech_to_text(audio_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)

                if not user_text:
                    await send_text_message(chat_id, "❌ I could not transcribe the lecture audio clearly. Please try a cleaner recording.")
                    return

                await send_text_message(chat_id, "📋 Generating detailed study notes from your lecture audio...")
                ai_response = await get_study_response(user_text, mode=current_mode, context="")
                await send_long_text_message(chat_id, ai_response)
                return

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

            ai_response = await get_study_response(user_text, mode=current_mode, context=context)

            if current_mode == "audio_to_notes":
                await send_long_text_message(chat_id, ai_response)
            else:
                out_ogg_path = f"/tmp/{uuid.uuid4().hex}_out.ogg"
                success = await text_to_speech(ai_response, out_ogg_path)

                if success:
                    await send_voice_message(chat_id, out_ogg_path)
                    await send_text_message(chat_id, ai_response)
                else:
                    await send_text_message(chat_id, ai_response)

                if os.path.exists(out_ogg_path):
                    os.remove(out_ogg_path)

        # 1b. Handle Audio File
        elif "audio" in message:
            if current_mode != "audio_to_notes":
                await send_text_message(chat_id, "Please switch to /audio_to_notes mode to upload lecture audio.")
                return

            audio = message["audio"]
            file_id = audio["file_id"]
            file_name = audio.get("file_name", "lecture_audio")
            file_ext = file_name.split(".")[-1].lower() if "." in file_name else "bin"

            await send_text_message(chat_id, f"🎧 Received '{file_name}'. Transcribing your lecture audio...")

            audio_path = await process_audio_file(file_id, file_ext=file_ext)
            if not audio_path:
                await send_text_message(chat_id, "❌ I couldn't process that audio file. Please try MP3, M4A, WAV, or OGG.")
                return

            user_text = await speech_to_text(audio_path)

            if os.path.exists(audio_path):
                os.remove(audio_path)

            if not user_text:
                await send_text_message(chat_id, "❌ I could not transcribe the lecture audio clearly. Please try a cleaner recording.")
                return

            await send_text_message(chat_id, "📋 Generating detailed study notes from your lecture audio...")
            ai_response = await get_study_response(user_text, mode=current_mode, context="")
            await send_long_text_message(chat_id, ai_response)

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
            ai_response = await get_study_response(user_text, mode=current_mode, context=context)
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
