import pytest
from app.services.scoring import (
    calculate_wellness_score,
    normalize_hydration,
    normalize_sleep,
    normalize_exercise,
    normalize_mood,
    normalize_stress,
    normalize_study
)

def test_normalize_hydration():
    assert normalize_hydration(8) == 100.0
    assert normalize_hydration(4) == 50.0
    assert normalize_hydration(12) == 100.0  # Capped at 100
    assert normalize_hydration(None) is None

def test_normalize_sleep():
    assert normalize_sleep(8.0) == 100.0
    assert normalize_sleep(7.5) == 100.0
    assert normalize_sleep(6.5) == 80.0
    assert normalize_sleep(3.0) == 20.0
    assert normalize_sleep(None) is None

def test_normalize_exercise():
    assert normalize_exercise(30) == 100.0
    assert normalize_exercise(15) == 50.0
    assert normalize_exercise(60) == 100.0
    assert normalize_exercise(None) is None

def test_normalize_mood():
    assert normalize_mood(5) == 100.0
    assert normalize_mood(3) == 60.0
    assert normalize_mood(1) == 20.0
    assert normalize_mood(None) is None

def test_normalize_stress():
    assert normalize_stress(1) == 100.0  # Very Low stress = highest wellness score
    assert normalize_stress(5) == 20.0   # Very High stress = lowest wellness score
    assert normalize_stress(None) is None

def test_normalize_study():
    assert normalize_study(4.0) == 100.0  # Ideal balance
    assert normalize_study(12.0) == 20.0 # Excessive study
    assert normalize_study(None) is None

def test_calculate_wellness_score_full():
    record = {
        'water_glasses': 8,      # 100 * 0.20 = 20
        'sleep_hours': 8.0,      # 100 * 0.20 = 20
        'exercise_duration': 30, # 100 * 0.15 = 15
        'mood': 5,               # 100 * 0.15 = 15
        'stress_level': 1,       # 100 * 0.15 = 15
        'study_hours': 4.0       # 100 * 0.15 = 15
    }
    score = calculate_wellness_score(record)
    assert score == 100

def test_calculate_wellness_score_partial():
    record = {
        'water_glasses': 8,      # 100 (weight 0.20)
        'sleep_hours': 8.0,      # 100 (weight 0.20)
        'exercise_duration': None,
        'mood': None,
        'stress_level': None,
        'study_hours': None
    }
    score = calculate_wellness_score(record)
    assert score == 100  # Proportional redistribution

def test_calculate_wellness_score_insufficient_data():
    record = {
        'water_glasses': 8,
        'sleep_hours': None,
        'exercise_duration': None,
        'mood': None,
        'stress_level': None,
        'study_hours': None
    }
    score = calculate_wellness_score(record)
    assert score is None  # < 2 components returns None

def test_calculate_current_streak_dual_db(monkeypatch):
    """Verify streak calculation handles both SQLite strings and MySQL date objects."""
    from datetime import date, timedelta
    from unittest.mock import patch
    from app import create_app
    from app.services.gamification import calculate_current_streak

    app = create_app('development')
    today = date.today()

    # 1. SQLite string dates
    mock_sqlite = [{'record_date': (today - timedelta(days=i)).strftime('%Y-%m-%d')} for i in range(3)]
    with app.app_context(), patch('app.services.gamification.execute_query', return_value=mock_sqlite):
        streak_sqlite = calculate_current_streak(1)
        assert streak_sqlite == 3

    # 2. MySQL date objects
    mock_mysql = [{'record_date': (today - timedelta(days=i))} for i in range(4)]
    with app.app_context(), patch('app.services.gamification.execute_query', return_value=mock_mysql):
        streak_mysql = calculate_current_streak(1)
        assert streak_mysql == 4

    # 3. Broken streak
    mock_broken = [{'record_date': (today - timedelta(days=3)).strftime('%Y-%m-%d')}]
    with app.app_context(), patch('app.services.gamification.execute_query', return_value=mock_broken):
        streak_broken = calculate_current_streak(1)
        assert streak_broken == 0

