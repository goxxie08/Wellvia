from datetime import date, timedelta
import pandas as pd
from app.models.db import execute_query

# Categorical definitions for Mood and Stress
MOOD_MAPPINGS = {
    5: {'label': 'Great', 'emoji': '😊', 'description': 'Very Happy / Energized'},
    4: {'label': 'Good', 'emoji': '🙂', 'description': 'Good / Content'},
    3: {'label': 'Neutral', 'emoji': '😐', 'description': 'Neutral / Okay'},
    2: {'label': 'Low', 'emoji': '🙁', 'description': 'Low / Down'},
    1: {'label': 'Sad', 'emoji': '😞', 'description': 'Very Sad / Depressed'},
}

STRESS_MAPPINGS = {
    1: {'label': 'Calm', 'emoji': '🧘', 'description': 'Very Low / Calm'},
    2: {'label': 'Low', 'emoji': '😌', 'description': 'Low Stress'},
    3: {'label': 'Moderate', 'emoji': '😐', 'description': 'Moderate Stress'},
    4: {'label': 'High', 'emoji': '😰', 'description': 'High / Pressured'},
    5: {'label': 'Severe', 'emoji': '😫', 'description': 'Severe / Overwhelmed'},
}

def get_student_analytics_data(user_id, days=7):
    """
    Retrieves and processes historical wellness records for a student using Pandas.
    Generates continuous date sequences and structures JSON-ready chart series,
    compact overview statistics, deterministic wellness analysis, and actionable areas to improve.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    # Query database for student records in date range
    records = execute_query(
        """
        SELECT record_date, sleep_hours, sleep_quality, water_glasses,
               exercise_type, exercise_duration, exercise_intensity,
               mood, stress_level, study_hours, study_sessions, study_subject,
               wellness_score
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
    
    metric_cols = [
        'sleep_hours', 'sleep_quality', 'water_glasses', 'exercise_duration',
        'mood', 'stress_level', 'study_hours', 'wellness_score'
    ]
    
    if records:
        df_records = pd.DataFrame(records)
        df_records['record_date'] = pd.to_datetime(df_records['record_date']).dt.date
        df = pd.merge(df_dates, df_records, on='record_date', how='left')
    else:
        df = df_dates.copy()
        for col in metric_cols + ['exercise_type', 'exercise_intensity', 'study_subject']:
            df[col] = None

    # Format labels (e.g. 'Mon 12 Oct' and '2026-10-12')
    labels = [d.strftime('%a %d %b') for d in df['record_date']]
    dates_iso = [d.isoformat() for d in df['record_date']]
    
    # Helper to clean numeric series preserving None for JSON null
    def clean_series(series):
        return [float(x) if pd.notnull(x) else None for x in series]

    def clean_int_series(series):
        return [int(x) if pd.notnull(x) else None for x in series]

    # Categorical arrays for mood and stress
    mood_categories = []
    for val in df['mood']:
        if pd.notnull(val) and int(val) in MOOD_MAPPINGS:
            entry = MOOD_MAPPINGS[int(val)].copy()
            entry['value'] = int(val)
            mood_categories.append(entry)
        else:
            mood_categories.append(None)

    stress_categories = []
    for val in df['stress_level']:
        if pd.notnull(val) and int(val) in STRESS_MAPPINGS:
            entry = STRESS_MAPPINGS[int(val)].copy()
            entry['value'] = int(val)
            stress_categories.append(entry)
        else:
            stress_categories.append(None)

    # Base chart data
    chart_data = {
        'labels': labels,
        'dates': dates_iso,
        'sleep': clean_series(df['sleep_hours']),
        'water': clean_int_series(df['water_glasses']),
        'exercise': clean_int_series(df['exercise_duration']),
        'mood': clean_int_series(df['mood']),
        'mood_categories': mood_categories,
        'stress': clean_int_series(df['stress_level']),
        'stress_categories': stress_categories,
        'study': clean_series(df['study_hours']),
        'score': clean_int_series(df['wellness_score'])
    }
    
    # Calculate habit completion rates for Doughnut chart (kept for backward compatibility)
    non_null_counts = {
        'Sleep': int(df['sleep_hours'].notnull().sum()),
        'Hydration': int(df['water_glasses'].notnull().sum()),
        'Exercise': int(df['exercise_duration'].notnull().sum()),
        'Mood': int(df['mood'].notnull().sum()),
        'Stress': int(df['stress_level'].notnull().sum()),
        'Study': int(df['study_hours'].notnull().sum())
    }
    chart_data['habit_completion'] = {
        'labels': list(non_null_counts.keys()),
        'counts': list(non_null_counts.values())
    }

    # Extract historical BMI and Weight trajectory (preserved for backward compatibility & tests)
    bmi_records = execute_query(
        """
        SELECT recorded_at, height, weight, bmi, bmi_category, ml_health_status
        FROM bmi_history
        WHERE user_id = %s
        ORDER BY recorded_at ASC
        LIMIT 20
        """,
        (user_id,),
        fetchall=True
    )
    if bmi_records:
        chart_data['bmi_history'] = {
            'labels': [str(r['recorded_at'])[:10] for r in bmi_records],
            'bmi': [round(float(r['bmi']), 2) for r in bmi_records],
            'weight': [round(float(r['weight']), 1) for r in bmi_records],
            'categories': [r['bmi_category'] for r in bmi_records],
            'ml_status': [r['ml_health_status'] or '' for r in bmi_records]
        }
    else:
        chart_data['bmi_history'] = {'labels': [], 'bmi': [], 'weight': [], 'categories': [], 'ml_status': []}

    # -------------------------------------------------------------
    # 1. WELLNESS OVERVIEW SUMMARY COMPUTATION
    # -------------------------------------------------------------
    valid_sleep = df['sleep_hours'].dropna()
    valid_water = df['water_glasses'].dropna()
    valid_exercise = df['exercise_duration'].dropna()
    valid_study = df['study_hours'].dropna()
    valid_stress = df['stress_level'].dropna()
    valid_mood = df['mood'].dropna()

    # Determine logged days count (days where at least one metric is present)
    any_metric_mask = (
        df['sleep_hours'].notnull() |
        df['water_glasses'].notnull() |
        df['exercise_duration'].notnull() |
        df['study_hours'].notnull() |
        df['stress_level'].notnull() |
        df['mood'].notnull()
    )
    logged_days_count = int(any_metric_mask.sum())

    # Sleep summary
    sleep_avg = round(float(valid_sleep.mean()), 1) if len(valid_sleep) > 0 else None
    
    # Water summary
    water_avg = round(float(valid_water.mean()), 1) if len(valid_water) > 0 else None
    
    # Exercise summary
    exercise_avg = round(float(valid_exercise.mean()), 1) if len(valid_exercise) > 0 else None
    exercise_total = int(valid_exercise.sum()) if len(valid_exercise) > 0 else None
    
    # Study summary
    study_avg = round(float(valid_study.mean()), 1) if len(valid_study) > 0 else None
    study_total = round(float(valid_study.sum()), 1) if len(valid_study) > 0 else None

    # Stress summary
    stress_avg = round(float(valid_stress.mean()), 1) if len(valid_stress) > 0 else None
    stress_label = None
    if stress_avg is not None:
        if stress_avg < 2.0:
            stress_label = "Calm / Very Low"
        elif stress_avg < 3.0:
            stress_label = "Low"
        elif stress_avg < 4.0:
            stress_label = "Moderate"
        else:
            stress_label = "High / Elevated"

    # Mood dominant pattern
    mood_dominant = None
    if len(valid_mood) > 0:
        mode_val = int(valid_mood.mode().iloc[0])
        mood_dominant = MOOD_MAPPINGS.get(mode_val, {}).get('label', 'Neutral') + ' ' + MOOD_MAPPINGS.get(mode_val, {}).get('emoji', '')

    overview = {
        'period_days': days,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'date_range_label': f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}",
        'logged_days_count': logged_days_count,
        'sleep': {
            'avg': sleep_avg,
            'days_logged': len(valid_sleep),
            'unit': 'hrs/night',
            'target': '7–9 hrs'
        },
        'water': {
            'avg': water_avg,
            'days_logged': len(valid_water),
            'unit': 'glasses/day',
            'target': '8 glasses (~2.0L)'
        },
        'exercise': {
            'avg': exercise_avg,
            'total': exercise_total,
            'days_logged': len(valid_exercise),
            'unit': 'mins/day',
            'target': '30+ mins'
        },
        'study': {
            'avg': study_avg,
            'total': study_total,
            'days_logged': len(valid_study),
            'unit': 'hrs/day',
            'target': '2–5 hrs'
        },
        'stress': {
            'avg': stress_avg,
            'label': stress_label,
            'days_logged': len(valid_stress),
            'unit': 'scale 1-5'
        },
        'mood': {
            'dominant': mood_dominant,
            'days_logged': len(valid_mood),
            'unit': 'category'
        }
    }
    chart_data['overview'] = overview

    # -------------------------------------------------------------
    # 2. YOUR WELLNESS ANALYSIS (DETERMINISTIC OBSERVATIONS)
    # -------------------------------------------------------------
    analysis = []

    # Sleep Analysis
    if len(valid_sleep) < 2:
        analysis.append({
            'key': 'sleep',
            'title': 'Sleep Duration & Rest',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'hrs',
            'logged_count': len(valid_sleep),
            'target_label': 'Target: 7–9 hrs',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Tracking your sleep duration for at least 2–3 consecutive nights will establish your baseline rest pattern.'
        })
    else:
        if sleep_avg < 7.0:
            analysis.append({
                'key': 'sleep',
                'title': 'Sleep Duration & Rest',
                'status': 'needs_improvement',
                'current_value': sleep_avg,
                'unit': 'hrs',
                'logged_count': len(valid_sleep),
                'target_label': 'Target: 7–9 hrs',
                'observation': f'Your recent sleep duration has averaged {sleep_avg} hours, which is below the recommended 7–9 hour target.',
                'recommendation': 'Try maintaining a consistent bedtime and allowing enough time for restful, uninterrupted sleep.'
            })
        elif sleep_avg > 9.5:
            analysis.append({
                'key': 'sleep',
                'title': 'Sleep Duration & Rest',
                'status': 'attention',
                'current_value': sleep_avg,
                'unit': 'hrs',
                'logged_count': len(valid_sleep),
                'target_label': 'Target: 7–9 hrs',
                'observation': f'Your recent sleep duration has averaged {sleep_avg} hours, which is on the higher side.',
                'recommendation': 'Ensure your sleep feels refreshing and balance extended rest with light daytime movement.'
            })
        else:
            analysis.append({
                'key': 'sleep',
                'title': 'Sleep Duration & Rest',
                'status': 'good',
                'current_value': sleep_avg,
                'unit': 'hrs',
                'logged_count': len(valid_sleep),
                'target_label': 'Target: 7–9 hrs',
                'observation': f'Your recent sleep duration is on track, averaging {sleep_avg} hours per night within your recommended target.',
                'recommendation': 'Maintain this steady bedtime routine to support daytime focus and physical recovery.'
            })

    # Water Analysis
    if len(valid_water) < 2:
        analysis.append({
            'key': 'water',
            'title': 'Daily Hydration',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'glasses',
            'logged_count': len(valid_water),
            'target_label': 'Target: 8 glasses',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Track your daily water glasses to receive personalized hydration insights.'
        })
    else:
        if water_avg < 6.0:
            analysis.append({
                'key': 'water',
                'title': 'Daily Hydration',
                'status': 'needs_improvement',
                'current_value': water_avg,
                'unit': 'glasses',
                'logged_count': len(valid_water),
                'target_label': 'Target: 8 glasses',
                'observation': f'Your logged water intake is averaging {water_avg} glasses daily, below your 8-glass daily goal.',
                'recommendation': 'Try drinking water at regular intervals throughout the day and keep a water bottle near your study space.'
            })
        elif water_avg < 8.0:
            analysis.append({
                'key': 'water',
                'title': 'Daily Hydration',
                'status': 'moderate',
                'current_value': water_avg,
                'unit': 'glasses',
                'logged_count': len(valid_water),
                'target_label': 'Target: 8 glasses',
                'observation': f'You are getting close to your hydration target with an average of {water_avg} glasses per day.',
                'recommendation': 'Adding just 1–2 more glasses during morning or study breaks will help you consistently hit your daily goal.'
            })
        else:
            analysis.append({
                'key': 'water',
                'title': 'Daily Hydration',
                'status': 'good',
                'current_value': water_avg,
                'unit': 'glasses',
                'logged_count': len(valid_water),
                'target_label': 'Target: 8 glasses',
                'observation': f'Great job! Your hydration is meeting your daily target with an average of {water_avg} glasses.',
                'recommendation': 'Maintain this healthy habit to keep your physical vitality and focus optimal.'
            })

    # Physical Activity Analysis
    if len(valid_exercise) < 2:
        analysis.append({
            'key': 'exercise',
            'title': 'Physical Activity & Movement',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'mins',
            'logged_count': len(valid_exercise),
            'target_label': 'Target: 30 mins/day',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Log your walks, workouts, or stretches to understand your daily activity level.'
        })
    else:
        if exercise_avg < 15.0:
            analysis.append({
                'key': 'exercise',
                'title': 'Physical Activity & Movement',
                'status': 'needs_improvement',
                'current_value': exercise_avg,
                'unit': 'mins',
                'logged_count': len(valid_exercise),
                'target_label': 'Target: 30 mins/day',
                'observation': f'You have logged relatively little physical activity recently, averaging {exercise_avg} minutes per logged day.',
                'recommendation': 'Consider adding a short walk, light stretching, or a movement break to your routine.'
            })
        elif exercise_avg < 30.0:
            analysis.append({
                'key': 'exercise',
                'title': 'Physical Activity & Movement',
                'status': 'moderate',
                'current_value': exercise_avg,
                'unit': 'mins',
                'logged_count': len(valid_exercise),
                'target_label': 'Target: 30 mins/day',
                'observation': f'You are maintaining regular movement, averaging {exercise_avg} active minutes on logged days.',
                'recommendation': 'Aim to gradually build towards 30 minutes of moderate activity like brisk walking or cycling.'
            })
        else:
            analysis.append({
                'key': 'exercise',
                'title': 'Physical Activity & Movement',
                'status': 'good',
                'current_value': exercise_avg,
                'unit': 'mins',
                'logged_count': len(valid_exercise),
                'target_label': 'Target: 30 mins/day',
                'observation': f'You have consistently stayed active, averaging {exercise_avg} minutes of exercise per logged day.',
                'recommendation': 'Keep up regular movement to boost your energy, cardiovascular health, and focus.'
            })

    # Stress Analysis
    if len(valid_stress) < 2:
        analysis.append({
            'key': 'stress',
            'title': 'Stress Level Management',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'scale 1-5',
            'logged_count': len(valid_stress),
            'target_label': 'Scale: 1 (Calm) – 5 (Severe)',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Checking in on your stress levels helps identify exam pressure patterns and maintain balance.'
        })
    else:
        if stress_avg >= 3.5:
            analysis.append({
                'key': 'stress',
                'title': 'Stress Level Management',
                'status': 'needs_improvement',
                'current_value': stress_avg,
                'unit': 'scale 1-5',
                'logged_count': len(valid_stress),
                'target_label': 'Scale: 1 (Calm) – 5 (Severe)',
                'observation': f'Your recent entries indicate elevated stress, averaging {stress_avg}/5 on your check-ins.',
                'recommendation': 'Consider taking a short break, practising a breathing exercise, or talking to someone you trust.'
            })
        elif stress_avg >= 2.5:
            analysis.append({
                'key': 'stress',
                'title': 'Stress Level Management',
                'status': 'moderate',
                'current_value': stress_avg,
                'unit': 'scale 1-5',
                'logged_count': len(valid_stress),
                'target_label': 'Scale: 1 (Calm) – 5 (Severe)',
                'observation': f'Your recent stress entries reflect moderate levels (averaging {stress_avg}/5) during this study period.',
                'recommendation': 'Schedule brief 5-minute mental pauses between demanding academic tasks to prevent tension buildup.'
            })
        else:
            analysis.append({
                'key': 'stress',
                'title': 'Stress Level Management',
                'status': 'good',
                'current_value': stress_avg,
                'unit': 'scale 1-5',
                'logged_count': len(valid_stress),
                'target_label': 'Scale: 1 (Calm) – 5 (Severe)',
                'observation': f'Your reported stress levels have been manageable and calm, averaging {stress_avg}/5.',
                'recommendation': 'Notice the habits and routines supporting your calm state and keep them in place.'
            })

    # Mood Analysis
    if len(valid_mood) < 2:
        analysis.append({
            'key': 'mood',
            'title': 'Emotional Mood Patterns',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'category',
            'logged_count': len(valid_mood),
            'target_label': 'Categories: Sad to Great',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Tracking your daily emotional state helps build meaningful emotional self-awareness.'
        })
    else:
        low_mood_count = int((valid_mood <= 2).sum())
        high_mood_count = int((valid_mood >= 4).sum())
        mood_total = len(valid_mood)
        
        if low_mood_count / mood_total >= 0.5:
            analysis.append({
                'key': 'mood',
                'title': 'Emotional Mood Patterns',
                'status': 'needs_improvement',
                'current_value': mood_dominant,
                'unit': 'category',
                'logged_count': mood_total,
                'target_label': 'Categories: Sad to Great',
                'observation': 'Your recent mood entries suggest that you may be experiencing some difficult or tiring days.',
                'recommendation': 'Consider making time for activities you enjoy, stepping outside, or reaching out for support if needed.'
            })
        elif high_mood_count / mood_total >= 0.5:
            analysis.append({
                'key': 'mood',
                'title': 'Emotional Mood Patterns',
                'status': 'good',
                'current_value': mood_dominant,
                'unit': 'category',
                'logged_count': mood_total,
                'target_label': 'Categories: Sad to Great',
                'observation': 'Your recent mood entries reflect generally positive, content, and energized days.',
                'recommendation': 'Celebrate your positive mindset and continue prioritizing balance in your daily routine.'
            })
        else:
            analysis.append({
                'key': 'mood',
                'title': 'Emotional Mood Patterns',
                'status': 'moderate',
                'current_value': mood_dominant,
                'unit': 'category',
                'logged_count': mood_total,
                'target_label': 'Categories: Sad to Great',
                'observation': 'Your recent mood entries indicate balanced and steady days overall.',
                'recommendation': 'Incorporate small moments of joy or relaxing breaks into your day to lift your spirits.'
            })

    # Study Habits Analysis
    if len(valid_study) < 2:
        analysis.append({
            'key': 'study',
            'title': 'Academic Study Habits',
            'status': 'insufficient_data',
            'current_value': None,
            'unit': 'hrs',
            'logged_count': len(valid_study),
            'target_label': 'Target: 2–5 hrs/day',
            'observation': 'Log a few days of wellness data to receive personalized insights.',
            'recommendation': 'Log your daily study hours to gain clear insights into your academic pacing and balance.'
        })
    else:
        if study_avg < 2.0:
            analysis.append({
                'key': 'study',
                'title': 'Academic Study Habits',
                'status': 'needs_improvement',
                'current_value': study_avg,
                'unit': 'hrs',
                'logged_count': len(valid_study),
                'target_label': 'Target: 2–5 hrs/day',
                'observation': f'Your logged study time has been lower than your goal, averaging {study_avg} hours per day.',
                'recommendation': 'Consider setting a manageable study target for tomorrow and taking regular breaks.'
            })
        elif study_avg > 7.0:
            analysis.append({
                'key': 'study',
                'title': 'Academic Study Habits',
                'status': 'attention',
                'current_value': study_avg,
                'unit': 'hrs',
                'logged_count': len(valid_study),
                'target_label': 'Target: 2–5 hrs/day',
                'observation': f'Your logged study time has been intensive, averaging {study_avg} hours daily.',
                'recommendation': 'Remember to protect your sleep and take regular breaks to prevent academic fatigue and burnout.'
            })
        else:
            analysis.append({
                'key': 'study',
                'title': 'Academic Study Habits',
                'status': 'good',
                'current_value': study_avg,
                'unit': 'hrs',
                'logged_count': len(valid_study),
                'target_label': 'Target: 2–5 hrs/day',
                'observation': f'Your study routine shows consistent dedication, averaging {study_avg} hours per day.',
                'recommendation': 'Keep pacing your learning sessions with the Pomodoro technique for sustained concentration.'
            })

    chart_data['analysis'] = analysis

    # -------------------------------------------------------------
    # 3. AREAS TO IMPROVE (PRIORITIZED TOP 1-2 ACTIONABLE HABITS)
    # -------------------------------------------------------------
    # Priority ranking weight: Sleep (1) -> Stress (2) -> Hydration (3) -> Exercise (4) -> Mood (5) -> Study (6)
    PRIORITY_WEIGHTS = {
        'sleep': 1,
        'stress': 2,
        'water': 3,
        'exercise': 4,
        'mood': 5,
        'study': 6
    }

    # Map candidate items that need improvement
    needs_imp = [item for item in analysis if item['status'] in ('needs_improvement', 'attention')]
    needs_imp.sort(key=lambda x: PRIORITY_WEIGHTS.get(x['key'], 99))

    areas_to_improve = []
    
    if needs_imp:
        for idx, item in enumerate(needs_imp[:2]):
            k = item['key']
            if k == 'sleep':
                areas_to_improve.append({
                    'habit': 'Sleep Consistency',
                    'priority': idx + 1,
                    'headline': 'Focus on improving your sleep consistency',
                    'reason': f'Your average sleep over the past {days} days was {sleep_avg} hours, below your recommended target.',
                    'action_step': 'Set a consistent bedtime tonight and turn off digital screens 30 minutes before sleep.'
                })
            elif k == 'stress':
                areas_to_improve.append({
                    'habit': 'Stress Relief',
                    'priority': idx + 1,
                    'headline': 'Incorporate regular stress relief breaks',
                    'reason': f'Your recent stress ratings averaged {stress_avg}/5 during this period.',
                    'action_step': 'Practice a 3-minute guided deep-breathing exercise or take a short walk between study sessions.'
                })
            elif k == 'water':
                areas_to_improve.append({
                    'habit': 'Daily Hydration',
                    'priority': idx + 1,
                    'headline': 'Work towards your daily hydration target',
                    'reason': f'Your average intake was {water_avg} glasses per day, below your 8-glass daily goal.',
                    'action_step': 'Drink one full glass of water upon waking and keep a filled water bottle at your desk.'
                })
            elif k == 'exercise':
                areas_to_improve.append({
                    'habit': 'Physical Movement',
                    'priority': idx + 1,
                    'headline': 'Try including short movement breaks in your routine',
                    'reason': f'Your logged activity averaged {exercise_avg} minutes daily over the past {days} days.',
                    'action_step': 'Take a 15-minute brisk walk outside or do gentle stretching during your study break.'
                })
            elif k == 'mood':
                areas_to_improve.append({
                    'habit': 'Emotional Well-being',
                    'priority': idx + 1,
                    'headline': 'Make space for restorative and uplifting activities',
                    'reason': 'Multiple recent check-ins reflect low mood or tiring days.',
                    'action_step': 'Dedicate 20 minutes today to an activity you genuinely enjoy or connect with a friend.'
                })
            elif k == 'study':
                areas_to_improve.append({
                    'habit': 'Study Pacing',
                    'priority': idx + 1,
                    'headline': 'Consider a manageable study schedule with regular breaks',
                    'reason': f'Your logged study time averaged {study_avg} hours per day.',
                    'action_step': 'Plan one focused 45-minute study block tomorrow followed by a 10-minute relaxing break.'
                })
    else:
        # Check if all logged metrics are healthy or if data is insufficient
        logged_metrics = [item for item in analysis if item['status'] != 'insufficient_data']
        if len(logged_metrics) >= 2 and all(m['status'] in ('good', 'moderate') for m in logged_metrics):
            areas_to_improve.append({
                'habit': 'Healthy Momentum',
                'priority': 1,
                'headline': 'Maintain your healthy wellness habits',
                'reason': 'All your tracked habits are currently within their configured healthy targets.',
                'action_step': 'Keep up your balanced routine and continue daily logging to sustain your progress and streak.',
                'is_all_good': True
            })
        else:
            areas_to_improve.append({
                'habit': 'Habit Logging',
                'priority': 1,
                'headline': 'Build your wellness baseline with daily logging',
                'reason': 'We need at least 2–3 days of logged habits to detect meaningful patterns and opportunities.',
                'action_step': 'Record your sleep, hydration, and movement today in the Wellness Tracker to unlock personalized advice.',
                'is_insufficient': True
            })

    chart_data['areas_to_improve'] = areas_to_improve

    # Keep recent raw logs for callers/tests that check user boundaries
    recent_logs = [dict(r) for r in records] if records else []
    chart_data['recent_logs'] = recent_logs

    # -------------------------------------------------------------
    # 4. PATTERN INSIGHTS (Preserved for backward compatibility)
    # -------------------------------------------------------------
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

