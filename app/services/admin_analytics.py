from datetime import date, timedelta
import pandas as pd
from app.models.db import execute_query

def get_admin_analytics_summary():
    """
    Computes system-wide aggregate and anonymized analytics for administrators.
    Excludes all individual user identifiers to guarantee student privacy.
    """
    # 1. Total & Active Student Counts
    user_counts = execute_query(
        """
        SELECT 
            COUNT(*) as total_students,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_students
        FROM users WHERE role = 'student'
        """,
        fetchone=True
    )
    
    total_students = user_counts['total_students'] if user_counts else 0
    active_students = user_counts['active_students'] if user_counts else 0

    # 2. Aggregated Daily Wellness Metrics (Past 30 Days)
    thirty_days_ago = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    records = execute_query(
        """
        SELECT record_date, sleep_hours, water_glasses, study_hours, mood, stress_level, wellness_score
        FROM wellness_records
        WHERE record_date >= %s
        """,
        (thirty_days_ago,),
        fetchall=True
    )
    
    if records:
        df = pd.DataFrame(records)
        avg_sleep = float(df['sleep_hours'].mean()) if pd.notnull(df['sleep_hours'].mean()) else 0.0
        avg_water = float(df['water_glasses'].mean()) if pd.notnull(df['water_glasses'].mean()) else 0.0
        avg_study = float(df['study_hours'].mean()) if pd.notnull(df['study_hours'].mean()) else 0.0
        avg_score = float(df['wellness_score'].mean()) if pd.notnull(df['wellness_score'].mean()) else 0.0
        
        # Mood Distribution Count
        mood_counts = df['mood'].value_counts().to_dict()
        mood_dist = [
            int(mood_counts.get(5, 0)), # Very Happy
            int(mood_counts.get(4, 0)), # Happy
            int(mood_counts.get(3, 0)), # Neutral
            int(mood_counts.get(2, 0)), # Sad
            int(mood_counts.get(1, 0))  # Very Sad
        ]
        
        # Stress Distribution Count
        stress_counts = df['stress_level'].value_counts().to_dict()
        stress_dist = [
            int(stress_counts.get(1, 0)), # Very Low
            int(stress_counts.get(2, 0)), # Low
            int(stress_counts.get(3, 0)), # Moderate
            int(stress_counts.get(4, 0)), # High
            int(stress_counts.get(5, 0))  # Very High
        ]
    else:
        avg_sleep, avg_water, avg_study, avg_score = 0.0, 0.0, 0.0, 0.0
        mood_dist = [0, 0, 0, 0, 0]
        stress_dist = [0, 0, 0, 0, 0]

    # 3. Challenge Completion Stats
    ch_stats = execute_query(
        """
        SELECT 
            c.title,
            COUNT(cp.id) as completion_count
        FROM challenges c
        LEFT JOIN challenge_progress cp ON c.id = cp.challenge_id AND cp.is_completed = 1
        GROUP BY c.id, c.title
        ORDER BY completion_count DESC
        """,
        fetchall=True
    )
    
    challenge_labels = [row['title'] for row in ch_stats] if ch_stats else []
    challenge_data = [int(row['completion_count']) for row in ch_stats] if ch_stats else []

    # 4. Return Structured Anonymized Dictionary for Admin Dashboard
    return {
        'total_students': total_students,
        'active_students': active_students,
        'avg_sleep': round(avg_sleep, 1),
        'avg_water': round(avg_water, 1),
        'avg_study': round(avg_study, 1),
        'avg_score': round(avg_score, 1),
        'mood_dist': mood_dist,
        'stress_dist': stress_dist,
        'challenge_labels': challenge_labels,
        'challenge_data': challenge_data
    }
