import os
from flask import current_app, send_from_directory, request, has_app_context

def get_dist_dir():
    """Returns the absolute path to the compiled React frontend dist directory."""
    if has_app_context() and current_app:
        return os.path.abspath(os.path.join(current_app.root_path, '..', 'frontend', 'dist'))
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base_dir, 'frontend', 'dist')

def is_spa_available():
    """Checks whether the compiled React SPA entry point (index.html) exists."""
    index_file = os.path.join(get_dist_dir(), 'index.html')
    return os.path.exists(index_file)

def should_serve_spa():
    """
    Determines if the incoming request should be routed to the React SPA entry point.
    Returns True for GET requests when the SPA build exists and legacy template is not requested.
    """
    if not is_spa_available():
        return False
    if request.method != 'GET':
        return False
    # Support explicit legacy template testing via query parameter or header
    if request.args.get('legacy') == '1' or request.headers.get('X-Legacy-Template') == '1':
        return False
    return True

def serve_spa():
    """Serves the React single-page application index.html entry point."""
    dist_dir = get_dist_dir()
    return send_from_directory(dist_dir, 'index.html')
