WhatsApp Nurse
AI-powered maternal & newborn health assistant for first-time mothers in Ghana
📌 Overview

WhatsApp Nurse is a focused AI assistant designed to support first-time mothers in Ghana during pregnancy and the first 6 months after childbirth.

It delivers clear, safe, and culturally relevant health guidance via WhatsApp, helping mothers understand symptoms, make informed decisions, and know when to seek medical care.

This is not a general chatbot — it is a narrow, safety-focused maternal health assistant built for real-world use in low-resource environments.

🎯 Problem

Maternal and newborn care in Ghana faces several challenges:

❌ Limited access to healthcare professionals, especially in rural areas
❌ High reliance on informal advice (friends, family, social media)
❌ Difficulty understanding medical instructions and prescriptions
❌ Delays in recognizing danger signs during pregnancy and early infancy
❌ Language and literacy barriers

As a result:

Preventable complications escalate
Mothers experience anxiety and confusion
Newborn health risks increase
💡 Solution

A WhatsApp-based AI assistant that provides:

1. Symptom Guidance

Users can ask:

“I have lower abdominal pain, is it normal?”
“My baby has a fever, what should I do?”

AI responds with:

Simple explanation
Likely severity (safe vs concerning)
Clear next steps
2. Medication & Instruction Explanation

Users can ask:

“What is this drug for?”
“How should I take this medicine?”

AI:

Translates medical instructions into simple language
Explains purpose and usage safely
3. “Danger Alert Mode” 🚨

If symptoms match high-risk conditions, the system:

Immediately flags urgency

Responds with:

“⚠️ This may be serious. Please go to the nearest clinic or hospital immediately.”

4. Weekly Maternal & Baby Guidance

Proactive messages like:

“At this stage of pregnancy, you may feel…”
“Your baby may start doing this this week…”

Focus:

What is normal
What to watch out for
5. Voice Interaction (Accessibility Feature)
Accepts voice notes
Responds in:
English
Twi (optional extension)
👩🏾‍🍼 Target Users
First-time mothers
Pregnant women
Mothers with newborns (0–6 months)
Especially those:
Outside major cities
With limited medical knowledge
Who primarily use WhatsApp for communication
⚠️ Risks & Mitigation
Risk 1: Unsafe Medical Advice

Mitigation:

Restrict responses to approved maternal health guidelines
Avoid diagnosis — focus on guidance
Use conservative responses when uncertain
Risk 2: Misinformation About Medication

Mitigation:

Only explain commonly used, verified medications

Include disclaimers:

“Follow your nurse or doctor’s instructions first.”

Risk 3: Over-Reliance on AI

Mitigation:

Reinforce that AI is a support tool, not a doctor
Encourage real-world care when needed
Risk 4: Missed Emergency Cases

Mitigation:

Implement Danger Alert Mode
Use symptom keyword + pattern detection
Always err on the side of caution
🧠 Design Principles
Clarity over complexity
Safety over completeness
Guidance over decision-making
Local relevance over global generalization
🏗️ System Architecture (High-Level)
Input Layer
WhatsApp messages (text + voice)
Processing Layer
Speech-to-text (for voice input)
Intent detection (symptoms, medication, general advice)
Context classification (pregnancy vs newborn)
AI Layer
Controlled LLM responses
Prompt constraints based on:
Maternal health guidelines
Safety rules
Safety Layer
Risk detection engine
Emergency trigger system
Output Layer
Simple text responses
Optional voice responses
⚙️ Core Features (MVP)
✅ WhatsApp chatbot integration
✅ Symptom Q&A system
✅ Danger alert detection
✅ Simple language explanations
✅ Basic weekly guidance
🚀 Future Enhancements
🌍 Multi-language support (Twi, Hausa, Ewe)
📍 Location-based hospital recommendations
👩🏾‍⚕️ Human nurse escalation system
📊 Health tracking (symptoms over time)
🧾 Integration with antenatal records
🧪 Example User Interaction

User:

“My baby is not feeding well and feels hot”

AI:

“This may be a sign of fever. Try checking your baby’s temperature if possible.
If your baby is weak, not feeding, or feels very hot, please go to the nearest clinic immediately.”

❤️ Social Impact

This system helps:

Reduce maternal anxiety
Improve early detection of complications
Provide trusted, accessible health information
Bridge the gap between patients and healthcare systems
🧩 Why This Matters

Instead of replacing healthcare professionals, WhatsApp Nurse:

👉 Empowers mothers with understanding
👉 Supports better decisions
👉 Encourages timely medical careQ: What's your starting point for this build session?
A: BACKEND AND WHATSAPP INTEGRATION

Q: For speech-to-speech, which stack do you want to use?
A: WE WILL BE USING SOME AZURE TEXT TO SPEECH AND SPEECH TO TEXT MODELS TO CONVERT USER SPEECH TO TEXT AND THEN PASS TO AN LLM, GET RESPONSE AND THEN PASS BACK TO TTS TO PRODUCE SPEECH. WE'LL DO ENGLISH FOR NOW

Q: Which LLM will power the AI responses?
A: groq api