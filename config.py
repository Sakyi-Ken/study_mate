from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    telegram_bot_token: str
    groq_api_key: str
    azure_speech_key: str
    azure_stt_key: str
    azure_speech_region: str
    ghana_nlp_api_key_primary: str = ""
    ghana_nlp_api_key_secondary: str = ""
    ghana_nlp_subscription_key: str = ""
    rag_api_base_url: str = "https://pinecone-pipeline.onrender.com"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
