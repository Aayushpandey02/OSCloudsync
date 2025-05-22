from flask import Flask, render_template, request, redirect, url_for, session
import threading, time, os, logging, psutil, webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from cleanup import cleanup_old_files

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERNAME = "admin"
PASSWORD = "admin123"

sync_running = True
sync_logs = []
sync_errors = []

# Directories
WATCH_FOLDER = 'watch_folder'
logs_folder = 'logs'

# Ensure folders exist
os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(logs_folder, exist_ok=True)

# Logging setup
logging.basicConfig(filename=os.path.join(logs_folder, 'sync.log'), level=logging.INFO)

def is_cpu_busy(threshold=70):
    return psutil.cpu_percent(interval=1) > threshold

def upload_file(file_path):
    try:
        if is_cpu_busy():
            log_entry = {'file': file_path, 'status': 'Skipped - CPU busy', 'time': timestamp()}
            sync_logs.append(log_entry)
            logging.info(f"{log_entry}")
            return
        time.sleep(1)  # Simulate upload
        log_entry = {'file': file_path, 'status': 'Uploaded', 'time': timestamp()}
        sync_logs.append(log_entry)
        logging.info(f"{log_entry}")
    except Exception as e:
        err_entry = {'file': file_path, 'error': str(e), 'time': timestamp()}
        sync_errors.append(err_entry)
        logging.error(f"{err_entry}")

def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class BackupHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not sync_running:
            return
        upload_file(event.src_path)

    def on_created(self, event):
        if event.is_directory or not sync_running:
            return
        upload_file(event.src_path)

    def on_deleted(self, event):
        log_entry = {'file': event.src_path, 'status': 'Deleted', 'time': timestamp()}
        sync_logs.append(log_entry)
        logging.info(f"{log_entry}")

    def on_moved(self, event):
        log_entry = {'file': event.dest_path, 'status': 'Moved', 'time': timestamp()}
        sync_logs.append(log_entry)
        logging.info(f"{log_entry}")

def start_monitor():
    observer = Observer()
    observer.schedule(BackupHandler(), path=WATCH_FOLDER, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', logs=sync_logs, running=sync_running, errors=sync_errors)

@app.route('/toggle-sync', methods=['POST'])
def toggle_sync():
    global sync_running
    sync_running = not sync_running
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/test-upload', methods=['POST'])
def test_upload():
    dummy_file = os.path.join(WATCH_FOLDER, 'test_sync.txt')
    with open(dummy_file, 'w') as f:
        f.write('Test content')
    return "Test file created."

def auto_cleanup_runner():
    while True:
        print("🧹 Running automatic cleanup...")
        cleanup_old_files(WATCH_FOLDER, 20)  # Cleanup files older than 20 days
        time.sleep(86400)  # Run once per day

def print_login_url():
    time.sleep(1)  # Allow Flask to start
    url = "http://127.0.0.1:5000/login"
    print(f"\n🚀 Flask app is live!\n🔗 Login here: {url}\n")
    webbrowser.open(url)

# Start background tasks
cleanup_thread = threading.Thread(target=auto_cleanup_runner, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    threading.Thread(target=start_monitor, daemon=True).start()
    threading.Thread(target=print_login_url, daemon=True).start()
    app.run(debug=True, port=5000)
