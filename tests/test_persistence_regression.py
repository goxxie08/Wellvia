import os
import pytest
from datetime import date, timedelta
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

def test_wellness_log_zero_values_persistence(client, app_instance):
    """
    REGRESSION TEST:
    Verify that 0 values (e.g. sleep_hours: 0, water_glasses: 0, study_hours: 0)
    are NOT treated as falsy and converted to None/blank when saved or retrieved.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    # Save wellness log with explicit 0 values
    res_post = client.post('/api/student/wellness', json={
        'sleep_hours': 0,
        'sleep_quality': 1,
        'water_glasses': 0,
        'exercise_type': 'Rest',
        'exercise_duration': 0,
        'exercise_intensity': 'Low',
        'mood': 2,
        'stress_level': 5,
        'study_hours': 0,
        'study_sessions': 0,
        'study_subject': 'Testing'
    })
    assert res_post.status_code == 200
    post_data = res_post.get_json()
    assert post_data['success'] is True
    # The immediate POST response must contain the synchronized record with 0s preserved
    assert 'record' in post_data
    assert post_data['record']['sleep_hours'] == 0
    assert post_data['record']['water_glasses'] == 0
    assert post_data['record']['study_hours'] == 0

    # Simulate page refresh: GET /api/student/wellness/today
    res_get = client.get('/api/student/wellness/today')
    assert res_get.status_code == 200
    get_data = res_get.get_json()
    assert get_data['success'] is True
    today_rec = get_data['record']
    assert today_rec is not None
    assert today_rec['sleep_hours'] == 0
    assert today_rec['water_glasses'] == 0
    assert today_rec['study_hours'] == 0

    # Verify actual database persistence in SQLite
    with app_instance.app_context():
        today_str = date.today().strftime('%Y-%m-%d')
        row = execute_query(
            "SELECT sleep_hours, water_glasses, study_hours FROM wellness_records WHERE user_id = %s AND (record_date = %s OR record_date = %s)",
            (14, today_str, date.today()),
            fetchone=True
        )
        assert row is not None
        assert row['sleep_hours'] == 0
        assert row['water_glasses'] == 0
        assert row['study_hours'] == 0

def test_body_metrics_persistence_and_refresh_shape(client, app_instance):
    """
    REGRESSION TEST:
    Verify that POST and GET /api/student/body-metrics return consistent response keys
    (assessment, bmi, standard_category, ml_health_status, ml_lifestyle_risk)
    so cards do not disappear after page refresh.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    # Save body metrics with questionnaire
    payload = {
        'height': 168.0,
        'weight': 62.0,
        'gender': 'Female',
        'include_lifestyle': True,
        'lifestyle_payload': {
            'Age': 20,
            'family_history_with_overweight': 'yes',
            'FAVC': 'yes',
            'FCVC': 2.0,
            'NCP': 3.0,
            'CAEC': 'Sometimes',
            'SMOKE': 'no',
            'CH2O': 2.0,
            'SCC': 'no',
            'FAF': 1.0,
            'TUE': 1.0,
            'CALC': 'Sometimes',
            'MTRANS': 'Public_Transportation'
        }
    }
    res_post = client.post('/api/student/body-metrics', json=payload)
    assert res_post.status_code == 200
    post_data = res_post.get_json()
    assert post_data['success'] is True
    assert 'assessment' in post_data
    assert 'bmi' in post_data['assessment']
    assert 'standard_category' in post_data['assessment']
    assert 'ml_health_status' in post_data['assessment']
    assert post_data['assessment']['ml_lifestyle_risk'] is not None

    # Simulate page refresh: GET /api/student/body-metrics
    res_get = client.get('/api/student/body-metrics')
    assert res_get.status_code == 200
    get_data = res_get.get_json()
    assert get_data['success'] is True
    assert 'assessment' in get_data
    assess = get_data['assessment']
    assert assess['bmi'] is not None
    assert assess['standard_category'] is not None
    assert assess['ml_health_status'] is not None
    # ml_lifestyle_risk must be preserved from DB on GET
    assert assess['ml_lifestyle_risk'] == post_data['assessment']['ml_lifestyle_risk']

    # Confirm database persistence in users table and bmi_history table
    with app_instance.app_context():
        user_row = execute_query(
            "SELECT ml_lifestyle_risk FROM users WHERE id = %s",
            (14,),
            fetchone=True
        )
        assert user_row is not None
        assert user_row['ml_lifestyle_risk'] == assess['ml_lifestyle_risk']

        hist_row = execute_query(
            "SELECT height, weight, bmi FROM bmi_history WHERE user_id = %s ORDER BY recorded_at DESC LIMIT 1",
            (14,),
            fetchone=True
        )
        assert hist_row is not None
        assert float(hist_row['height']) == 168.0
        assert float(hist_row['weight']) == 62.0

def test_weekly_challenge_persistence_across_days(client, app_instance):
    """
    REGRESSION TEST:
    Verify that a weekly challenge completed earlier in the week remains
    marked as completed on subsequent days of the same week, rather than resetting daily.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    # Fetch challenges
    res_init = client.get('/api/student/challenges')
    assert res_init.status_code == 200
    challenges = res_init.get_json().get('challenges', [])
    weekly_challenges = [c for c in challenges if c.get('challenge_type') == 'weekly']
    assert len(weekly_challenges) > 0
    weekly_chal = weekly_challenges[0]
    chal_id = weekly_chal['id']

    # Clean up any existing progress for this challenge to ensure fresh state
    with app_instance.app_context():
        execute_query("DELETE FROM challenge_progress WHERE user_id = %s AND challenge_id = %s", (14, chal_id), commit=True)

    # Complete the challenge
    res_comp = client.post(f'/api/student/challenges/{chal_id}/complete')
    assert res_comp.status_code == 200

    # Simulate next day in the same week by modifying start_date and completion_date in challenge_progress to 2 days ago
    past_date_str = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    with app_instance.app_context():
        execute_query(
            "UPDATE challenge_progress SET start_date = %s, completion_date = %s WHERE user_id = %s AND challenge_id = %s",
            (past_date_str, past_date_str, 14, chal_id),
            commit=True
        )

    # Refresh challenges page (GET /api/student/challenges)
    res_refresh = client.get('/api/student/challenges')
    assert res_refresh.status_code == 200
    refreshed_list = res_refresh.get_json().get('challenges', [])
    target = next((c for c in refreshed_list if c['id'] == chal_id), None)
    assert target is not None
    # Must remain completed because it's within the 7-day weekly window!
    assert target['is_completed'] == 1 or target['is_completed'] is True

def test_student_data_isolation(client):
    """
    SECURITY & PRIVACY TEST:
    Verify that Student B cannot view Student A's wellness log, body metrics, or streak.
    """
    # Student A (Kelly, id=14) logs wellness
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    client.post('/api/student/wellness', json={
        'sleep_hours': 9.0,
        'sleep_quality': 5,
        'water_glasses': 10,
        'exercise_type': 'Running',
        'exercise_duration': 45,
        'exercise_intensity': 'High',
        'mood': 5,
        'stress_level': 1,
        'study_hours': 6.0,
        'study_sessions': 3,
        'study_subject': 'KellyPrivateSubject'
    })

    # Student B (id=13) accesses dashboard and wellness
    with client.session_transaction() as sess:
        sess['user_id'] = 13
        sess['username'] = 'StudentB'
        sess['role'] = 'student'

    res_b_well = client.get('/api/student/wellness/today')
    assert res_b_well.status_code == 200
    b_rec = res_b_well.get_json().get('record')
    # If Student B has a record, it must NOT be Student A's private subject
    if b_rec:
        assert b_rec.get('study_subject') != 'KellyPrivateSubject'

    # Student B progress analytics
    res_b_prog = client.get('/api/student/progress?days=7')
    assert res_b_prog.status_code == 200
    b_prog = res_b_prog.get_json()
    assert b_prog['success'] is True
    # Student B's recent history must not contain Student A's private subject
    for entry in b_prog.get('recent_logs', []):
        assert entry.get('study_subject') != 'KellyPrivateSubject'

def test_sqlite_db_config_fallback(app_instance):
    """
    DATABASE CONFIG TEST:
    Verify that SQLite connection resolution safely respects custom config paths.
    """
    with app_instance.app_context():
        from app.models.db import get_sqlite_db
        # Standard default db path
        db = get_sqlite_db()
        assert db is not None
        # Verify custom path in config
        custom_path = os.path.join(os.path.dirname(app_instance.root_path), 'test_custom.db')
        app_instance.config['SQLITE_DB'] = custom_path
        db_custom = get_sqlite_db()
        assert db_custom is not None
        # Revert config
        del app_instance.config['SQLITE_DB']
        if os.path.exists(custom_path):
            try:
                db_custom.close()
                os.remove(custom_path)
            except Exception:
                pass

def test_dashboard_and_student_routes_serve_react_spa(client):
    """
    REGRESSION TEST:
    Verify that GET /dashboard and related student routes serve the React SPA entry point
    (dist/index.html with <div id="root">) on both direct navigation and browser refresh,
    rather than rendering the old Flask/Jinja templates.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    # Direct navigation and refresh for student SPA routes
    student_routes = [
        '/dashboard',
        '/body-metrics',
        '/wellness',
        '/wellness/history',
        '/challenges',
        '/progress',
        '/profile',
        '/tips',
        '/'
    ]
    for route in student_routes:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} returned status {res.status_code}"
        html = res.get_data(as_text=True)
        # Must contain React root container and Wellvia title
        assert '<div id="root">' in html, f"Route {route} missing React #root container"
        assert "Wellvia" in html, f"Route {route} missing Wellvia brand title"
        # Must NOT contain the legacy Flask dashboard title
        assert "Student Dashboard - Wellvia" not in html, f"Route {route} returned legacy Jinja dashboard"

def test_public_and_admin_react_routes_serve_spa(client):
    """
    Verify public auth and admin routes return the React SPA entry point.
    """
    routes = ['/login', '/register', '/forgot-password', '/admin']
    for route in routes:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} returned status {res.status_code}"
        html = res.get_data(as_text=True)
        assert '<div id="root">' in html
        assert "Wellvia" in html

def test_missing_static_assets_return_404_not_html(client):
    """
    CRITICAL REQUIREMENT:
    Missing static assets (e.g., .js, .css, .png, files under /assets/ or /static/)
    must return an explicit 404 response instead of falling back to the HTML SPA entry point.
    """
    res_js = client.get('/assets/nonexistent-bundle.js')
    assert res_js.status_code == 404
    assert '<div id="root">' not in res_js.get_data(as_text=True)

    res_css = client.get('/static/nonexistent-style.css')
    assert res_css.status_code == 404
    assert '<div id="root">' not in res_css.get_data(as_text=True)

    res_img = client.get('/nonexistent-image.png')
    assert res_img.status_code == 404
    assert '<div id="root">' not in res_img.get_data(as_text=True)

def test_missing_api_endpoint_returns_json_404(client):
    """
    Missing endpoints under /api/ must return JSON 404, never the HTML SPA entry point.
    """
    res = client.get('/api/student/nonexistent-endpoint')
    assert res.status_code == 404
    assert res.is_json
    data = res.get_json()
    assert data.get('success') is False
    assert '<div id="root">' not in res.get_data(as_text=True)

def test_legacy_templates_accessible_with_query_param(client):
    """
    Verify legacy templates remain accessible when explicitly requested via ?legacy=1.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    res = client.get('/dashboard?legacy=1')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert '<div id="root">' not in html
    assert "Student Dashboard - Wellvia" in html

