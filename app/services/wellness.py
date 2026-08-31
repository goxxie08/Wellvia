from datetime import date
from app.models.db import execute_query
from app.services.scoring import calculate_wellness_score
from app.services.gamification import add_user_points, calculate_current_streak, check_and_award_achievements, POINTS_MAP

def get_today_record(user_id):
    """Retrieve today's wellness record for student."""
    today = date.today()
    return execute_query(
        "SELECT * FROM wellness_records WHERE user_id = %s AND record_date = %s",
        (user_id, today),
        fetchone=True
    )

def log_daily_wellness(user_id, form_data):
    """
    Upserts daily wellness metrics for user for today's date.
    Calculates wellness score, updates points/streaks, and checks achievement badges.
    """
    today = date.today()
    existing_record = get_today_record(user_id)
    
    # Parse form inputs safely
    sleep_hours = float(form_data.get('sleep_hours')) if form_data.get('sleep_hours') else None
    sleep_quality = int(form_data.get('sleep_quality')) if form_data.get('sleep_quality') else None
    water_glasses = int(form_data.get('water_glasses')) if form_data.get('water_glasses') else None
    exercise_type = form_data.get('exercise_type', '').strip() or None
    exercise_duration = int(form_data.get('exercise_duration')) if form_data.get('exercise_duration') else None
    exercise_intensity = form_data.get('exercise_intensity', '').strip() or None
    mood = int(form_data.get('mood')) if form_data.get('mood') else None
    stress_level = int(form_data.get('stress_level')) if form_data.get('stress_level') else None
    study_hours = float(form_data.get('study_hours')) if form_data.get('study_hours') else None
    study_sessions = int(form_data.get('study_sessions')) if form_data.get('study_sessions') else None
    study_subject = form_data.get('study_subject', '').strip() or None

    record_dict = {
        'sleep_hours': sleep_hours,
        'sleep_quality': sleep_quality,
        'water_glasses': water_glasses,
        'exercise_type': exercise_type,
        'exercise_duration': exercise_duration,
        'exercise_intensity': exercise_intensity,
        'mood': mood,
        'stress_level': stress_level,
        'study_hours': study_hours,
        'study_sessions': study_sessions,
        'study_subject': study_subject
    }

    # Calculate Wellness Score
    wellness_score = calculate_wellness_score(record_dict)

    if existing_record:
        # Update record
        query = """
            UPDATE wellness_records SET
                sleep_hours = %s, sleep_quality = %s, water_glasses = %s,
                exercise_type = %s, exercise_duration = %s, exercise_intensity = %s,
                mood = %s, stress_level = %s, study_hours = %s,
                study_sessions = %s, study_subject = %s, wellness_score = %s
            WHERE id = %s
        """
        params = (
            sleep_hours, sleep_quality, water_glasses,
            exercise_type, exercise_duration, exercise_intensity,
            mood, stress_level, study_hours,
            study_sessions, study_subject, wellness_score,
            existing_record['id']
        )
        execute_query(query, params, commit=True)
    else:
        # Insert new record & award initial daily log points
        query = """
            INSERT INTO wellness_records (
                user_id, record_date, sleep_hours, sleep_quality, water_glasses,
                exercise_type, exercise_duration, exercise_intensity, mood,
                stress_level, study_hours, study_sessions, study_subject, wellness_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id, today, sleep_hours, sleep_quality, water_glasses,
            exercise_type, exercise_duration, exercise_intensity, mood,
            stress_level, study_hours, study_sessions, study_subject, wellness_score
        )
        execute_query(query, params, commit=True)
        
        # Award daily logging points (+10)
        add_user_points(user_id, POINTS_MAP['daily_log'])

    # Evaluate achievements & recalculate streaks
    new_badges = check_and_award_achievements(user_id)
    streak = calculate_current_streak(user_id)
    
    return {
        'wellness_score': wellness_score,
        'streak': streak,
        'new_badges': new_badges
    }
