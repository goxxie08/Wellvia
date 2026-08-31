from datetime import datetime, timedelta, date
from app.models.db import execute_query

POINTS_MAP = {
    'daily_log': 10,
    'daily_challenge': 20,
    'weekly_challenge': 50
}

def add_user_points(user_id, points):
    """Add points to user's running total."""
    if points <= 0:
        return
    execute_query(
        "UPDATE users SET total_points = total_points + %s WHERE id = %s",
        (points, user_id),
        commit=True
    )

def calculate_current_streak(user_id):
    """
    Calculates consecutive days count where user has logged wellness data.
    Looks backward starting from today or yesterday.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Fetch dates of logged records ordered descending
    records = execute_query(
        "SELECT record_date FROM wellness_records WHERE user_id = %s ORDER BY record_date DESC",
        (user_id,),
        fetchall=True
    )
    
    if not records:
        return 0
        
    logged_dates = {r['record_date'] for r in records}
    
    # Determine starting date for loop
    if today in logged_dates:
        curr = today
    elif yesterday in logged_dates:
        curr = yesterday
    else:
        return 0  # Streak broken
        
    streak = 0
    while curr in logged_dates:
        streak += 1
        curr = curr - timedelta(days=1)
        
    return streak

def check_and_award_achievements(user_id):
    """
    Evaluates unearned achievement badges for user and awards newly qualified ones.
    Returns list of newly earned achievement names.
    """
    # Fetch all unearned achievements for user
    unearned = execute_query(
        """
        SELECT a.* FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = %s
        WHERE ua.id IS NULL
        """,
        (user_id,),
        fetchall=True
    )
    
    if not unearned:
        return []
        
    streak = calculate_current_streak(user_id)
    
    # Fetch aggregated stats for user
    stats = execute_query(
        """
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN water_glasses >= 8 THEN 1 ELSE 0 END) as hydration_target_days,
            SUM(CASE WHEN sleep_hours >= 7 THEN 1 ELSE 0 END) as good_sleep_days,
            SUM(CASE WHEN exercise_duration >= 20 THEN 1 ELSE 0 END) as exercise_days,
            SUM(CASE WHEN sleep_hours IS NOT NULL AND water_glasses IS NOT NULL AND exercise_duration IS NOT NULL AND mood IS NOT NULL AND stress_level IS NOT NULL AND study_hours IS NOT NULL THEN 1 ELSE 0 END) as all_categories_days
        FROM wellness_records WHERE user_id = %s
        """,
        (user_id,),
        fetchone=True
    )
    
    challenges_count_row = execute_query(
        "SELECT COUNT(*) as ccount FROM challenge_progress WHERE user_id = %s AND is_completed = 1",
        (user_id,),
        fetchone=True
    )
    challenges_count = challenges_count_row['ccount'] if challenges_count_row else 0

    newly_earned = []
    
    for ach in unearned:
        earned = False
        ctype = ach['criteria_type']
        cval = ach['criteria_value']
        
        if ctype == 'streak':
            if streak >= cval:
                earned = True
        elif ctype == 'hydration_streak':
            if (stats and stats['hydration_target_days'] or 0) >= cval:
                earned = True
        elif ctype == 'sleep_count':
            if (stats and stats['good_sleep_days'] or 0) >= cval:
                earned = True
        elif ctype == 'exercise_count':
            if (stats and stats['exercise_days'] or 0) >= cval:
                earned = True
        elif ctype == 'challenges_completed':
            if challenges_count >= cval:
                earned = True
        elif ctype == 'all_categories_day':
            if (stats and stats['all_categories_days'] or 0) >= cval:
                earned = True

        if earned:
            try:
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                execute_query(
                    "INSERT INTO user_achievements (user_id, achievement_id, earned_at) VALUES (%s, %s, %s)",
                    (user_id, ach['id'], now_str),
                    commit=True
                )
                newly_earned.append(ach['name'])
            except Exception:
                pass  # Ignore duplicate insert race condition if any
                
    return newly_earned
