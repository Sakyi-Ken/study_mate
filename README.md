# Maternal-Nurse AI Assistant

Maternal-Nurse is a Telegram bot powered by generative AI to provide assistance in maternal healthcare. It supports both English and Twi languages, utilizing AI services from Groq, Azure Speech, and Ghana NLP for robust Voice-to-Text and Text-to-Speech capabilities.

## 🚀 Features

- **Multilingual Support:** Communicate in English or Twi via text or voice notes.
- **Voice Capabilities:** Send voice notes and receive comprehensive audio responses.
- **AI-Powered Diagnostics/Advice:** Integrated with Groq AI for fast and reliable medical/maternal advice.

## 🛠️ Prerequisites

Before you start, make sure you have the following installed:
- Python 3.9 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (strictly required for audio conversion via `pydub`)

## ⚙️ Environment Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository_url>
   cd Maternal-Nurse
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

   # Ghana NLP (For Twi STT/TTS)
   ghana_nlp_api_key_primary=your_ghana_nlp_primary_key_here
   ghana_nlp_api_key_secondary=your_ghana_nlp_secondary_key_here
   ghana_nlp_subscription_key=your_ghana_nlp_subscription_key_here
   ```

## 🏃‍♂️ Running the Project

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

## 💬 Usage

- Open Telegram and search for your bot.
- Start a chat.
- Select your preferred language by typing `/english` or `/twi`.
- You can now send text queries or voice notes, and the bot will reply accordingly!
