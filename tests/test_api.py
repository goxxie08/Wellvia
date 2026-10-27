import pytest
from app import create_app
from app.models.db import execute_query

@pytest.fixture
def app_instance():
    app = create_app('default')
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_api_unauthenticated_me(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 200
    data = res.get_json()
    assert data['authenticated'] is False
    assert data['user'] is None

def test_api_login_and_authenticated_me(client):
    # Log in as admin
    res = client.post('/api/auth/login', json={
        'login_input': 'admin@wellvia.edu',
        'password': 'Admin@123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['role'] == 'admin'

    # Check /api/auth/me
    res_me = client.get('/api/auth/me')
    assert res_me.status_code == 200
    data_me = res_me.get_json()
    assert data_me['authenticated'] is True
    assert data_me['user']['username'] == 'admin'

    # Check /api/auth/logout
    res_logout = client.post('/api/auth/logout')
    assert res_logout.status_code == 200

    # Verify session cleared
    res_me2 = client.get('/api/auth/me')
    assert res_me2.get_json()['authenticated'] is False

def test_api_demo_student_login(client):
    # 1. Login with demo student username 'Kelly'
    res = client.post('/api/auth/login', json={
        'login_input': 'Kelly',
        'password': 'Password123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['username'] == 'Kelly'
    assert data['user']['role'] == 'student'
    assert data['redirect'] == '/dashboard'

    # 2. Check /api/auth/me returns authenticated student
    res_me = client.get('/api/auth/me')
    assert res_me.status_code == 200
    data_me = res_me.get_json()
    assert data_me['authenticated'] is True
    assert data_me['user']['username'] == 'Kelly'
    assert data_me['user']['role'] == 'student'

    # 3. Check /api/student/dashboard returns student's dashboard
    res_dash = client.get('/api/student/dashboard')
    assert res_dash.status_code == 200
    assert res_dash.get_json()['success'] is True

    # 4. Logout
    client.post('/api/auth/logout')

    # 5. Login with demo student email 'student@wellvia.edu'
    res_email = client.post('/api/auth/login', json={
        'login_input': 'student@wellvia.edu',
        'password': 'Password123'
    })
    assert res_email.status_code == 200
    assert res_email.get_json()['success'] is True
    assert res_email.get_json()['user']['username'] == 'Kelly'

    # Logout to clean session
    client.post('/api/auth/logout')


def test_api_student_dashboard_and_metrics(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 14  # Kelly from seed DB
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    # 1. Dashboard
    res = client.get('/api/student/dashboard')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'today_record' in data
    assert 'streak' in data
    assert 'challenges' in data

    # 2. Body Metrics POST
    res_post = client.post('/api/student/body-metrics', json={
        'height': 172.0,
        'weight': 64.0,
        'gender': 'Female',
        'include_lifestyle': False
    })
    assert res_post.status_code == 200
    data_bm = res_post.get_json()
    assert data_bm['success'] is True
    assert data_bm['bmi_info']['category'] == 'Normal weight'
    assert data_bm['ml_health_status'] == 'Normal'

    # 3. Wellness log POST
    res_log = client.post('/api/student/wellness', json={
        'sleep_hours': 8.0,
        'sleep_quality': 4,
        'water_glasses': 8,
        'exercise_type': 'Walk',
        'exercise_duration': 30,
        'exercise_intensity': 'Medium',
        'mood': 4,
        'stress_level': 2,
        'study_hours': 4.0,
        'study_sessions': 2,
        'study_subject': 'Computer Science'
    })
    assert res_log.status_code == 200
    data_log = res_log.get_json()
    assert data_log['success'] is True
    assert data_log['result']['wellness_score'] > 0

    # 4. Progress analytics GET
    res_prog = client.get('/api/student/progress?days=7')
    assert res_prog.status_code == 200
    data_prog = res_prog.get_json()
    assert data_prog['success'] is True
    assert 'chart_data' in data_prog

from unittest.mock import patch, MagicMock

def test_api_chat_companion(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Take a slow, deep breath. Focus on one topic at a time and take regular breaks."
    mock_client.models.generate_content.return_value = mock_response

    with patch('google.genai.Client', return_value=mock_client):
        res = client.post('/api/chat/message', json={'message': 'I have exams tomorrow and feel anxious'})
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'reply' in data
        assert len(data['reply']) > 10

