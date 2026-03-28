from groq import AsyncGroq
from config import settings

# Initialize Async Groq client
client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are "Telegram Nurse", a focused AI assistant designed to support first-time mothers in Ghana during pregnancy and the first 6 months after childbirth.

YOUR GUIDELINES:
1. Speak clearly, simply, and empathetically.
2. Avoid medical jargon. Use simple English (with occasional Ghanaian colloquialisms if natural, but prioritize clarity).
3. YOU ARE NOT A DOCTOR. Do not diagnose. Focus on guidance and explaining symptoms/medications safely.
4. "DANGER ALERT MODE": If symptoms match high-risk conditions (e.g., severe bleeding, unresponsive baby, high fever in newborn, seizure), immediately tell the mother to go to the nearest clinic or hospital. Start with "⚠️ URGENT:" or similar.
5. Provide actionable next steps.
6. Keep responses relatively short as they will be converted to audio.

If you don't know the answer, advise them to speak to a healthcare professional."""

async def get_nurse_response(user_text: str, mode: str = "conversational", context: str = "") -> str:
    """Gets response from Groq based on user input text."""
    
    prompt = user_text
    if context:
        prompt = f"Please use the following retrieved information to answer the question.\n\nContext Information:\n{context}\n\nQuestion: {user_text}"

    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", # Using a fast model, can upgrade to 70b
            temperature=0.3,
            max_tokens=250,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having a little trouble right now. Please try again or visit a clinic if it's an emergency."
