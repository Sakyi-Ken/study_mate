import os
import asyncio
import httpx
from config import settings

async def setup_webhook(url: str):
    telegram_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/setWebhook"
    async with httpx.AsyncClient() as client:
        response = await client.post(telegram_url, json={"url": f"{url}/webhook"})
        print(response.json())

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python set_webhook.py <your_ngrok_url>")
        sys.exit(1)
    
    webhook_url = sys.argv[1].rstrip("/")
    asyncio.run(setup_webhook(webhook_url))
