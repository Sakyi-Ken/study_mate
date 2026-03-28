# Study Mate Telegram Bot

Study Mate is a Telegram bot powered by Groq and Azure Speech to help students learn faster from lectures and slides.

## Features

- Conversational study assistant for course questions.
- Slide read-aloud mode for PDF slides.
- Audio-to-notes mode for lecture audio and voice notes.
- Optional course PDF ingestion for retrieval-augmented study chat.

## Prerequisites

Before you start, make sure you have the following installed:
- Python 3.9 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (strictly required for audio conversion via `pydub`)

## Environment Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository_url>
   cd study_mate
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and populate it with your API keys:
   ```env
   # Telegram
   telegram_bot_token=your_telegram_bot_token_here

   # Groq AI
   groq_api_key=your_groq_api_key_here

   # Azure Speech (For English STT/TTS)
   azure_speech_key=your_azure_speech_key_here
   azure_stt_key=your_azure_stt_key_here
   azure_speech_region=your_azure_speech_region_here

   # Ghana NLP (optional, for Twi STT/TTS)
   ghana_nlp_api_key_primary=your_ghana_nlp_primary_key_here
   ghana_nlp_api_key_secondary=your_ghana_nlp_secondary_key_here
   ghana_nlp_subscription_key=your_ghana_nlp_subscription_key_here
   ```

## Running the Project

1. **Start the FastAPI Server**:
   Run the application using Uvicorn so it is ready to receive requests:
   ```bash
   uvicorn main:app --reload
   ```

2. **Expose your local server (if developing locally)**:
   You need to expose your local server (running on port 8000) to the internet so Telegram can reach it. If you are using GitHub Codespaces, you can make the port public and use the forwarded URL. Alternatively, use a tool like [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 8000
   ```

3. **Set up the Telegram Webhook**:
   Once you have your public base URL (e.g., `https://your-ngrok-url.ngrok-free.app` or your Codespaces URL), run the webhook configuration script. 
   
   **Important:** Only provide the base URL! The `set_webhook.py` script automatically appends the `/webhook` path for you. Do not add `/webhook` to the end of your URL.
   ```bash
   python set_webhook.py <your_public_base_url>
   ```

   The bot should now be actively listening to your webhook endpoints!

## Usage

- Open Telegram and search for your bot.
- Start a chat and run `/start`.
- Select a mode:
   - `/conversational` for course chat
   - `/read_slide` to upload a slide PDF and get voice read-aloud
   - `/audio_to_notes` to upload lecture audio and receive detailed notes
   - `/course_advising` for study planning help

## Notes

- In `/read_slide`, only PDF documents are currently supported.
- In `/audio_to_notes`, both Telegram voice notes and audio files are supported.
- For RAG in `/conversational`, upload course PDF with caption as course name.
