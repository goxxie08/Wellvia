import pytest
from datetime import date, timedelta
from app import create_app
from app.services.analytics import get_student_analytics_data
from app.models.db import execute_query

@pytest.fixture
def app_instance():
    app = create_app('default')
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_progress_empty_records(app_instance):
    """
    Test analytics behavior when a user has no wellness records in the period.
    Ensures missing values are None (not 0) and insufficient info messages are returned.
    """
    with app_instance.app_context():
        # User ID 99999 has no records
        chart_data, insights = get_student_analytics_data(user_id=99999, days=7)
        
        overview = chart_data['overview']
        assert overview['logged_days_count'] == 0
        assert overview['sleep']['avg'] is None
        assert overview['water']['avg'] is None
        assert overview['exercise']['avg'] is None
        assert overview['study']['avg'] is None
        assert overview['stress']['avg'] is None
        assert overview['mood']['dominant'] is None
        
        # Verify analysis handles insufficient data
        analysis = chart_data['analysis']
        assert len(analysis) == 6
        for item in analysis:
            assert item['status'] == 'insufficient_data'
            assert "Log a few days of wellness data" in item['observation']
            
        # Verify areas to improve gives encouragement to log
        areas = chart_data['areas_to_improve']
        assert len(areas) == 1
        assert areas[0].get('is_insufficient') is True
        assert "baseline" in areas[0]['headline'].lower() or "log" in areas[0]['headline'].lower()

def test_progress_distinguishes_zero_from_missing(app_instance):
    """
    Test that a genuine value of zero (e.g., exercise_duration = 0)
    is computed as 0.0, NOT treated as missing data (None).
    """
    with app_instance.app_context():
        test_uid = 9876
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Clean up any test records for this user
        execute_query(
            "DELETE FROM wellness_records WHERE user_id = %s",
            (test_uid,),
            commit=True
        )
        execute_query(
            """
            INSERT INTO wellness_records (user_id, record_date, sleep_hours, water_glasses, exercise_duration, study_hours, mood, stress_level, wellness_score)
            VALUES (%s, %s, 7.5, 8, 0, 0, 4, 2, 75)
            """,
            (test_uid, yesterday),
            commit=True
        )
        execute_query(
            """
            INSERT INTO wellness_records (user_id, record_date, sleep_hours, water_glasses, exercise_duration, study_hours, mood, stress_level, wellness_score)
            VALUES (%s, %s, 8.0, 8, 0, 0, 4, 2, 80)
            """,
            (test_uid, today),
            commit=True
        )
        
        chart_data, _ = get_student_analytics_data(user_id=test_uid, days=7)
        overview = chart_data['overview']
        
        # Exercise and study average must be 0.0, NOT None
        assert overview['exercise']['avg'] == 0.0
        assert overview['exercise']['total'] == 0
        assert overview['study']['avg'] == 0.0
        
        # In analysis, low exercise (0 mins) should be marked as needs_improvement
        analysis_map = {item['key']: item for item in chart_data['analysis']}
        assert analysis_map['exercise']['status'] == 'needs_improvement'
        assert analysis_map['exercise']['current_value'] == 0.0

def test_progress_api_endpoint(client):
    """
    Verify /api/student/progress endpoint returns 200 with new structured keys.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 14
        sess['username'] = 'Kelly'
        sess['role'] = 'student'

    res = client.get('/api/student/progress?days=7')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'overview' in data
    assert 'analysis' in data
    assert 'areas_to_improve' in data
    assert 'chart_data' in data
    assert 'labels' in data['chart_data']
    assert 'mood_categories' in data['chart_data']
    assert 'stress_categories' in data['chart_data']
