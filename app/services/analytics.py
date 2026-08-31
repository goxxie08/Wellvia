from datetime import date, timedelta
import pandas as pd
from app.models.db import execute_query

def get_student_analytics_data(user_id, days=7):
    """
    Retrieves and processes historical wellness records for a student using Pandas.
    Generates continuous date sequences and structures JSON-ready chart series and pattern insights.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    # Query database for student records in date range
    records = execute_query(
        """
        SELECT record_date, sleep_hours, water_glasses, exercise_duration,
               mood, stress_level, study_hours, wellness_score
        FROM wellness_records
        WHERE user_id = %s AND record_date >= %s AND record_date <= %s
        ORDER BY record_date ASC
        """,
        (user_id, start_date, end_date),
        fetchall=True
    )
    
    # Create complete date range dataframe with Pandas
    date_range = pd.date_range(start=start_date, end=end_date)
    df_dates = pd.DataFrame({'record_date': date_range.date})
    
    if records:
        df_records = pd.DataFrame(records)
        # Convert date column
        df_records['record_date'] = pd.to_datetime(df_records['record_date']).dt.date
        df = pd.merge(df_dates, df_records, on='record_date', how='left')
    else:
        df = df_dates.copy()
        for col in ['sleep_hours', 'water_glasses', 'exercise_duration', 'mood', 'stress_level', 'study_hours', 'wellness_score']:
            df[col] = None

    # Format labels (e.g. 'Mon 12/08' or '08 Aug')
    labels = [d.strftime('%a %d %b') for d in df['record_date']]
    
    # Extract series handling NaN values for JSON
    def clean_series(series):
        return [float(x) if pd.notnull(x) else None for x in series]

    chart_data = {
        'labels': labels,
        'sleep': clean_series(df['sleep_hours']),
        'water': clean_series(df['water_glasses']),
        'exercise': clean_series(df['exercise_duration']),
        'mood': clean_series(df['mood']),
        'stress': clean_series(df['stress_level']),
        'study': clean_series(df['study_hours']),
        'score': clean_series(df['wellness_score'])
    }
    
    # Calculate habit completion rates for Doughnut chart
    non_null_counts = {
        'Sleep': df['sleep_hours'].notnull().sum(),
        'Hydration': df['water_glasses'].notnull().sum(),
        'Exercise': df['exercise_duration'].notnull().sum(),
        'Mood': df['mood'].notnull().sum(),
        'Stress': df['stress_level'].notnull().sum(),
        'Study': df['study_hours'].notnull().sum()
    }
    chart_data['habit_completion'] = {
        'labels': list(non_null_counts.keys()),
        'counts': [int(x) for x in non_null_counts.values()]
    }

    # Generate pattern observations
    insights = []
    if len(df.dropna(subset=['sleep_hours', 'stress_level'])) >= 3:
        avg_stress_good_sleep = df[df['sleep_hours'] >= 7]['stress_level'].mean()
        avg_stress_low_sleep = df[df['sleep_hours'] < 7]['stress_level'].mean()
        if pd.notnull(avg_stress_good_sleep) and pd.notnull(avg_stress_low_sleep):
            if avg_stress_good_sleep < avg_stress_low_sleep:
                insights.append("Your average stress level was lower on days when you logged at least 7 hours of sleep.")

    if len(df.dropna(subset=['exercise_duration', 'mood'])) >= 3:
        avg_mood_exercise = df[df['exercise_duration'] >= 20]['mood'].mean()
        avg_mood_no_exercise = df[df['exercise_duration'] < 20]['mood'].mean()
        if pd.notnull(avg_mood_exercise) and pd.notnull(avg_mood_no_exercise):
            if avg_mood_exercise > avg_mood_no_exercise:
                insights.append("Your reported mood was generally higher on days with 20+ minutes of exercise.")

    if not insights:
        insights.append("Log your wellness metrics consistently for 3-5 days to unlock personalized habit observations!")

    return chart_data, insights
