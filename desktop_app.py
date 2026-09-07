import sys
import os
import time
import socket
import threading
import webbrowser
from app import create_app

def find_free_port():
    """Find a free port on localhost."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def run_flask(port):
    """Run Flask server in background thread."""
    app = create_app('development')
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

def wait_for_server(port, timeout=10):
    """Wait until Flask server is listening on specified port."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.2)
    return False

def main():
    port = find_free_port()
    app_url = f"http://127.0.0.1:{port}"
    
    print("=" * 65)
    print("  Wellvia - Student Wellness Companion (Desktop Application)")
    print("=" * 65)
    print(f"[+] Starting local application server at {app_url} ...")

    # Start Flask in daemon thread
    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()

    if not wait_for_server(port):
        print("[-] Error: Failed to start backend application server.")
        sys.exit(1)

    print("[+] Server ready! Launching Desktop Window ...")

    # Try PyWebView for native frameless/windowed GUI
    try:
        import webview
        icon_path = os.path.join(os.path.dirname(__file__), 'app', 'static', 'img', 'icon-512.png')
        
        window = webview.create_window(
            title='Wellvia - Student Wellness Companion',
            url=app_url,
            width=1200,
            height=820,
            min_size=(400, 600),
            resizable=True,
            confirm_close=False
        )
        print("[+] Wellvia Desktop GUI Window Launched successfully.")
        webview.start(private_mode=False)
    except ImportError:
        print("[!] pywebview not installed. Launching standalone App Window via Web Browser...")
        # Open in App Mode (Edge/Chrome app window) if available
        try:
            # Try launching Chrome/Edge in app mode
            import subprocess
            chrome_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            launched = False
            for path in chrome_paths:
                if os.path.exists(path):
                    subprocess.Popen([path, f"--app={app_url}", "--window-size=1200,820"])
                    launched = True
                    print(f"[+] Launched standalone app window using {os.path.basename(path)}")
                    break
            
            if not launched:
                webbrowser.open(app_url)
        except Exception as e:
            webbrowser.open(app_url)
            
        print("\nPress Ctrl+C in this terminal window to stop the server when done.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[+] Wellvia Desktop Application closed.")

if __name__ == '__main__':
    main()
