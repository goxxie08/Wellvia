import os
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from google.genai import errors


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
# 2. Input Validation Tests
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
        "I don't want to live anymore"
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


# -----------------------------------------------------------------------------
# 4. Gemini SDK Integration & Mocking Tests
# -----------------------------------------------------------------------------

def test_chat_gemini_success_with_mock(auth_student_client, monkeypatch):
    """Successful Gemini SDK response via mocked client."""
    auth_student_client.application.config['GEMINI_API_KEY'] = 'test_key_server_only'
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Try taking a 10-minute break, drinking a glass of water, and doing some gentle neck stretches."
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client) as mock_client_cls:
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'How can I stay alert while studying?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'gemini'
        assert data['reply'] == mock_response.text

        # Verify Client was initialized with server API key
        mock_client_cls.assert_called_once_with(api_key='test_key_server_only')

        # Verify call to client.models.generate_content
        mock_client.models.generate_content.assert_called_once()
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs['model'] == 'gemini-2.5-flash'
        assert 'config' in call_kwargs
        assert 'Wellvia' in call_kwargs['config'].system_instruction


def test_chat_multi_turn_history(auth_student_client, monkeypatch):
    """Validates that conversation history is formatted and included in contents."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Continuing our discussion on sleep hygiene, aim for a dark, quiet room."
    mock_client.models.generate_content.return_value = mock_response

    history_payload = [
        {'role': 'user', 'text': 'I have trouble falling asleep before midnight.'},
        {'role': 'model', 'text': 'Try setting a consistent wind-down routine without screens.'}
    ]

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'What else can I adjust in my bedroom environment?',
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
        assert contents[2].parts[0].text == 'What else can I adjust in my bedroom environment?'


# -----------------------------------------------------------------------------
# 5. Privacy Protection Tests: No Health Data Sent to Gemini
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

        # Examine every text part sent to Gemini
        combined_text = ' '.join(
            part.text for content in contents for part in content.parts if hasattr(part, 'text')
        )
        # Verify no database/user metrics are injected
        for private_field in ['bmi', 'weight', 'height', 'sleep_hours', 'mood', 'wellness_records']:
            assert private_field not in combined_text.lower()


# -----------------------------------------------------------------------------
# 6. Fallback & Provider Error Resilience Tests
# -----------------------------------------------------------------------------

def test_chat_missing_api_key_fallback(auth_student_client, monkeypatch):
    """If GEMINI_API_KEY is not configured, gracefully fall back to local assistant."""
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    # Also ensure current_app.config doesn't have it
    with patch('app.services.chat_service.get_gemini_api_key', return_value=None):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'How do I calm down after an exam?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'wellvia_local_assistant'
        assert len(data['reply']) > 10


def test_chat_gemini_provider_error_fallback(auth_student_client, monkeypatch):
    """When Gemini API encounters network or API error, fall back cleanly without 500 error."""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_server_only')

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Rate limit exceeded or network down")

    with patch('google.genai.Client', return_value=mock_client):
        res = auth_student_client.post('/api/chat/message', json={
            'message': 'How can I organize my study sessions?'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['source'] == 'wellvia_local_assistant'
        assert len(data['reply']) > 10
