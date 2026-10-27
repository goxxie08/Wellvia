from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from app.utils.spa import should_serve_spa, serve_spa

def login_required(f):
    """Decorator to enforce that user is logged in, or serve SPA if active."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if should_serve_spa():
            return serve_spa()
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to enforce student role, or serve SPA entry point on client GETs."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if should_serve_spa():
            return serve_spa()
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to enforce admin role, or serve SPA entry point on client GETs."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if should_serve_spa():
            return serve_spa()
        if 'user_id' not in session:
            flash('Please log in to access administrative pages.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
