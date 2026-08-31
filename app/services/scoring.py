"""
Rule-Based Wellness Score Engine
Calculates a 0-100 wellness score based on 6 daily categories:
- Hydration: 20% (Target: 8+ glasses)
- Sleep: 20% (Target: 7-9 hours)
- Exercise: 15% (Target: 30+ minutes)
- Mood: 15% (Scale 1-5)
- Stress: 15% (Inverse Scale 1-5)
- Study Balance: 15% (Balanced 2-6 hours)
"""

def normalize_hydration(glasses):
    if glasses is None:
        return None
    try:
        g = float(glasses)
        return min(100.0, (g / 8.0) * 100.0)
    except (ValueError, TypeError):
        return None

def normalize_sleep(hours):
    if hours is None:
        return None
    try:
        h = float(hours)
        if 7.0 <= h <= 9.0:
            return 100.0
        elif 6.0 <= h < 7.0:
            return 80.0
        elif 9.0 < h <= 10.0:
            return 80.0
        elif 5.0 <= h < 6.0:
            return 60.0
        elif 10.0 < h <= 12.0:
            return 60.0
        elif 4.0 <= h < 5.0:
            return 40.0
        else:  # < 4.0 or > 12.0
            return 20.0
    except (ValueError, TypeError):
        return None

def normalize_exercise(duration_mins):
    if duration_mins is None:
        return None
    try:
        mins = float(duration_mins)
        if mins >= 30:
            return 100.0
        elif mins > 0:
            return (mins / 30.0) * 100.0
        return 0.0
    except (ValueError, TypeError):
        return None

def normalize_mood(rating):
    if rating is None:
        return None
    try:
        m = int(rating)
        mapping = {5: 100.0, 4: 80.0, 3: 60.0, 2: 40.0, 1: 20.0}
        return mapping.get(m, None)
    except (ValueError, TypeError):
        return None

def normalize_stress(rating):
    if rating is None:
        return None
    try:
        s = int(rating)
        # Inverse: 1 (Very Low) = 100, 5 (Very High) = 20
        mapping = {1: 100.0, 2: 80.0, 3: 60.0, 4: 40.0, 5: 20.0}
        return mapping.get(s, None)
    except (ValueError, TypeError):
        return None

def normalize_study(hours):
    if hours is None:
        return None
    try:
        h = float(hours)
        if 2.0 <= h <= 6.0:
            return 100.0
        elif 1.0 <= h < 2.0 or 6.0 < h <= 8.0:
            return 80.0
        elif 0.5 <= h < 1.0 or 8.0 < h <= 10.0:
            return 50.0
        elif h > 10.0:
            return 20.0
        else: # 0 hours
            return 40.0
    except (ValueError, TypeError):
        return None

def calculate_wellness_score(record):
    """
    Computes a composite wellness score (0-100) from a daily record dict.
    Redistributes weights if some components are missing.
    Requires at least 2 components for calculation.
    """
    if not record:
        return None
        
    weights = {
        'hydration': 0.20,
        'sleep': 0.20,
        'exercise': 0.15,
        'mood': 0.15,
        'stress': 0.15,
        'study': 0.15
    }
    
    sub_scores = {
        'hydration': normalize_hydration(record.get('water_glasses')),
        'sleep': normalize_sleep(record.get('sleep_hours')),
        'exercise': normalize_exercise(record.get('exercise_duration')),
        'mood': normalize_mood(record.get('mood')),
        'stress': normalize_stress(record.get('stress_level')),
        'study': normalize_study(record.get('study_hours'))
    }
    
    # Filter out missing metrics
    available = {k: v for k, v in sub_scores.items() if v is not None}
    
    if len(available) < 2:
        return None  # Insufficient data for composite score
        
    # Calculate total weight of available metrics and normalize weights
    available_weight_sum = sum(weights[k] for k in available.keys())
    
    composite_score = 0.0
    for k, score in available.items():
        adjusted_weight = weights[k] / available_weight_sum
        composite_score += score * adjusted_weight
        
    return int(round(composite_score))
