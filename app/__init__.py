from flask import Flask, render_template, redirect, url_for, session, send_from_directory, request, jsonify
import os
from config.settings import config
from app.models.db import close_db
from app.utils.spa import is_spa_available, serve_spa, get_dist_dir

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Teardown database connection after request
    app.teardown_appcontext(close_db)
    
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    dist_dir = get_dist_dir()

    @app.route('/assets/<path:filename>')
    def serve_frontend_assets(filename):
        assets_dir = os.path.join(dist_dir, 'assets')
        target_file = os.path.join(assets_dir, filename)
        if os.path.exists(target_file):
            return send_from_directory(assets_dir, filename)
        return "Asset not found", 404

    @app.route('/')
    def index():
        if is_spa_available():
            return serve_spa()
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    # Explicit top-level React SPA routes
    for r_path in ['/login', '/register', '/forgot-password', '/admin']:
        def make_handler():
            def spa_route_view():
                if is_spa_available():
                    return serve_spa()
                if 'user_id' in session:
                    return redirect(url_for('student.dashboard'))
                return redirect(url_for('auth.login'))
            return spa_route_view
        app.add_url_rule(
            r_path,
            endpoint=f'spa_{r_path.strip("/").replace("-", "_")}',
            view_func=make_handler(),
            methods=['GET']
        )

    # PWA & Static Asset Routes
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest.json', mimetype='application/manifest+json')

    @app.route('/service-worker.js')
    def service_worker():
        response = send_from_directory(os.path.join(app.root_path, 'static'), 'service-worker.js', mimetype='application/javascript')
        response.headers['Service-Worker-Allowed'] = '/'
        return response

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/offline')
    def offline():
        return render_template('offline.html')

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        # 1. API routes must always return JSON errors, never HTML
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'API endpoint not found'}), 404

        # 2. Missing static assets must return 404, never index.html
        static_extensions = (
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.eot', '.map', '.json', '.txt', '.webp', '.webmanifest'
        )
        if (request.path.startswith('/assets/') or 
            request.path.startswith('/static/') or 
            any(request.path.lower().endswith(ext) for ext in static_extensions)):
            return "Asset not found", 404

        # 3. Valid GET navigation fallback for client-side React routes
        if is_spa_available() and request.method == 'GET':
            return serve_spa()

        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
