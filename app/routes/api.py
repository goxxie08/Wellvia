import random
from datetime import date, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.db import execute_query
from app.utils.validation import validate_registration, validate_wellness_input
from app.utils.bmi import calculate_bmi, get_integrated_health_assessment
from app.services.ml_service import predict_health_status, predict_lifestyle_risk, DISCLAIMER_TEXT
from app.services.wellness import get_today_record, log_daily_wellness
from app.services.gamification import calculate_current_streak, check_and_award_achievements, add_user_points, POINTS_MAP
from app.services.analytics import get_student_analytics_data
from app.services.admin_analytics import get_admin_analytics_summary
from app.services.chat_service import generate_wellness_chat_reply, MAX_MESSAGE_LENGTH

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ============================================================================
# Auth Decorators for JSON APIs
# ============================================================================

def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated

def api_student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        if session.get('role') != 'student':
            return jsonify({'success': False, 'error': 'Access denied: student privileges required.'}), 403
        return f(*args, **kwargs)
    return decorated

def api_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Access denied: administrator privileges required.'}), 403
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# 1. AUTHENTICATION & SESSION ENDPOINTS
# ============================================================================

@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """Returns currently authenticated user session data or 401 if unauthenticated."""
    if 'user_id' not in session:
        return jsonify({'authenticated': False, 'user': None}), 200

    user_id = session['user_id']
    user = execute_query(
        """SELECT id, username, email, role, total_points, height, weight, gender,
                  bmi, bmi_category, ml_health_status, ml_lifestyle_risk, is_active, created_at
           FROM users WHERE id = %s""",
        (user_id,),
        fetchone=True
    )
    if not user or not user.get('is_active', 1):
        session.clear()
        return jsonify({'authenticated': False, 'user': None}), 200

    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'total_points': user['total_points'],
            'height': user['height'],
            'weight': user['weight'],
            'gender': user.get('gender') or 'Female',
            'bmi': user['bmi'],
            'bmi_category': user['bmi_category'],
            'ml_health_status': user['ml_health_status'],
            'ml_lifestyle_risk': user['ml_lifestyle_risk'],
            'needs_metrics': (user['role'] == 'student' and (user['height'] is None or user['weight'] is None))
        }
    }), 200

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """Authenticates user credentials and establishes server session."""
    data = request.get_json(silent=True) or {}
    login_input = str(data.get('login_input', '')).strip()
    password = str(data.get('password', ''))

    if not login_input or not password:
        return jsonify({'success': False, 'error': 'Please provide both email/username and password.'}), 400

    user = execute_query(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(%s) OR LOWER(username) = LOWER(%s)",
        (login_input, login_input),
        fetchone=True
    )

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'error': 'Invalid email/username or password.'}), 401

    if not user.get('is_active', 1):
        return jsonify({'success': False, 'error': 'Your account has been deactivated. Please contact an administrator.'}), 403

    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']
    session['role'] = user['role']

    needs_metrics = (user['role'] == 'student' and (user.get('height') is None or user.get('weight') is None))
    redirect_target = '/admin' if user['role'] == 'admin' else ('/body-metrics' if needs_metrics else '/dashboard')

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user["username"]}!',
        'redirect': redirect_target,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'total_points': user['total_points'],
            'needs_metrics': needs_metrics
        }
    }), 200

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """Registers a new student user."""
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    confirm_password = str(data.get('confirm_password', ''))

    errors = validate_registration(username, email, password, confirm_password)

    if not errors:
        existing_user = execute_query(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)",
            (username, email),
            fetchone=True
        )
        if existing_user:
            errors.append("Username or email address is already registered.")

    if errors:
        return jsonify({'success': False, 'errors': errors, 'error': errors[0]}), 400

    password_hash = generate_password_hash(password)
    try:
        user_id = execute_query(
            "INSERT INTO users (username, email, password_hash, role, total_points, is_active) VALUES (%s, %s, %s, 'student', 0, 1)",
            (username, email, password_hash),
            commit=True
        )
        return jsonify({
            'success': True,
            'message': 'Registration successful! You may now log in.',
            'user_id': user_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': 'Registration failed due to a server error. Please try again.'}), 500

@api_bp.route('/auth/logout', methods=['POST', 'GET'])
def api_logout():
    """Destroys current authenticated session."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out securely.'}), 200

@api_bp.route('/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    """Simulates password reset instructions for provided email."""
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()

    if not email:
        return jsonify({'success': False, 'error': 'Please enter a valid email address.'}), 400

    return jsonify({
        'success': True,
        'message': 'If an account is associated with that email address, reset instructions have been sent.'
    }), 200


# ============================================================================
# 2. STUDENT DASHBOARD & WELLNESS METRICS
# ============================================================================

@api_bp.route('/student/dashboard', methods=['GET'])
@api_student_required
def api_student_dashboard():
    """Returns aggregated data for student dashboard."""
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    today_record = get_today_record(user_id)
    streak = calculate_current_streak(user_id)
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None

    # Rotating daily tip
    tips = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1", fetchall=True)
    daily_tip = random.choice(tips) if tips else None

    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    week_start_str = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    challenges = execute_query(
        """
        SELECT c.*, 
               CASE WHEN cp.id IS NOT NULL AND cp.is_completed = 1 THEN 1 ELSE 0 END as is_completed
        FROM challenges c
        LEFT JOIN challenge_progress cp ON c.id = cp.challenge_id 
             AND cp.user_id = %s 
             AND (
                 (c.challenge_type = 'daily' AND (cp.start_date = %s OR cp.completion_date = %s))
                 OR (c.challenge_type = 'weekly' AND (cp.start_date >= %s OR cp.completion_date >= %s))
             )
        WHERE c.is_active = 1 AND c.challenge_type = 'daily'
        LIMIT 3
        """,
        (user_id, today_str, today_str, week_start_str, week_start_str),
        fetchall=True
    ) or []

    bmi_history = execute_query(
        "SELECT * FROM bmi_history WHERE user_id = %s ORDER BY recorded_at ASC LIMIT 7",
        (user_id,),
        fetchall=True
    ) or []

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'total_points': user['total_points'],
            'height': user['height'],
            'weight': user['weight'],
            'gender': user.get('gender') or 'Female',
            'bmi': user['bmi'],
            'bmi_category': user['bmi_category'],
            'ml_health_status': user['ml_health_status'],
            'ml_lifestyle_risk': user['ml_lifestyle_risk'],
        },
        'today_record': today_record,
        'streak': streak,
        'daily_tip': daily_tip,
        'challenges': challenges,
        'bmi_info': bmi_info,
        'bmi_history': bmi_history
    }), 200

@api_bp.route('/student/body-metrics', methods=['GET', 'POST'])
@api_student_required
def api_body_metrics():
    """Handles GET (fetch status/history) and POST (save metrics & run ML)."""
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        height_raw = data.get('height')
        weight_raw = data.get('weight')
        gender = str(data.get('gender', (user.get('gender') if user else 'Female') or 'Female')).strip()
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
            return jsonify({'success': False, 'errors': errors, 'error': errors[0]}), 400

        bmi_res = calculate_bmi(height, weight)
        if not bmi_res:
            return jsonify({'success': False, 'error': 'Could not calculate BMI with provided metrics.'}), 400

        # ML Model 1: Body Metrics Health Status Classifier
        ml_status = predict_health_status(gender=gender, height_cm=height, weight_kg=weight)
        ml_health_status = ml_status.get('predicted_label') if ml_status.get('success') else None

        # ML Model 2: Lifestyle risk assessment if provided
        ml_lifestyle_risk = None
        lifestyle_payload = data.get('lifestyle_payload')
        if data.get('include_lifestyle') and lifestyle_payload:
            try:
                lifestyle_payload['Gender'] = gender
                lifestyle_payload['Height'] = height
                lifestyle_payload['Weight'] = weight
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

        updated_user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
        assessment = get_integrated_health_assessment(
            height, weight, gender=gender, lifestyle_data=lifestyle_payload if data.get('include_lifestyle') else None
        )
        if assessment:
            assessment['ml_health_status'] = ml_health_status
            assessment['ml_lifestyle_risk'] = ml_lifestyle_risk
            assessment['category'] = bmi_res['category']
            assessment['standard_category'] = bmi_res['category']
            assessment['health_tip'] = bmi_res['health_tip']
            assessment['standard_tip'] = bmi_res['health_tip']
            assessment['bmi_info'] = bmi_res

        bmi_history = execute_query(
            "SELECT * FROM bmi_history WHERE user_id = %s ORDER BY recorded_at DESC LIMIT 10",
            (user_id,),
            fetchall=True
        ) or []

        return jsonify({
            'success': True,
            'message': f"Metrics saved successfully! BMI: {bmi_res['bmi_formatted']} ({bmi_res['category']})",
            'user': updated_user,
            'bmi_info': bmi_res,
            'assessment': assessment,
            'bmi_history': bmi_history,
            'ml_health_status': ml_health_status,
            'ml_lifestyle_risk': ml_lifestyle_risk,
            'ml_details': ml_status
        }), 200

    # GET request
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None
    assessment = get_integrated_health_assessment(
        user.get('height'), user.get('weight'), gender=(user.get('gender') or 'Female')
    ) if bmi_info else None

    if assessment and user:
        assessment['ml_health_status'] = user.get('ml_health_status')
        assessment['ml_lifestyle_risk'] = user.get('ml_lifestyle_risk')
        assessment['category'] = assessment.get('standard_category')
        assessment['health_tip'] = assessment.get('standard_tip')
        assessment['bmi_info'] = bmi_info
        if user.get('ml_lifestyle_risk') and not assessment.get('ml_lifestyle'):
            assessment['ml_lifestyle'] = {
                'success': True,
                'predicted_label': user['ml_lifestyle_risk'],
                'risk_level': 'Elevated' if any(w in str(user['ml_lifestyle_risk']) for w in ['Obesity', 'Overweight', 'High']) else 'Normal',
                'explanation': f"Multi-factor lifestyle assessment indicates {user['ml_lifestyle_risk']} risk profile based on recorded habits."
            }

    bmi_history = execute_query(
        "SELECT * FROM bmi_history WHERE user_id = %s ORDER BY recorded_at DESC LIMIT 10",
        (user_id,),
        fetchall=True
    ) or []

    return jsonify({
        'success': True,
        'user': user,
        'bmi_info': bmi_info,
        'assessment': assessment,
        'bmi_history': bmi_history
    }), 200

@api_bp.route('/student/wellness/today', methods=['GET'])
@api_student_required
def api_wellness_today():
    """Fetches today's logged record for the authenticated student."""
    user_id = session['user_id']
    record = get_today_record(user_id)
    return jsonify({'success': True, 'record': record}), 200

@api_bp.route('/student/wellness', methods=['POST'])
@api_student_required
def api_log_wellness():
    """Logs daily wellness metrics, recalculates score, streaks, and awards achievements."""
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}

    errors = validate_wellness_input(data)
    if errors:
        return jsonify({'success': False, 'errors': errors, 'error': errors[0]}), 400

    result = log_daily_wellness(user_id, data)
    today_record = get_today_record(user_id)
    return jsonify({
        'success': True,
        'message': 'Daily wellness metrics saved successfully!',
        'result': result,
        'record': today_record
    }), 200

@api_bp.route('/student/wellness/history', methods=['GET'])
@api_student_required
def api_wellness_history():
    """Retrieves chronological wellness records for student."""
    user_id = session['user_id']
    records = execute_query(
        "SELECT * FROM wellness_records WHERE user_id = %s ORDER BY record_date DESC",
        (user_id,),
        fetchall=True
    ) or []
    return jsonify({'success': True, 'records': records}), 200

@api_bp.route('/student/tips', methods=['GET'])
@api_student_required
def api_student_tips():
    """Returns curated wellness tips with optional category filter."""
    category = request.args.get('category', '').strip()
    if category and category != 'All':
        tips_list = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1 AND category = %s ORDER BY id DESC", (category,), fetchall=True)
    else:
        tips_list = execute_query("SELECT * FROM wellness_tips WHERE is_active = 1 ORDER BY id DESC", fetchall=True)

    categories = execute_query("SELECT DISTINCT category FROM wellness_tips WHERE is_active = 1", fetchall=True) or []
    cat_names = [c['category'] for c in categories]

    return jsonify({
        'success': True,
        'tips': tips_list or [],
        'categories': cat_names,
        'current_category': category
    }), 200

@api_bp.route('/student/challenges', methods=['GET'])
@api_student_required
def api_student_challenges():
    """Returns all active challenges along with student completion status."""
    user_id = session['user_id']
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    week_start_str = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    active_challenges = execute_query(
        """
        SELECT c.*, 
               CASE WHEN cp.id IS NOT NULL AND cp.is_completed = 1 THEN 1 ELSE 0 END as is_completed
        FROM challenges c
        LEFT JOIN challenge_progress cp ON c.id = cp.challenge_id 
             AND cp.user_id = %s 
             AND (
                 (c.challenge_type = 'daily' AND (cp.start_date = %s OR cp.completion_date = %s))
                 OR (c.challenge_type = 'weekly' AND (cp.start_date >= %s OR cp.completion_date >= %s))
             )
        WHERE c.is_active = 1
        ORDER BY c.challenge_type ASC, c.id DESC
        """,
        (user_id, today_str, today_str, week_start_str, week_start_str),
        fetchall=True
    ) or []

    return jsonify({'success': True, 'challenges': active_challenges}), 200

@api_bp.route('/student/challenges/<int:challenge_id>/complete', methods=['POST'])
@api_student_required
def api_complete_challenge(challenge_id):
    """Marks a challenge completed, adds points, and evaluates achievement unlocks."""
    user_id = session['user_id']
    ch = execute_query("SELECT * FROM challenges WHERE id = %s AND is_active = 1", (challenge_id,), fetchone=True)

    if not ch:
        return jsonify({'success': False, 'error': 'Challenge not found or inactive.'}), 404

    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    week_start_str = (today - timedelta(days=6)).strftime('%Y-%m-%d')

    if ch['challenge_type'] == 'weekly':
        existing = execute_query(
            "SELECT id FROM challenge_progress WHERE user_id = %s AND challenge_id = %s AND (start_date >= %s OR completion_date >= %s) AND is_completed = 1",
            (user_id, challenge_id, week_start_str, week_start_str),
            fetchone=True
        )
        if existing:
            return jsonify({'success': False, 'error': 'You have already completed this weekly challenge this week!'}), 400
    else:
        existing = execute_query(
            "SELECT id FROM challenge_progress WHERE user_id = %s AND challenge_id = %s AND (start_date = %s OR completion_date = %s) AND is_completed = 1",
            (user_id, challenge_id, today_str, today_str),
            fetchone=True
        )
        if existing:
            return jsonify({'success': False, 'error': 'You have already completed this challenge today!'}), 400

    execute_query(
        "INSERT INTO challenge_progress (user_id, challenge_id, start_date, completion_date, is_completed) VALUES (%s, %s, %s, %s, 1)",
        (user_id, challenge_id, today_str, today_str),
        commit=True
    )
    points = ch['points']
    add_user_points(user_id, points)
    new_badges = check_and_award_achievements(user_id)

    # Fetch updated user points
    user = execute_query("SELECT total_points FROM users WHERE id = %s", (user_id,), fetchone=True)

    return jsonify({
        'success': True,
        'message': f"Challenge completed! +{points} points awarded.",
        'points_awarded': points,
        'total_points': user['total_points'] if user else 0,
        'new_badges': new_badges or []
    }), 200

@api_bp.route('/student/progress', methods=['GET'])
@api_student_required
def api_student_progress():
    """Returns analytics chart datasets and insights for progress page."""
    user_id = session['user_id']
    days = int(request.args.get('days', 7))
    if days not in (7, 14, 30):
        days = 7
    chart_data, insights = get_student_analytics_data(user_id, days=days)
    return jsonify({
        'success': True,
        'days': days,
        'chart_data': chart_data,
        'insights': insights,
        'overview': chart_data.get('overview'),
        'analysis': chart_data.get('analysis'),
        'areas_to_improve': chart_data.get('areas_to_improve'),
        'recent_logs': chart_data.get('recent_logs', [])
    }), 200

@api_bp.route('/student/profile', methods=['GET'])
@api_student_required
def api_student_profile():
    """Returns student profile details, streak, and full list of badges."""
    user_id = session['user_id']
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    streak = calculate_current_streak(user_id)

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
    ) or []

    unlocked_count = sum(1 for a in all_achievements if a.get('unlocked'))
    bmi_info = calculate_bmi(user.get('height'), user.get('weight')) if user and user.get('height') and user.get('weight') else None

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'total_points': user['total_points'],
            'height': user['height'],
            'weight': user['weight'],
            'gender': user.get('gender') or 'Female',
            'created_at': str(user.get('created_at', ''))
        },
        'streak': streak,
        'achievements': all_achievements,
        'unlocked_count': unlocked_count,
        'total_achievements': len(all_achievements),
        'bmi_info': bmi_info
    }), 200


# ============================================================================
# 3. ADMINISTRATOR ENDPOINTS
# ============================================================================

@api_bp.route('/admin/analytics', methods=['GET'])
@api_admin_required
def api_admin_analytics():
    """Returns aggregate student wellness population metrics."""
    analytics = get_admin_analytics_summary()
    return jsonify({'success': True, 'analytics': analytics}), 200

@api_bp.route('/admin/users', methods=['GET'])
@api_admin_required
def api_admin_users():
    """Returns list of student users and their logging counts."""
    students = execute_query(
        """
        SELECT u.id, u.username, u.email, u.total_points, u.is_active, u.created_at,
               COUNT(r.id) as log_count
        FROM users u
        LEFT JOIN wellness_records r ON u.id = r.user_id
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.created_at DESC
        """,
        fetchall=True
    ) or []
    return jsonify({'success': True, 'students': students}), 200

@api_bp.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@api_admin_required
def api_admin_toggle_user(user_id):
    """Toggles active/deactive status of student account."""
    user = execute_query("SELECT * FROM users WHERE id = %s AND role = 'student'", (user_id,), fetchone=True)
    if not user:
        return jsonify({'success': False, 'error': 'Student account not found.'}), 404

    new_status = 0 if user['is_active'] else 1
    execute_query("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id), commit=True)
    status_str = "activated" if new_status else "deactivated"
    return jsonify({
        'success': True,
        'is_active': new_status,
        'message': f"Account '{user['username']}' has been {status_str}."
    }), 200

@api_bp.route('/admin/tips', methods=['GET', 'POST'])
@api_admin_required
def api_admin_tips():
    """Fetches all tips or creates a new one."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        category = str(data.get('category', '')).strip()
        content = str(data.get('content', '')).strip()

        if not category or not content:
            return jsonify({'success': False, 'error': 'Category and tip content are required.'}), 400

        tip_id = execute_query(
            "INSERT INTO wellness_tips (category, content, is_active) VALUES (%s, %s, 1)",
            (category, content),
            commit=True
        )
        return jsonify({'success': True, 'message': 'New wellness tip added successfully!', 'tip_id': tip_id}), 201

    tips_list = execute_query("SELECT * FROM wellness_tips ORDER BY id DESC", fetchall=True) or []
    return jsonify({'success': True, 'tips': tips_list}), 200

@api_bp.route('/admin/tips/<int:tip_id>', methods=['DELETE'])
@api_admin_required
def api_admin_delete_tip(tip_id):
    """Deletes a wellness tip."""
    execute_query("DELETE FROM wellness_tips WHERE id = %s", (tip_id,), commit=True)
    return jsonify({'success': True, 'message': 'Wellness tip deleted.'}), 200

@api_bp.route('/admin/challenges', methods=['GET', 'POST'])
@api_admin_required
def api_admin_challenges():
    """Fetches all challenges or creates a new one."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        title = str(data.get('title', '')).strip()
        description = str(data.get('description', '')).strip()
        challenge_type = str(data.get('challenge_type', 'daily'))
        try:
            points = int(data.get('points', 20))
        except (ValueError, TypeError):
            points = 20

        if not title or not description:
            return jsonify({'success': False, 'error': 'Title and description are required.'}), 400

        challenge_id = execute_query(
            "INSERT INTO challenges (title, description, challenge_type, points, is_active) VALUES (%s, %s, %s, %s, 1)",
            (title, description, challenge_type, points),
            commit=True
        )
        return jsonify({'success': True, 'message': 'Challenge created successfully!', 'challenge_id': challenge_id}), 201

    challenges_list = execute_query("SELECT * FROM challenges ORDER BY id DESC", fetchall=True) or []
    return jsonify({'success': True, 'challenges': challenges_list}), 200

@api_bp.route('/admin/challenges/<int:challenge_id>/toggle', methods=['POST'])
@api_admin_required
def api_admin_toggle_challenge(challenge_id):
    """Toggles active/inactive state of a challenge."""
    ch = execute_query("SELECT * FROM challenges WHERE id = %s", (challenge_id,), fetchone=True)
    if not ch:
        return jsonify({'success': False, 'error': 'Challenge not found.'}), 404

    new_status = 0 if ch['is_active'] else 1
    execute_query("UPDATE challenges SET is_active = %s WHERE id = %s", (new_status, challenge_id), commit=True)
    return jsonify({
        'success': True,
        'is_active': new_status,
        'message': f"Challenge '{ch['title']}' status updated."
    }), 200

@api_bp.route('/admin/challenges/<int:challenge_id>', methods=['DELETE'])
@api_admin_required
def api_admin_delete_challenge(challenge_id):
    """Deletes a challenge."""
    execute_query("DELETE FROM challenges WHERE id = %s", (challenge_id,), commit=True)
    return jsonify({'success': True, 'message': 'Challenge deleted.'}), 200


# ============================================================================
# 4. AI WELLNESS CHATBOT (Official Google GenAI SDK Proxy)
# ============================================================================

@api_bp.route('/chat/message', methods=['POST'])
@api_login_required
def api_chat_message():
    """
    Secure endpoint for the AI Wellness Chatbot using official google-genai SDK.
    Protects user secrets: GEMINI_API_KEY is read strictly from the server environment.
    Personalizes responses using the student's dashboard metrics and logged habits.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'error': 'Invalid request payload. Expected JSON object.'}), 400

    raw_msg = data.get('message')
    if not raw_msg or not isinstance(raw_msg, str) or not raw_msg.strip():
        return jsonify({'success': False, 'error': 'Message content cannot be empty.'}), 400

    user_msg = raw_msg.strip()
    if len(user_msg) > MAX_MESSAGE_LENGTH:
        return jsonify({
            'success': False,
            'error': f'Message exceeds maximum allowed length of {MAX_MESSAGE_LENGTH} characters.'
        }), 400

    history = data.get('history')
    if history is not None and not isinstance(history, list):
        return jsonify({'success': False, 'error': 'Conversation history must be a list if provided.'}), 400

    # Retrieve real-time dashboard context for personalization
    user_context = None
    user_id = session.get('user_id')
    if user_id:
        try:
            user = execute_query(
                "SELECT id, username, email, total_points, height, weight, gender, bmi, bmi_category, ml_health_status, ml_lifestyle_risk FROM users WHERE id = %s",
                (user_id,),
                fetchone=True
            )
            if user:
                today_record = get_today_record(user_id)
                streak = calculate_current_streak(user_id)
                user_context = {
                    'username': user.get('username'),
                    'height': user.get('height'),
                    'weight': user.get('weight'),
                    'gender': user.get('gender'),
                    'bmi': user.get('bmi'),
                    'bmi_category': user.get('bmi_category'),
                    'ml_health_status': user.get('ml_health_status'),
                    'ml_lifestyle_risk': user.get('ml_lifestyle_risk'),
                    'total_points': user.get('total_points'),
                    'today_record': today_record,
                    'streak': streak,
                }
        except Exception:
            # Graceful non-blocking fallback if context retrieval encounters an error
            pass

    chat_res = generate_wellness_chat_reply(
        message=user_msg,
        history=history,
        user_context=user_context
    )
    return jsonify(chat_res), 200

