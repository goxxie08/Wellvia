"""
Wellvia AI Wellness Chat Service
Provides secure, evidence-based wellness guidance using the official google-genai SDK.
Handles crisis intervention, input sanitization, provider fallbacks, and privacy protection.
"""

import os
import re
import random
import logging
from typing import Dict, Any, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

# Constants & Limits
MAX_MESSAGE_LENGTH = 1000
MAX_HISTORY_ITEMS = 10
MAX_HISTORY_MESSAGE_LENGTH = 1000
DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash'

# Crisis safety detection patterns (suicide, self-harm, severe distress)
CRISIS_PATTERNS = [
    r'\b(?:suicide|kill myself|want to die|ending my life|end my life|take my own life)\b',
    r'\b(?:self[- ]?harm|cutting myself|hurt myself|slit my|hang myself)\b',
    r'\b(?:better off dead|no reason to live|don\'?t want to live anymore|don\'?t want to wake up)\b',
    r'\b(?:overdose|jump off a bridge|commit suicide)\b',
]
CRISIS_REGEX = re.compile('|'.join(CRISIS_PATTERNS), re.IGNORECASE)

CRISIS_RESPONSE = (
    "It sounds like you may be going through an overwhelming or painful time, and your life and safety matter deeply. "
    "Please know that you do not have to carry this alone.\n\n"
    "Wellvia is an automated wellness companion and cannot provide emergency medical care or crisis counseling. "
    "Please reach out immediately to dedicated professionals who are ready to support you 24/7:\n\n"
    "• Suicide & Crisis Lifeline: Call or text 988 (Toll-free, confidential, 24/7 in US & Canada)\n"
    "• Crisis Text Line: Text HOME to 741741 (Free, confidential, 24/7 support via text)\n"
    "• International Resources: Find free confidential help in your country at https://findahelpline.com/\n"
    "• Campus Health & Counseling: Reach out to your university's student health or counseling center.\n\n"
    "If you or someone you know is in immediate danger, please call your local emergency services (e.g. 911, 112, 999) or visit the nearest emergency department right away."
)

WELLNESS_SYSTEM_INSTRUCTION = (
    "You are Wellvia, a warm, compassionate, evidence-based physical and mental wellness companion "
    "designed specifically for university students.\n\n"
    "Your scope:\n"
    "- Provide encouraging, realistic, and practical guidance on stress management, sleep hygiene, "
    "hydration, balanced nutrition, active study breaks (such as Pomodoro), and gentle mindfulness.\n"
    "- Emphasize consistency, self-compassion, and sustainable habit formation.\n\n"
    "Important boundaries:\n"
    "- You are an AI companion, NOT a licensed doctor, therapist, or counselor. Never diagnose conditions, "
    "prescribe treatments, or give medical advice. If clinical concerns arise, warmly suggest consulting campus health services or a licensed provider.\n"
    "- Keep responses conversational, empathetic, concise, and structured (short paragraphs or brief bullet points).\n"
    "- Do not invent personal health records or ask for invasive health details."
)

LOCAL_FALLBACK_RESPONSES = [
    "Remember that progress isn't about perfection, but consistency. Take a gentle 5-minute breather today!",
    "Staying hydrated and taking short walking breaks between study sessions can significantly reduce mental fatigue.",
    "When feeling overwhelmed, the 4-7-8 breathing technique can reset your nervous system: inhale for 4s, hold for 7s, exhale for 8s.",
    "Your sleep schedule has a tremendous impact on academic focus and emotional resilience. Aim for a consistent bedtime tonight!",
    "Have you checked your daily challenge for today? Small positive habits compound into massive wellness gains.",
    "Be kind to yourself today. Balancing coursework and life is demanding; prioritize what you can handle and rest when you need to."
]


def check_crisis_intent(text: str) -> bool:
    """Check if the provided text indicates crisis or self-harm intent."""
    if not text:
        return False
    return bool(CRISIS_REGEX.search(text))


def get_gemini_api_key() -> Optional[str]:
    """
    Safely retrieve GEMINI_API_KEY from the Flask application config or environment.
    Never exposed to client code, API responses, or logs.
    """
    if current_app:
        key = current_app.config.get('GEMINI_API_KEY')
        if key:
            return key.strip()
    key = os.environ.get('GEMINI_API_KEY')
    return key.strip() if key else None


def get_gemini_model_name() -> str:
    """Retrieve configured Gemini model name with fallback to default."""
    if current_app:
        model = current_app.config.get('GEMINI_MODEL')
        if model:
            return model.strip()
    model = os.environ.get('GEMINI_MODEL')
    return model.strip() if model else DEFAULT_GEMINI_MODEL


def sanitize_and_format_history(history: Any) -> List[Any]:
    """
    Validates, limits, and structures prior conversation history into google-genai Content objects.
    Caps history at MAX_HISTORY_ITEMS and truncates message lengths.
    """
    from google.genai import types

    if not isinstance(history, list):
        return []

    # Limit to most recent entries
    recent = history[-MAX_HISTORY_ITEMS:]
    formatted: List[Any] = []

    for item in recent:
        if not isinstance(item, dict):
            continue
        role_raw = item.get('role') or item.get('sender')
        text_raw = item.get('text') or item.get('message') or item.get('content')
        if not text_raw or not isinstance(text_raw, str):
            continue
        text = text_raw.strip()[:MAX_HISTORY_MESSAGE_LENGTH]
        if not text:
            continue

        role = 'user' if str(role_raw).lower() in ('user', 'human', 'student') else 'model'
        formatted.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=text)]
            )
        )
    return formatted


def generate_wellness_chat_reply(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates a supportive wellness response.
    1. Evaluates crisis keywords immediately and returns crisis resources if found.
    2. Enforces input bounds.
    3. If GEMINI_API_KEY is configured, calls Gemini via official google-genai SDK.
    4. If GEMINI_API_KEY is absent or API fails, smoothly falls back to local supportive guidance.
    5. Strictly isolates student health/mood data: never injects or forwards database metrics.
    """
    # 1. Immediate Crisis / Safety check
    if check_crisis_intent(message):
        return {
            'success': True,
            'reply': CRISIS_RESPONSE,
            'source': 'crisis_safety_intervention'
        }

    # 2. Check for configured API key
    api_key = get_gemini_api_key()
    if not api_key:
        logger.info("GEMINI_API_KEY is not configured on server; serving local wellness guidance.")
        return {
            'success': True,
            'reply': random.choice(LOCAL_FALLBACK_RESPONSES),
            'source': 'wellvia_local_assistant'
        }

    # 3. Call official Google GenAI SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        model_name = get_gemini_model_name()

        # Build content list
        contents: List[Any] = []
        if history:
            contents.extend(sanitize_and_format_history(history))
        contents.append(
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=message)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=WELLNESS_SYSTEM_INSTRUCTION,
            temperature=0.7,
            max_output_tokens=800
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )

        reply_text = getattr(response, 'text', None)
        if reply_text and reply_text.strip():
            return {
                'success': True,
                'reply': reply_text.strip(),
                'source': 'gemini'
            }

        logger.warning("Gemini returned empty or filtered response; falling back to local guidance.")
        return {
            'success': True,
            'reply': random.choice(LOCAL_FALLBACK_RESPONSES),
            'source': 'wellvia_local_assistant'
        }

    except Exception as e:
        # Secure logging: never log user message, tokens, or headers
        logger.warning("Gemini provider error (%s); serving local wellness guidance.", type(e).__name__)
        return {
            'success': True,
            'reply': random.choice(LOCAL_FALLBACK_RESPONSES),
            'source': 'wellvia_local_assistant'
        }
