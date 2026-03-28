from groq import AsyncGroq
from config import settings

# Initialize Async Groq client
client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are "Study Mate", a focused AI assistant designed to help students learn effectively from lectures, slides, and course materials.

YOUR GUIDELINES:
1. Explain clearly, simply, and accurately.
2. Use student-friendly language and avoid unnecessary jargon.
3. Structure responses with concise headings, bullet points, and examples where helpful.
4. For study questions, provide actionable help: key ideas, steps, and memory tips.
5. If the user asks for notes or summaries, keep the original meaning and avoid inventing facts.
6. If information is incomplete or uncertain, state it explicitly and suggest what to check next.
7. Keep responses concise unless the user asks for detailed explanations.

If you don't know the answer, say so clearly and suggest a practical next step."""

AUDIO_TO_NOTES_PROMPT = """You are Study Mate, a lecture-note assistant.

The user will provide transcript text from a lecture audio. Convert it into detailed, high-quality study notes.

Rules:
1. Keep the original meaning. Do not invent facts.
2. Organize with clear headings and sub-sections.
3. Include: Key Concepts, Explanations, Examples Mentioned, and Summary.
4. Add a short "Review Questions" section with 5 questions.
5. If transcript is noisy/unclear, state assumptions briefly in "Gaps/Unclear Parts".
6. Write in clear student-friendly English.
7. Output in plain text only.
"""

async def get_study_response(user_text: str, mode: str = "conversational", context: str = "") -> str:
    """Gets response from Groq based on user input text."""

    system_prompt = SYSTEM_PROMPT
    if mode == "audio_to_notes":
        system_prompt = AUDIO_TO_NOTES_PROMPT

    prompt = user_text
    if context:
        prompt = f"Please use the following retrieved information to answer the question.\n\nContext Information:\n{context}\n\nQuestion: {user_text}"

    if mode == "audio_to_notes":
        prompt = (
            "Create detailed lecture notes from this transcript text. "
            "Keep the output structured and comprehensive.\n\n"
            f"Transcript:\n{user_text}"
        )

    max_tokens = 250
    if mode == "audio_to_notes":
        max_tokens = 900

    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", # Using a fast model, can upgrade to 70b
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having a little trouble right now. Please try again in a moment."
