from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.db import execute_query
from app.utils.validation import validate_registration

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = validate_registration(username, email, password, confirm_password)
        
        if not errors:
            # Check if username or email already exists
            existing_user = execute_query(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email),
                fetchone=True
            )
            if existing_user:
                errors.append("Username or email address is already registered.")
                
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html', username=username, email=email)
            
        password_hash = generate_password_hash(password)
        try:
            user_id = execute_query(
                "INSERT INTO users (username, email, password_hash, role, total_points, is_active) VALUES (%s, %s, %s, 'student', 0, 1)",
                (username, email, password_hash),
                commit=True
            )
            flash('Registration successful! Please log in to continue.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html', username=username, email=email)

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '')
        
        if not login_input or not password:
            flash('Please enter both email/username and password.', 'warning')
            return render_template('auth/login.html', login_input=login_input)
            
        user = execute_query(
            "SELECT * FROM users WHERE email = %s OR username = %s",
            (login_input.lower(), login_input),
            fetchone=True
        )
        
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email/username or password.', 'danger')
            return render_template('auth/login.html', login_input=login_input)
            
        if not user.get('is_active', 1):
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return render_template('auth/login.html', login_input=login_input)
            
        # Clear existing session & set authenticated session parameters
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        
        flash(f'Welcome back, {user["username"]}!', 'success')
        
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
