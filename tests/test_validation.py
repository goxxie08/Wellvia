import pytest
from app.utils.validation import validate_registration, validate_wellness_input

def test_validate_registration_valid():
    errors = validate_registration("johndoe", "john@example.com", "password123", "password123")
    assert len(errors) == 0

def test_validate_registration_mismatch_password():
    errors = validate_registration("johndoe", "john@example.com", "password123", "different")
    assert "Passwords do not match." in errors

def test_validate_registration_invalid_email():
    errors = validate_registration("johndoe", "not-an-email", "password123", "password123")
    assert "Please enter a valid email address." in errors

def test_validate_wellness_input_valid():
    data = {
        'sleep_hours': '8.0',
        'sleep_quality': '4',
        'water_glasses': '8',
        'exercise_duration': '30',
        'mood': '5',
        'stress_level': '2',
        'study_hours': '4.0'
    }
    errors = validate_wellness_input(data)
    assert len(errors) == 0

def test_validate_wellness_input_invalid_ranges():
    data = {
        'sleep_hours': '25.0',  # > 24
        'mood': '6',            # > 5
        'stress_level': '0'     # < 1
    }
    errors = validate_wellness_input(data)
    assert len(errors) == 3
