import random
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.utils.decorators import student_required
from app.utils.validation import validate_wellness_input
from app.utils.bmi import calculate_bmi, get_integrated_health_assessment
from app.services.ml_service import predict_health_status, predict_lifestyle_risk
from app.services.wellness import get_today_record, log_daily_wellness
from app.services.gamification import calculate_current_streak, check_and_award_achievements
from app.services.analytics import get_student_analytics_data
from app.services.gamification import add_user_points, POINTS_MAP
from app.models.db import execute_query

student_bp = Blueprint('student', __name__)

@student_bp.route('/body-metrics', methods=['GET', 'POST'])
@student_required
def body_metrics():
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    
    if request.method == 'POST':
        height_raw = request.form.get('height', '').strip()
        weight_raw = request.form.get('weight', '').strip()
        gender = request.form.get('gender', (user.get('gender') if user else 'Female') or 'Female').strip()
        if gender not in ('Female', 'Male'):
            gender = 'Female'
        
        errors = []
        try:
            height = float(height_raw)
            if not (50 <= height <= 250):
                errors.append("Height must be between 50 cm and 250 cm.")
        except (ValueError, TypeError):
            errors.append("Please enter a valid numeric value for height.")
            
        try:
            weight = float(weight_raw)
            if not (20 <= weight <= 300):
                errors.append("Weight must be between 20 kg and 300 kg.")
        except (ValueError, TypeError):
            errors.append("Please enter a valid numeric value for weight.")
            
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('bmi_setup.html', user=user, height=height_raw, weight=weight_raw, gender=gender)
            
        bmi_res = calculate_bmi(height, weight)
        if not bmi_res:
            flash("Could not calculate BMI with provided metrics.", "danger")
            return render_template('bmi_setup.html', user=user, height=height_raw, weight=weight_raw, gender=gender)
            
        # Run ML Model 1: Body Metrics Health Status Classifier (Dataset 1)
        ml_status = predict_health_status(gender=gender, height_cm=height, weight_kg=weight)
        ml_health_status = ml_status.get('predicted_label') if ml_status.get('success') else None
        
        # Check if optional lifestyle questionnaire was completed
        ml_lifestyle_risk = None
        include_lifestyle = request.form.get('include_lifestyle') == '1'
        if include_lifestyle:
            try:
                lifestyle_payload = {
                    'Gender': gender,
                    'Age': float(request.form.get('age', 21)),
                    'Height': height,
                    'Weight': weight,
                    'family_history_with_overweight': request.form.get('family_history', 'no'),
                    'FAVC': request.form.get('favc', 'no'),
                    'FCVC': float(request.form.get('fcvc', 2.0)),
                    'NCP': float(request.form.get('ncp', 3.0)),
                    'CAEC': request.form.get('caec', 'Sometimes'),
                    'SMOKE': request.form.get('smoke', 'no'),
                    'CH2O': float(request.form.get('ch2o', 2.0)),
                    'SCC': request.form.get('scc', 'no'),
                    'FAF': float(request.form.get('faf', 1.0)),
                    'TUE': float(request.form.get('tue', 1.0)),
                    'CALC': request.form.get('calc', 'Sometimes'),
                    'MTRANS': request.form.get('mtrans', 'Public_Transportation')
                }
                ml_ls_res = predict_lifestyle_risk(lifestyle_payload)
                if ml_ls_res.get('success'):
                    ml_lifestyle_risk = ml_ls_res.get('predicted_label')
            except Exception:
                ml_lifestyle_risk = None

        # Update users table
        execute_query(
            """UPDATE users 
               SET height = %s, weight = %s, gender = %s, bmi = %s, bmi_category = %s, 
                   ml_health_status = %s, ml_lifestyle_risk = %s 
               WHERE id = %s""",
            (height, weight, gender, bmi_res['bmi'], bmi_res['category'], ml_health_status, ml_lifestyle_risk, user_id),
            commit=True
        )
        
        # Store entry in bmi_history
        execute_query(
            """INSERT INTO bmi_history 
               (user_id, height, weight, bmi, bmi_category, ml_health_status, ml_lifestyle_risk) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, height, weight, bmi_res['bmi'], bmi_res['category'], ml_health_status, ml_lifestyle_risk),
            commit=True
        )
        
        flash_msg = f"Body metrics saved! BMI: {bmi_res['bmi_formatted']} ({bmi_res['category']})"
        if ml_health_status:
            flash_msg += f" | ML Health Status: {ml_health_status}"
        flash(flash_msg, "success")
        return redirect(url_for('student.dashboard'))
        
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None
    assessment = get_integrated_health_assessment(
        user.get('height'), user.get('weight'), gender=(user.get('gender') or 'Female')
    ) if bmi_info else None
    
    bmi_history = execute_query(
        "SELECT * FROM bmi_history WHERE user_id = %s ORDER BY recorded_at DESC LIMIT 7",
        (user_id,),
        fetchall=True
    ) or []
    
    return render_template(
        'bmi_setup.html',
        user=user,
        bmi_info=bmi_info,
        assessment=assessment,
        bmi_history=bmi_history
    )

@student_bp.route('/api/bmi/assess', methods=['POST'])
@student_required
def api_bmi_assess():
    """
    JSON API endpoint for real-time BMI and ML health prediction.
    Accepts validated inputs, performs mathematical BMI & ML inferences, returns structured JSON.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON payload in request.'}), 400
        
    height_raw = data.get('height')
    weight_raw = data.get('weight')
    gender = data.get('gender', 'Female')
    lifestyle_data = data.get('lifestyle')
    
    try:
        height = float(height_raw)
        weight = float(weight_raw)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Height and weight must be valid numeric values.'}), 400
        
    if not (40 <= height <= 300) or not (15 <= weight <= 400):
        return jsonify({'success': False, 'error': 'Height must be between 40-300 cm and weight between 15-400 kg.'}), 400
        
    assessment = get_integrated_health_assessment(height, weight, gender=gender, lifestyle_data=lifestyle_data)
    if not assessment.get('success'):
        return jsonify(assessment), 400
        
    return jsonify(assessment), 200

@student_bp.route('/dashboard')
@student_required
def dashboard():
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    today_record = get_today_record(user_id)
    streak = calculate_current_streak(user_id)
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None
    
    # Select rotating daily tip
    tips = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1", fetchall=True)
    daily_tip = random.choice(tips) if tips else None
    
    today_str = date.today().strftime('%Y-%m-%d')
    # Active challenges and student completion status
    challenges = execute_query(
        """
        SELECT c.*, 
               CASE WHEN cp.id IS NOT NULL AND cp.is_completed = 1 THEN 1 ELSE 0 END as is_completed
        FROM challenges c
        LEFT JOIN challenge_progress cp ON c.id = cp.challenge_id 
             AND cp.user_id = %s AND cp.start_date = %s
        WHERE c.is_active = 1 AND c.challenge_type = 'daily'
        LIMIT 3
        """,
        (user_id, today_str),
        fetchall=True
    )
    
    bmi_history = execute_query(
        "SELECT * FROM bmi_history WHERE user_id = %s ORDER BY recorded_at ASC LIMIT 7",
        (user_id,),
        fetchall=True
    ) or []

    return render_template(
        'dashboard.html',
        user=user,
        today_record=today_record,
        streak=streak,
        daily_tip=daily_tip,
        challenges=challenges,
        bmi_info=bmi_info,
        bmi_history=bmi_history
    )

@student_bp.route('/wellness', methods=['GET', 'POST'])
@student_required
def log_wellness():
    user_id = session['user_id']
    
    if request.method == 'POST':
        errors = validate_wellness_input(request.form)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('wellness/log.html', record=request.form)
            
        result = log_daily_wellness(user_id, request.form)
        
        flash("Daily wellness metrics saved successfully!", "success")
        if result.get('new_badges'):
            for bname in result['new_badges']:
                flash(f"🏆 Achievement Unlocked: {bname}!", "info")
                
        return redirect(url_for('student.dashboard'))
        
    today_record = get_today_record(user_id)
    return render_template('wellness/log.html', record=today_record or {})

@student_bp.route('/wellness/history')
@student_required
def wellness_history():
    user_id = session['user_id']
    records = execute_query(
        "SELECT * FROM wellness_records WHERE user_id = %s ORDER BY record_date DESC",
        (user_id,),
        fetchall=True
    )
    return render_template('wellness/history.html', records=records)

@student_bp.route('/tips')
@student_required
def tips():
    category = request.args.get('category', '').strip()
    if category and category != 'All':
        tips_list = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1 AND category = %s ORDER BY id DESC", (category,), fetchall=True)
    else:
        tips_list = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1 ORDER BY id DESC", fetchall=True)
        
    categories = execute_query("SELECT DISTINCT category FROM wellness_tips WHERE is_active = 1", fetchall=True)
    cat_names = [c['category'] for c in categories]
    
    return render_template('tips/index.html', tips=tips_list, categories=cat_names, current_category=category)

@student_bp.route('/challenges')
@student_required
def challenges():
    user_id = session['user_id']
    today_str = date.today().strftime('%Y-%m-%d')
    active_challenges = execute_query(
        """
        SELECT c.*, 
               CASE WHEN cp.id IS NOT NULL AND cp.is_completed = 1 THEN 1 ELSE 0 END as is_completed
        FROM challenges c
        LEFT JOIN challenge_progress cp ON c.id = cp.challenge_id 
             AND cp.user_id = %s AND cp.start_date = %s
        WHERE c.is_active = 1
        ORDER BY c.challenge_type ASC, c.id DESC
        """,
        (user_id, today_str),
        fetchall=True
    )
    return render_template('challenges/index.html', challenges=active_challenges)

@student_bp.route('/challenges/complete/<int:challenge_id>', methods=['POST'])
@student_required
def complete_challenge(challenge_id):
    user_id = session['user_id']
    ch = execute_query("SELECT * FROM challenges WHERE id = %s AND is_active = 1", (challenge_id,), fetchone=True)
    
    if not ch:
        flash("Challenge not found or inactive.", "danger")
        return redirect(url_for('student.challenges'))
        
    today_str = date.today().strftime('%Y-%m-%d')
    # Check if already completed today
    existing = execute_query(
        "SELECT id FROM challenge_progress WHERE user_id = %s AND challenge_id = %s AND start_date = %s",
        (user_id, challenge_id, today_str),
        fetchone=True
    )
    
    if existing:
        flash("You have already completed this challenge today!", "info")
    else:
        execute_query(
            "INSERT INTO challenge_progress (user_id, challenge_id, start_date, completion_date, is_completed) VALUES (%s, %s, %s, %s, 1)",
            (user_id, challenge_id, today_str, today_str),
            commit=True
        )
        points = ch['points']
        add_user_points(user_id, points)
        new_badges = check_and_award_achievements(user_id)
        
        flash(f"🎉 Challenge completed! +{points} points awarded.", "success")
        if new_badges:
            for b in new_badges:
                flash(f"🏆 Achievement Unlocked: {b}!", "info")
                
    return redirect(url_for('student.challenges'))

@student_bp.route('/progress')
@student_required
def progress():
    user_id = session['user_id']
    days = int(request.args.get('days', 7))
    chart_data, insights = get_student_analytics_data(user_id, days=days)
    return render_template('progress.html', chart_data=chart_data, insights=insights, current_days=days)

@student_bp.route('/api/my-charts')
@student_required
def api_my_charts():
    user_id = session['user_id']
    days = int(request.args.get('days', 7))
    chart_data, _ = get_student_analytics_data(user_id, days=days)
    return jsonify(chart_data)

@student_bp.route('/profile')
@student_required
def profile():
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    streak = calculate_current_streak(user_id)
    
    # Achievements
    all_achievements = execute_query(
        """
        SELECT a.*, 
               CASE WHEN ua.id IS NOT NULL THEN 1 ELSE 0 END as unlocked,
               ua.earned_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = %s
        ORDER BY unlocked DESC, a.id ASC
        """,
        (user_id,),
        fetchall=True
    )
    
    unlocked_count = sum(1 for a in all_achievements if a['unlocked'])
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None
    
    return render_template(
        'profile.html',
        user=user,
        streak=streak,
        achievements=all_achievements,
        unlocked_count=unlocked_count,
        total_achievements=len(all_achievements),
        bmi_info=bmi_info
    )
