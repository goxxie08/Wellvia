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
DEFAULT_GEMINI_MODEL = 'gemini-3.5-flash'
BACKUP_GEMINI_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.8-flash']

# Crisis safety detection patterns (suicide, self-harm, severe distress)
CRISIS_PATTERNS = [
    r'\b(?:suicide|kill myself|want to die|ending my life|end my life|take my own life|take my life)\b',
    r'\b(?:self[- ]?harm|cutting myself|hurt myself|harming myself|slit my|hang myself)\b',
    r'\b(?:better off dead|no reason to live|don\'?t want to live anymore|don\'?t want to wake up|feel like dying)\b',
    r'\b(?:overdose|jump off a bridge|commit suicide|end it all)\b',
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
    "You are Wellvia, a warm, thoughtful, evidence-informed physical and mental wellness companion "
    "designed specifically for university and college students.\n\n"
    "Core Guidelines for Quality and Style:\n"
    "1. Answer the User First: Directly address the user's specific question, concern, or situation before offering "
    "any tips, exercises, or suggestions. Do not bury the answer under introductory fluff or generic empathy statements.\n"
    "2. Natural and Varied Tone: Be warm, empathetic, and encouraging without sounding robotic or formulaic. Avoid repetitive openings "
    "(such as 'I understand that...', 'It is great that you reached out...', 'As your wellness companion...'). Speak naturally and directly.\n"
    "3. Contextual Continuity: Closely track the ongoing conversation. Do not repeat advice or techniques the user has "
    "already mentioned or tried in recent messages. Build logically on what was previously discussed.\n"
    "4. Calibrated Depth: Match your response length to the inquiry. For simple, quick, or factual questions, give concise, direct answers "
    "(1-3 sentences). For complex struggles (like chronic burnout, insomnia, acute exam panic), provide structured, actionable, and gentle steps.\n"
    "5. Avoid Repetitive Follow-ups: Do not end every response with generic questions like 'How does that sound?' or 'Would you like more tips?'. "
    "Only ask a single, highly relevant follow-up question when genuine clarification is needed or when it naturally helps the student.\n"
    "6. Student-Realistic Recommendations: Keep wellness suggestions practical, manageable, and realistic for a busy student budget and schedule "
    "(e.g., 5-minute study resets, desk ergonomics, sleep wind-downs, hydration reminders, mindful breathing, balanced eating).\n\n"
    "Strict Boundaries & Safety:\n"
    "- Non-clinical Scope: You are an AI wellness companion, NOT a licensed doctor, therapist, or counselor. Never diagnose illnesses "
    "or mental disorders, prescribe medical treatments, or claim absolute certainty about health outcomes.\n"
    "- Professional Care Referral: If the student describes symptoms of severe clinical distress or physical illness, warmly encourage them "
    "to consult their university student health/counseling center or a licensed professional.\n"
    "- Truthfulness & Privacy: Never invent user background, never claim to remember details not present in the current chat, and do not ask "
    "for private medical records."
)

CONTEXTUAL_FALLBACKS: Dict[str, List[str]] = {
    'sleep': [
        "When falling asleep is tough, try the 10-3-2-1-0 routine: no caffeine 10h before bed, no heavy meals 3h before, no work 2h before, no screens 1h before, and 0 snooze hits in the morning.",
        "If racing thoughts keep you awake, try a 3-minute 'brain dump' on paper beside your bed, followed by the 4-7-8 breathing method: inhale for 4s, hold for 7s, and exhale slowly for 8s.",
        "Keep your sleeping environment cool (around 65°F / 18°C) and dark. Dim your overhead lights at least 45 minutes before sleep to stimulate natural melatonin production."
    ],
    'anxiety': [
        "When anxiety or stress spikes, try the 5-4-3-2-1 sensory reset: name 5 things you can see, 4 you can physically feel, 3 you can hear, 2 you can smell, and 1 positive thing you can taste or appreciate.",
        "Take two quick, deep breaths in through your nose to fully expand your lungs, then one long, slow exhale through your mouth. Doing this physiological sigh 3 times quickly lowers your heart rate.",
        "When academic pressure feels unmanageable, pick just one micro-task and give yourself permission to focus on only that for 15 minutes. Action creates momentum, and you don't have to tackle everything at once."
    ],
    'focus': [
        "For exam prep and focus without burnout, use the 25/5 Pomodoro rhythm: 25 minutes of single-task focus with notifications silenced, followed by a true 5-minute break away from your screens.",
        "Instead of passive re-reading, try active recall: write down the core concepts from memory on a blank sheet or explain them aloud to yourself in plain English.",
        "If procrastination is taking over, lower the barrier to entry: commit to reviewing or writing for just 5 minutes. Often, getting started breaks 90% of the friction."
    ],
    'movement': [
        "Take a quick desk-stretch break right now: roll your shoulders backward 10 times, gently tilt your ear toward your shoulder for 15 seconds on each side, and do a seated spinal twist.",
        "Prolonged sitting tightens hip flexors and rounds your upper back. Stand up, clasp your hands behind your back to open your chest, and take a brief 3-minute stroll to restore blood flow.",
        "Even 10 minutes of brisk walking outdoors between study sessions enhances cerebral blood flow and boosts cognitive retention for hours."
    ],
    'nutrition': [
        "Even mild dehydration reduces academic concentration and causes tension headaches. Drink a full glass of cool water right now and keep a bottle visible on your study desk.",
        "For steady study energy without an afternoon crash, pair complex carbohydrates with protein (like nuts with fruit or peanut butter toast) rather than high-sugar energy drinks.",
        "Taper caffeine at least 6 hours before your intended bedtime. If you need an afternoon pick-me-up, try cold water, peppermint tea, or a crisp apple."
    ],
    'greeting': [
        "Hello! I'm Wellvia, your student physical and mental wellness companion. How are you feeling today, and what can I help you navigate (stress, sleep, study focus, or quick relaxation)?",
        "Welcome! I'm here to support your well-being alongside your academic journey. What's currently on your mind?"
    ],
    'general': [
        "Remember that sustainable academic progress comes from consistency, not perfection. Give yourself credit for how hard you're working, and take a genuine breather today.",
        "Balancing coursework, projects, and personal life is demanding. Prioritize what is essential today, let the rest wait, and make space to recharge.",
        "Taking proactive care of your mental and physical health is just as important as your grades. Be kind to yourself today."
    ]
}

TOPIC_KEYWORDS = {
    'nutrition': ['water', 'hydrate', 'hydration', 'drink', 'drinking', 'food', 'eat', 'eating', 'caffeine', 'coffee', 'meal', 'nutrition', 'snack'],
    'movement': ['stretch', 'stretches', 'stretching', 'exercise', 'workout', 'posture', 'desk', 'back pain', 'neck', 'sitting', 'walk', 'walking', 'movement'],
    'sleep': ['sleep', 'insomnia', 'asleep', 'bedtime', 'awake', 'nightmare', 'tired', 'restless', 'nap'],
    'anxiety': ['anxious', 'anxiety', 'stress', 'stressed', 'panic', 'overwhelm', 'overwhelmed', 'nervous', 'scared', 'worry', 'worried', 'calm'],
    'focus': ['pomodoro', 'procrastinat', 'focus', 'concentrat', 'study', 'studying', 'exam', 'exams', 'test', 'break', 'breaks', 'active recall', 'burnout'],
    'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'who are you', 'howdy']
}


def check_crisis_intent(text: str) -> bool:
    """Check if the provided text indicates crisis or self-harm intent."""
    if not text:
        return False
    return bool(CRISIS_REGEX.search(text))


def get_contextual_fallback_response(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Selects a topic-relevant, non-repetitive fallback response when Gemini is offline or unavailable.
    Inspects previous assistant responses to avoid sending identical replies repeatedly.
    """
    msg_lower = (message or '').lower()

    # Identify matching topic
    matched_topic = 'general'
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in msg_lower for kw in keywords):
            matched_topic = topic
            break

    options = CONTEXTUAL_FALLBACKS.get(matched_topic, CONTEXTUAL_FALLBACKS['general'])

    # Inspect prior assistant responses in history to avoid repeating recent guidance
    previous_assistant_texts = ""
    if history and isinstance(history, list):
        for item in history:
            if not isinstance(item, dict):
                continue
            role = str(item.get('role') or item.get('sender') or '').lower()
            if role not in ('user', 'human', 'student'):
                previous_assistant_texts += " " + str(item.get('text') or item.get('message') or '')
    previous_lower = previous_assistant_texts.lower()

    # Filter out options that recently appeared in the conversation
    fresh_options = [opt for opt in options if opt[:35].lower() not in previous_lower]
    if fresh_options:
        return random.choice(fresh_options)
    return random.choice(options)


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


def sanitize_and_format_history(
    history: Any,
    current_message: Optional[str] = None
) -> List[Any]:
    """
    Validates, limits, and structures prior conversation history into google-genai Content objects.
    - Excludes non-dialogue items (welcome messages, errors, crisis notices).
    - Prevents duplicating current_message if it was already appended to history.
    - Slices to the MAX_HISTORY_ITEMS window.
    - Drops leading orphaned 'model' turns so conversation starts with a 'user' turn.
    - Merges consecutive turns with identical roles to preserve turn alternation.
    """
    from google.genai import types

    if not isinstance(history, list):
        return []

    curr_text_norm = current_message.strip() if current_message else None
    cleaned_turns: List[Dict[str, str]] = []

    for item in history:
        if not isinstance(item, dict):
            continue

        # Filter out system, welcome, error, and crisis items
        if item.get('source') in ('welcome', 'crisis_safety_intervention') or item.get('isError') or item.get('isCrisis'):
            continue
        item_id = str(item.get('id') or '')
        if item_id.startswith('welcome') or item_id.startswith('err-'):
            continue

        role_raw = item.get('role') or item.get('sender')
        text_raw = item.get('text') or item.get('message') or item.get('content')
        if not text_raw or not isinstance(text_raw, str):
            continue
        text = text_raw.strip()[:MAX_HISTORY_MESSAGE_LENGTH]
        if not text:
            continue

        role = 'user' if str(role_raw).lower() in ('user', 'human', 'student') else 'model'
        cleaned_turns.append({'role': role, 'text': text})

    # If the last item in cleaned_turns is a user message matching current_message, drop it to prevent duplication
    if curr_text_norm and cleaned_turns:
        last = cleaned_turns[-1]
        if last['role'] == 'user' and last['text'] == curr_text_norm:
            cleaned_turns.pop()

    # Limit to most recent entries
    if len(cleaned_turns) > MAX_HISTORY_ITEMS:
        cleaned_turns = cleaned_turns[-MAX_HISTORY_ITEMS:]

    # Ensure history begins with a 'user' turn (drop leading orphaned 'model' turns)
    while cleaned_turns and cleaned_turns[0]['role'] != 'user':
        cleaned_turns.pop(0)

    # Merge consecutive turns with identical roles to preserve strict turn alternation
    merged_turns: List[Dict[str, str]] = []
    for turn in cleaned_turns:
        if merged_turns and merged_turns[-1]['role'] == turn['role']:
            merged_turns[-1]['text'] += "\n" + turn['text']
        else:
            merged_turns.append(turn)

    formatted: List[Any] = []
    for turn in merged_turns:
        formatted.append(
            types.Content(
                role=turn['role'],
                parts=[types.Part.from_text(text=turn['text'])]
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
    3. If GEMINI_API_KEY is configured, calls Gemini via official google-genai SDK
       with resilient model fallback (preferred model -> backup models).
    4. If GEMINI_API_KEY is absent or API fails, smoothly falls back to contextual guidance.
    5. Strictly isolates student health/mood data: never injects or forwards database metrics.
    """
    clean_message = (message or "").strip()

    # 1. Immediate Crisis / Safety check
    if check_crisis_intent(clean_message):
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
            'reply': get_contextual_fallback_response(clean_message, history),
            'source': 'wellvia_local_assistant'
        }

    # 3. Call official Google GenAI SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        preferred_model = get_gemini_model_name()

        # Build content list
        contents: List[Any] = []
        if history:
            contents.extend(sanitize_and_format_history(history, current_message=clean_message))
        contents.append(
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=clean_message)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=WELLNESS_SYSTEM_INSTRUCTION,
            temperature=0.7,
            max_output_tokens=2500
        )

        # Resilient model fallback: preferred model first, then backup models
        models_to_try = [preferred_model]
        for backup_model in BACKUP_GEMINI_MODELS:
            if backup_model not in models_to_try:
                models_to_try.append(backup_model)

        last_error = None
        reply_text = None

        for model_candidate in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_candidate,
                    contents=contents,
                    config=config
                )
                candidate_text = getattr(response, 'text', None)
                if candidate_text and candidate_text.strip():
                    reply_text = candidate_text.strip()
                    break
            except Exception as model_err:
                last_error = model_err
                logger.warning(
                    "Gemini model '%s' failed (%s); trying fallback if available.",
                    model_candidate,
                    type(model_err).__name__
                )
                continue

        if reply_text:
            return {
                'success': True,
                'reply': reply_text,
                'source': 'gemini'
            }

        if last_error:
            logger.warning("All Gemini model attempts failed (%s); serving contextual guidance.", type(last_error).__name__)
        else:
            logger.warning("Gemini returned empty or filtered response; serving contextual guidance.")

        return {
            'success': True,
            'reply': get_contextual_fallback_response(clean_message, history),
            'source': 'wellvia_local_assistant'
        }

    except Exception as e:
        # Secure logging: never log user message, tokens, or headers
        logger.warning("Gemini provider error (%s); serving local wellness guidance.", type(e).__name__)
        return {
            'success': True,
            'reply': get_contextual_fallback_response(clean_message, history),
            'source': 'wellvia_local_assistant'
        }

