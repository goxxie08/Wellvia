import pytest
from app import create_app
from app.models.db import execute_query

@pytest.fixture
def client():
    app = create_app('default')
    app.config['TESTING'] = True
    with app.app_context():
        execute_query("DELETE FROM users WHERE LOWER(username) = 'teststudentuser'", commit=True)
    with app.test_client() as client:
        yield client
    with app.app_context():
        execute_query("DELETE FROM users WHERE LOWER(username) = 'teststudentuser'", commit=True)



def test_registration_and_login_flow(client):
    # 1. Register a new user
    res_reg = client.post('/auth/register', data={
        'username': 'TestStudentUser',
        'email': 'student_test_user@wellvia.edu',
        'password': 'Password123',
        'confirm_password': 'Password123'
    }, follow_redirects=False)
    assert res_reg.status_code == 302
    assert '/auth/login' in res_reg.headers['Location']

    # 2. Login using exact email (new user without height/weight -> redirects to /body-metrics)
    res_login_email = client.post('/auth/login', data={
        'login_input': 'student_test_user@wellvia.edu',
        'password': 'Password123'
    }, follow_redirects=False)
    assert res_login_email.status_code == 302
    assert '/body-metrics' in res_login_email.headers['Location']

    # Submit body metrics
    res_metrics = client.post('/body-metrics', data={'height': 175, 'weight': 70}, follow_redirects=False)
    assert res_metrics.status_code == 302
    assert '/dashboard' in res_metrics.headers['Location']

    # 3. Login using case-insensitive username (lowercase) (user now has height/weight -> redirects to /dashboard)
    client.get('/auth/logout')
    res_login_username_lower = client.post('/auth/login', data={
        'login_input': 'teststudentuser',
        'password': 'Password123'
    }, follow_redirects=False)
    assert res_login_username_lower.status_code == 302
    assert '/dashboard' in res_login_username_lower.headers['Location']

    # 4. Login using case-insensitive username (uppercase)
    client.get('/auth/logout')
    res_login_username_upper = client.post('/auth/login', data={
        'login_input': 'TESTSTUDENTUSER',
        'password': 'Password123'
    }, follow_redirects=False)
    assert res_login_username_upper.status_code == 302
    assert '/dashboard' in res_login_username_upper.headers['Location']

    # 5. Login using wrong password
    client.get('/auth/logout')
    res_wrong_pw = client.post('/auth/login', data={
        'login_input': 'teststudentuser',
        'password': 'WrongPassword999'
    }, follow_redirects=False)
    assert res_wrong_pw.status_code == 200
    assert b'Invalid email/username or password.' in res_wrong_pw.data
