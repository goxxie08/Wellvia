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
