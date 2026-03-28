Study Mate
AI-powered Telegram study assistant for students

Overview

Study Mate is a focused learning assistant that helps students understand lectures, extract insights from course materials, and convert spoken content into structured study notes.

It is designed for practical day-to-day study workflows:
- Ask questions in conversational mode
- Upload slide PDFs and get audio read-aloud
- Upload lecture audio and receive detailed notes
- Optionally attach course PDFs for retrieval-based answers

This is a study assistant, not a general-purpose chatbot.

Problem

Students often struggle with:
- Long lecture recordings that are hard to review quickly
- Dense slide decks that are tiring to read
- Difficulty turning raw audio into clean, structured notes
- Fragmented course materials and weak context recall

As a result:
- Study sessions take longer than necessary
- Important concepts are missed
- Revision quality drops

Solution

A Telegram-based AI assistant that provides:

1. Conversational Study Help

Users can ask:
- "Explain overfitting in simple terms"
- "What is the difference between TCP and UDP?"

Assistant returns:
- Clear, concise explanations
- Step-by-step breakdowns when needed
- Practical examples for understanding

2. Slide Read-Aloud (PDF)

Users upload a slide PDF.
The system:
- Extracts text from the PDF
- Generates audio with TTS
- Sends voice playback in Telegram

3. Audio to Detailed Notes

Users send lecture audio (voice note or audio file).
The system:
- Transcribes audio to text
- Generates detailed, structured notes
- Returns notes with sections such as concepts, explanations, summary, and review questions

4. Course Material Retrieval (Optional)

In conversational mode, users can upload a course PDF with caption as course name.
The system indexes the document and retrieves relevant chunks for context-aware answers.

Target Users

- University and college students
- Learners preparing for exams
- Students revising from lecture recordings

Design Principles

- Clarity over verbosity
- Accuracy over speculation
- Structure over free-form output
- Learning outcomes over generic chat

System Architecture (High-Level)

Input Layer
- Telegram webhook updates (text, voice, audio, document)

Processing Layer
- Mode routing (`/conversational`, `/read_slide`, `/audio_to_notes`, `/course_advising`)
- File download and preprocessing
- Audio conversion to STT-ready WAV
- PDF text extraction for slides

AI Layer
- Groq chat completion for explanations and note generation
- Mode-specific prompting for lecture note formatting

Speech Layer
- Azure STT for audio transcription
- Azure TTS for slide read-aloud and short spoken responses

Retrieval Layer
- External RAG API for ingest/retrieve operations in conversational mode

Output Layer
- Telegram text replies
- Telegram voice replies where applicable

Current Scope

Implemented:
- Telegram webhook bot backend
- Conversational responses with optional retrieval context
- PDF-only slide read-aloud
- Audio-to-notes for voice note and audio upload
- Course PDF ingest for conversational mode

Not yet implemented:
- Slide image OCR
- Multi-part note chunking for very long outputs
- Per-user preferences for note style

Example Interaction

User:
/uploads lecture audio in `/audio_to_notes`

Assistant:
- "Transcribing your lecture audio..."
- "Generating detailed study notes..."
- Returns structured notes text

User:
/uploads slide PDF in `/read_slide`

Assistant:
- "Extracting slide text..."
- Sends voice read-aloud output

Build Direction

Near-term next steps:
- Add long-note splitting to respect Telegram message limits
- Add page-range controls for slide read-aloud
- Add concise vs detailed note style toggle
