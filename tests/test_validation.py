import unittest
from app.utils.validation import validate_registration, validate_wellness_input

class TestValidation(unittest.TestCase):
    def test_validate_registration_valid(self):
        errors = validate_registration("johndoe", "john@example.com", "password123", "password123")
        self.assertEqual(len(errors), 0)

    def test_validate_registration_mismatch_password(self):
        errors = validate_registration("johndoe", "john@example.com", "password123", "different")
        self.assertIn("Passwords do not match.", errors)

    def test_validate_registration_invalid_email(self):
        errors = validate_registration("johndoe", "not-an-email", "password123", "password123")
        self.assertIn("Please enter a valid email address.", errors)

    def test_validate_wellness_input_valid(self):
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
        self.assertEqual(len(errors), 0)

    def test_validate_wellness_input_invalid_ranges(self):
        data = {
            'sleep_hours': '25.0',  # > 24
            'mood': '6',            # > 5
            'stress_level': '0'     # < 1
        }
        errors = validate_wellness_input(data)
        self.assertEqual(len(errors), 3)

if __name__ == '__main__':
    unittest.main()
