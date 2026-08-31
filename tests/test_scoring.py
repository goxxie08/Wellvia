import unittest
from app.services.scoring import (
    calculate_wellness_score,
    normalize_hydration,
    normalize_sleep,
    normalize_exercise,
    normalize_mood,
    normalize_stress,
    normalize_study
)

class TestWellnessScoring(unittest.TestCase):
    def test_normalize_hydration(self):
        self.assertEqual(normalize_hydration(8), 100.0)
        self.assertEqual(normalize_hydration(4), 50.0)
        self.assertEqual(normalize_hydration(12), 100.0)  # Capped at 100
        self.assertIsNone(normalize_hydration(None))

    def test_normalize_sleep(self):
        self.assertEqual(normalize_sleep(8.0), 100.0)
        self.assertEqual(normalize_sleep(7.5), 100.0)
        self.assertEqual(normalize_sleep(6.5), 80.0)
        self.assertEqual(normalize_sleep(3.0), 20.0)
        self.assertIsNone(normalize_sleep(None))

    def test_normalize_exercise(self):
        self.assertEqual(normalize_exercise(30), 100.0)
        self.assertEqual(normalize_exercise(15), 50.0)
        self.assertEqual(normalize_exercise(60), 100.0)
        self.assertIsNone(normalize_exercise(None))

    def test_normalize_mood(self):
        self.assertEqual(normalize_mood(5), 100.0)
        self.assertEqual(normalize_mood(3), 60.0)
        self.assertEqual(normalize_mood(1), 20.0)
        self.assertIsNone(normalize_mood(None))

    def test_normalize_stress(self):
        self.assertEqual(normalize_stress(1), 100.0)  # Very Low stress = highest score
        self.assertEqual(normalize_stress(5), 20.0)   # Very High stress = lowest score
        self.assertIsNone(normalize_stress(None))

    def test_normalize_study(self):
        self.assertEqual(normalize_study(4.0), 100.0)  # Ideal balance
        self.assertEqual(normalize_study(12.0), 20.0) # Excessive study
        self.assertIsNone(normalize_study(None))

    def test_calculate_wellness_score_full(self):
        record = {
            'water_glasses': 8,      # 100 * 0.20 = 20
            'sleep_hours': 8.0,      # 100 * 0.20 = 20
            'exercise_duration': 30, # 100 * 0.15 = 15
            'mood': 5,               # 100 * 0.15 = 15
            'stress_level': 1,       # 100 * 0.15 = 15
            'study_hours': 4.0       # 100 * 0.15 = 15
        }
        score = calculate_wellness_score(record)
        self.assertEqual(score, 100)

    def test_calculate_wellness_score_partial(self):
        record = {
            'water_glasses': 8,      # 100 (weight 0.20)
            'sleep_hours': 8.0,      # 100 (weight 0.20)
            'exercise_duration': None,
            'mood': None,
            'stress_level': None,
            'study_hours': None
        }
        score = calculate_wellness_score(record)
        self.assertEqual(score, 100)  # Proportional weight redistribution

    def test_calculate_wellness_score_insufficient_data(self):
        record = {
            'water_glasses': 8,
            'sleep_hours': None,
            'exercise_duration': None,
            'mood': None,
            'stress_level': None,
            'study_hours': None
        }
        score = calculate_wellness_score(record)
        self.assertIsNone(score)  # < 2 components returns None

if __name__ == '__main__':
    unittest.main()
