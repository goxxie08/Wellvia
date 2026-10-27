import os
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.services.chat_service import sanitize_and_format_history, get_contextual_fallback_response, check_crisis_intent


@pytest.fixture
def app_instance():
    app = create_app('default')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def auth_student_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 14  # Kelly from seed data
        sess['username'] = 'Kelly'
        sess['role'] = 'student'
    return client


# -----------------------------------------------------------------------------
# 1. Authentication & Authorization Tests
# -----------------------------------------------------------------------------

def test_chat_unauthenticated(client):
    """Chat endpoint must reject unauthenticated requests with 401."""
    res = client.post('/api/chat/message', json={'message': 'Hello Wellvia'})
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False
    assert 'Authentication required' in data['error']


# -----------------------------------------------------------------------------
# 2. Input Validation Tests & Length Limits
# -----------------------------------------------------------------------------

def test_chat_invalid_payload_type(auth_student_client):
    """Payload must be a JSON object."""
    res = auth_student_client.post('/api/chat/message', data='not json', content_type='text/plain')
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'Invalid request payload' in data['error']


def test_chat_empty_or_whitespace_message(auth_student_client):
    """Empty or whitespace-only message returns 400."""
    for empty_val in ['', '   ', '\n\t  ', None]:
        res = auth_student_client.post('/api/chat/message', json={'message': empty_val})
        assert res.status_code == 400
        data = res.get_json()
        assert data['success'] is False
        assert 'cannot be empty' in data['error']


def test_chat_message_length_limit(auth_student_client):
    """Messages exceeding 1000 characters must be rejected with 400."""
    long_message = 'A' * 1001
    res = auth_student_client.post('/api/chat/message', json={'message': long_message})
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'exceeds maximum allowed length' in data['error']


def test_chat_invalid_history_format(auth_student_client):
    """If history is provided, it must be a list."""
    res = auth_student_client.post('/api/chat/message', json={
        'message': 'Hello',
        'history': 'this should be a list, not a string'
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'history must be a list' in data['error']


# -----------------------------------------------------------------------------
# 3. Crisis Safety & Intervention Tests
# -----------------------------------------------------------------------------

def test_chat_crisis_safety_intervention(auth_student_client):
    """Expressions of crisis or self-harm immediately trigger crisis resources."""
    crisis_prompts = [
        "I feel completely overwhelmed and want to kill myself",
        "I'm thinking about suicide",
        "I have thoughts of self harm and cutting myself",
        "I don't want to live anymore",
        "I want to end it all",
        "I feel like dying today"
    ]
    for prompt in crisis_prompts:
        res = auth_student_client.post('/api/chat/message', json={'message': prompt})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'crisis_safety_intervention'
        assert '988' in data['reply']
        assert '741741' in data['reply']
        assert 'campus' in data['reply'].lower()


def test_chat_crisis_no_false_positives():
    """Everyday student idioms should not trigger the crisis safety intervention."""
    casual_phrases = [
        "I have a killer headache from studying",
        "This exam is going to kill my GPA",
        "I'm dying of boredom in lecture",
        "How do I manage deadline stress?"
    ]
    for phrase in casual_phrases:
        assert not check_crisis_intent(phrase)


# -----------------------------------------------------------------------------
# 4. Specific Question Relevance & System Instruction Verification (Mocked)
# -----------------------------------------------------------------------------

def test_chat_gemini_specific_question_relevant_answer(auth_student_client, monkeypatch):
    """Specific user question receives relevant mocked answer and applies system instruction."""
    auth_student_client.application.config['GEMINI_API_KEY'] = 'test_key_server_only'
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = (
        "For quick neck tension relief between lectures, do 5 slow shoulder rolls backwards, "
        "then gently tilt your right ear to your right shoulder for 15 seconds, and repeat on the left."
    )
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client) as mock_client_cls:
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'What neck stretches can I do at my library desk?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'gemini'
        assert 'neck tension relief' in data['reply']

        # Verify Client initialized securely
        mock_client_cls.assert_called_once_with(api_key='test_key_server_only')

        # Verify generate_content parameters
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs['model'] == 'gemini-3.5-flash'
        sys_instruction = call_kwargs['config'].system_instruction
        assert 'Wellvia' in sys_instruction
        assert 'Answer the User First' in sys_instruction
        assert 'Non-clinical Scope' in sys_instruction


# -----------------------------------------------------------------------------
# 5. Follow-Up Questions & Conversation Context (Mocked)
# -----------------------------------------------------------------------------

def test_chat_follow_up_uses_conversation_context(auth_student_client, monkeypatch):
    """Follow-up questions preserve previous conversation history in correct order."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Since you already drink herbal tea, adding a cool bedroom temperature (65°F) is your next best step."
    mock_client.models.generate_content.return_value = mock_response

    history_payload = [
        {'role': 'user', 'text': 'I have trouble falling asleep before midnight.'},
        {'role': 'model', 'text': 'Try drinking warm chamomile tea and dimming lights 45 minutes before bed.'}
    ]

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'I already do the herbal tea. What else can I change?',
            'history': history_payload
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'gemini'

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        contents = call_kwargs['contents']
        assert len(contents) == 3
        assert contents[0].role == 'user'
        assert contents[0].parts[0].text == history_payload[0]['text']
        assert contents[1].role == 'model'
        assert contents[1].parts[0].text == history_payload[1]['text']
        assert contents[2].role == 'user'
        assert contents[2].parts[0].text == 'I already do the herbal tea. What else can I change?'


# -----------------------------------------------------------------------------
# 6. History Formatting, Deduplication & Ordering
# -----------------------------------------------------------------------------

def test_chat_history_does_not_duplicate_latest_message(auth_student_client, monkeypatch):
    """If caller includes latest message in history, it must NOT be duplicated in contents."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Try studying in 25-minute sprints."
    mock_client.models.generate_content.return_value = mock_response

    user_query = 'How should I break up my biology study sessions?'
    history_with_dup = [
        {'role': 'user', 'text': 'I have an exam on Friday.'},
        {'role': 'model', 'text': 'Plan your days backwards from Friday.'},
        {'role': 'user', 'text': user_query}  # Same as message
    ]

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': user_query,
            'history': history_with_dup
        })
        assert res.status_code == 200
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        contents = call_kwargs['contents']

        # Ensure user_query is only at the end once, not twice
        assert len(contents) == 3
        assert contents[0].role == 'user'
        assert contents[0].parts[0].text == 'I have an exam on Friday.'
        assert contents[1].role == 'model'
        assert contents[1].parts[0].text == 'Plan your days backwards from Friday.'
        assert contents[2].role == 'user'
        assert contents[2].parts[0].text == user_query


def test_chat_history_role_mapping_and_order():
    """Sanitizer normalizes role synonyms, strips leading model turns, and merges consecutive turns."""
    raw_history = [
        {'role': 'model', 'text': 'Welcome to Wellvia!'},  # Leading model turn should be dropped
        {'role': 'student', 'text': 'I feel restless.'},   # Normalized to 'user'
        {'role': 'human', 'text': 'And I cannot focus.'},  # Consecutive user turn -> merged
        {'role': 'assistant', 'text': 'Take a short breath.'},  # Normalized to 'model'
        {'role': 'bot', 'text': 'Then try 5 minutes of stretching.'}  # Consecutive model turn -> merged
    ]
    formatted = sanitize_and_format_history(raw_history)
    assert len(formatted) == 2
    assert formatted[0].role == 'user'
    assert 'I feel restless.\nAnd I cannot focus.' in formatted[0].parts[0].text
    assert formatted[1].role == 'model'
    assert 'Take a short breath.\nThen try 5 minutes of stretching.' in formatted[1].parts[0].text


# -----------------------------------------------------------------------------
# 7. Fallback Variety & Non-Repeating Responses
# -----------------------------------------------------------------------------

def test_chat_repeated_questions_avoid_identical_reply_in_fallback(auth_student_client):
    """Repeated questions in fallback mode must not return the exact same static reply."""
    with patch('app.services.chat_service.get_gemini_api_key', return_value=None):
        # First turn
        res1 = auth_student_client.post('/api/chat/message', json={
            'message': 'I cannot fall asleep.'
        })
        assert res1.status_code == 200
        reply1 = res1.get_json()['reply']

        # Second turn with previous assistant reply in history
        res2 = auth_student_client.post('/api/chat/message', json={
            'message': 'I cannot fall asleep.',
            'history': [
                {'role': 'user', 'text': 'I cannot fall asleep.'},
                {'role': 'model', 'text': reply1}
            ]
        })
        assert res2.status_code == 200
        reply2 = res2.get_json()['reply']

        # Replies should vary rather than repeatedly returning the identical canned response
        assert reply1 != reply2
        assert 'sleep' in reply1.lower() or 'caffeine' in reply1.lower() or 'breathing' in reply1.lower() or 'dark' in reply1.lower()
        assert 'sleep' in reply2.lower() or 'caffeine' in reply2.lower() or 'breathing' in reply2.lower() or 'dark' in reply2.lower()


def test_chat_fallback_topic_relevance():
    """Contextual fallback selects guidance relevant to the user's specific wellness topic."""
    topics_tests = [
        ('I am struggling with insomnia and sleep schedules', ['10-3-2-1-0', 'sleep', 'melatonin', '4-7-8']),
        ('I have severe exam panic and anxiety', ['5-4-3-2-1', 'sigh', 'heart rate', 'micro-task']),
        ('How should I structure my study breaks?', ['pomodoro', 'active recall', '25', 'focus', 'minutes', 'barrier', 'procrastinat']),
        ('What desk stretches can I do for neck pain?', ['shoulder', 'stretch', 'hip flexors', 'stroll', 'walking', 'movement']),
        ('How much water should I drink while studying?', ['dehydration', 'water', 'caffeine', 'protein'])
    ]
    for prompt, expected_words in topics_tests:
        resp = get_contextual_fallback_response(prompt).lower()
        assert any(word in resp for word in expected_words), f"Prompt '{prompt}' yielded irrelevant fallback: {resp}"


# -----------------------------------------------------------------------------
# 8. Provider Error Resilience, Timeouts & Empty Responses
# -----------------------------------------------------------------------------

def test_chat_missing_api_key_fallback(auth_student_client):
    """If GEMINI_API_KEY is missing, gracefully serve contextual guidance without 500 error."""
    with patch('app.services.chat_service.get_gemini_api_key', return_value=None):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'How do I calm down after an exam?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'wellvia_local_assistant'
        assert len(data['reply']) > 20


def test_chat_gemini_api_error_and_timeout_fallback(auth_student_client, monkeypatch):
    """When Gemini API encounters network errors or timeouts, fall back cleanly."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = TimeoutError("Request timed out connecting to Gemini endpoint")

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'How can I organize my study sessions?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'wellvia_local_assistant'
        assert len(data['reply']) > 20


def test_chat_gemini_empty_or_whitespace_response_fallback(auth_student_client, monkeypatch):
    """If Gemini returns an empty or whitespace response, fall back cleanly."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "   "
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'I feel restless before my test.'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'wellvia_local_assistant'
        assert len(data['reply']) > 20


def test_chat_model_fallback_resilience(auth_student_client, monkeypatch):
    """If the primary model fails (e.g. 503 high demand), the backup model is attempted."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()

    # Primary model throws exception, backup model succeeds
    backup_response = MagicMock()
    backup_response.text = "Here is guidance from the backup flash model: take a short mindful walk."
    mock_client.models.generate_content.side_effect = [
        Exception("503 Service Unavailable"),
        backup_response
    ]

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'Need advice on feeling overwhelmed.'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'gemini'
        assert data['reply'] == backup_response.text
        assert mock_client.models.generate_content.call_count == 2


# -----------------------------------------------------------------------------
# 9. Privacy Protection: No Health Data Sent to Gemini
# -----------------------------------------------------------------------------

def test_chat_privacy_no_health_data_transmitted(auth_student_client, monkeypatch):
    """
    Ensures student physical and mental health metrics (BMI, height, weight, mood logs)
    are NEVER automatically transmitted to Gemini.
    """
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hydration and light stretching work wonders!"
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'Tell me about hydration tips.'
        })
        assert res.status_code == 200
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        contents = call_kwargs['contents']

        combined_text = ' '.join(
            part.text for content in contents for part in content.parts if hasattr(part, 'text')
        )
        for private_field in ['bmi', 'weight', 'height', 'sleep_hours', 'mood', 'wellness_records']:
            assert private_field not in combined_text.lower()


# -----------------------------------------------------------------------------
# 10. Dashboard Data Personalization Tests
# -----------------------------------------------------------------------------

def test_chat_personalized_with_user_dashboard_data(auth_student_client, monkeypatch):
    """
    Ensures that when a logged-in student asks about their metrics (e.g., 'am i overweight'),
    the system instruction contains their real-time dashboard data (height, weight, BMI),
    and local fallback answers directly using their dashboard numbers.
    """
    from app.models.db import execute_query
    with auth_student_client.application.app_context():
        user = execute_query("SELECT height, weight, bmi FROM users WHERE id = 14", fetchone=True)
    height_str = str(int(user['height'])) if user and user.get('height') else "168"
    weight_str = str(int(user['weight'])) if user and user.get('weight') else "62"

    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = f"Based on your recorded height of {height_str} cm and weight of {weight_str} kg, your BMI is {user['bmi']}. You are in the normal weight range!"
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'am i overweight'
        })
        assert res.status_code == 200
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        sys_inst = call_kwargs['config'].system_instruction
        assert height_str in sys_inst
        assert weight_str in sys_inst

    # Test fallback personalization when offline
    with patch('app.services.chat_service.get_gemini_api_key', return_value=None):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'am i overweight'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert height_str in data['reply']
        assert weight_str in data['reply']
        assert 'not overweight' in data['reply'].lower()


