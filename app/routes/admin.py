from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app.utils.decorators import admin_required
from app.services.admin_analytics import get_admin_analytics_summary
from app.models.db import execute_query

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    analytics = get_admin_analytics_summary()
    return render_template('admin/dashboard.html', analytics=analytics)

@admin_bp.route('/users')
@admin_required
def users():
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
    )
    return render_template('admin/users.html', students=students)

@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = execute_query("SELECT * FROM users WHERE id = %s AND role = 'student'", (user_id,), fetchone=True)
    if not user:
        flash("Student account not found.", "danger")
        return redirect(url_for('admin.users'))
        
    new_status = 0 if user['is_active'] else 1
    execute_query("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id), commit=True)
    
    status_str = "activated" if new_status else "deactivated"
    flash(f"Student account '{user['username']}' has been {status_str}.", "success")
    return redirect(url_for('admin.users'))

@admin_bp.route('/tips', methods=['GET', 'POST'])
@admin_required
def tips():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()
        
        if not category or not content:
            flash("Category and tip content are required.", "danger")
        else:
            execute_query(
                "INSERT INTO wellness_tips (category, content, is_active) VALUES (%s, %s, 1)",
                (category, content),
                commit=True
            )
            flash("New wellness tip added successfully!", "success")
            return redirect(url_for('admin.tips'))
            
    tips_list = execute_query("SELECT * FROM wellness_tips ORDER BY id DESC", fetchall=True)
    return render_template('admin/tips.html', tips=tips_list)

@admin_bp.route('/tips/delete/<int:tip_id>', methods=['POST'])
@admin_required
def delete_tip(tip_id):
    execute_query("DELETE FROM wellness_tips WHERE id = %s", (tip_id,), commit=True)
    flash("Wellness tip deleted.", "success")
    return redirect(url_for('admin.tips'))

@admin_bp.route('/challenges', methods=['GET', 'POST'])
@admin_required
def challenges():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        challenge_type = request.form.get('challenge_type', 'daily')
        points = int(request.form.get('points', 20))
        
        if not title or not description:
            flash("Title and description are required.", "danger")
        else:
            execute_query(
                "INSERT INTO challenges (title, description, challenge_type, points, is_active) VALUES (%s, %s, %s, %s, 1)",
                (title, description, challenge_type, points),
                commit=True
            )
            flash("New challenge created successfully!", "success")
            return redirect(url_for('admin.challenges'))

    challenges_list = execute_query("SELECT * FROM challenges ORDER BY id DESC", fetchall=True)
    return render_template('admin/challenges.html', challenges=challenges_list)

@admin_bp.route('/challenges/toggle/<int:challenge_id>', methods=['POST'])
@admin_required
def toggle_challenge(challenge_id):
    ch = execute_query("SELECT * FROM challenges WHERE id = %s", (challenge_id,), fetchone=True)
    if ch:
        new_status = 0 if ch['is_active'] else 1
        execute_query("UPDATE challenges SET is_active = %s WHERE id = %s", (new_status, challenge_id), commit=True)
        flash(f"Challenge '{ch['title']}' status updated.", "success")
    return redirect(url_for('admin.challenges'))

@admin_bp.route('/challenges/delete/<int:challenge_id>', methods=['POST'])
@admin_required
def delete_challenge(challenge_id):
    execute_query("DELETE FROM challenges WHERE id = %s", (challenge_id,), commit=True)
    flash("Challenge deleted.", "success")
    return redirect(url_for('admin.challenges'))
