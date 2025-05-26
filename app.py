import os
import time
from threading import Thread, Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from supabase_sync import upload_file_to_supabase, delete_file_from_supabase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

log_lock = Lock()
logs = []
stats = {"synced": 0, "deleted": 0, "errors": 0, "last_sync": "Never"}
watching = False
observer = None

# === Configuration ===
WATCH_FOLDER = 'watch_folder'
BUCKET_NAME = 'user-files'
DEST_FOLDER = 'synced'

os.makedirs(WATCH_FOLDER, exist_ok=True)

# === File System Event Handler ===
class SupabaseSyncHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            # Add small delay to ensure file is fully written
            time.sleep(0.1)
            self._sync_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            # Add small delay to ensure file is fully written
            time.sleep(0.1)
            self._sync_file(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
            relative_path = os.path.relpath(event.src_path, WATCH_FOLDER)
            supabase_path = f"{DEST_FOLDER}/{relative_path}"
            try:
                delete_file_from_supabase(BUCKET_NAME, supabase_path)
                log_event(f"Deleted from Supabase: {supabase_path}", "deleted")
                stats["deleted"] += 1
                update_stats()
            except Exception as e:
                log_event(f"Error deleting {supabase_path}: {str(e)}", "error")
                stats["errors"] += 1
                update_stats()
    
    def _sync_file(self, filepath):
        try:
            # Check if file still exists (in case of quick delete)
            if not os.path.exists(filepath):
                return
                
            relative_path = os.path.relpath(filepath, WATCH_FOLDER)
            supabase_path = f"{DEST_FOLDER}/{relative_path}"
            
            print(f"Syncing file: {filepath} -> {supabase_path}")
            upload_file_to_supabase(BUCKET_NAME, filepath, supabase_path)
            log_event(f"Uploaded to Supabase: {supabase_path}", "synced")
            stats["synced"] += 1
            stats["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
            update_stats()
        except Exception as e:
            log_event(f"Error uploading {filepath}: {str(e)}", "error")
            stats["errors"] += 1
            update_stats()

# === Logging and Stats ===
def log_event(message, status):
    print(f"[{status.upper()}] {message}")  # Console logging for debugging
    with log_lock:
        log_entry = {
            "message": message,
            "status": status,
            "timestamp": time.strftime("%H:%M:%S")
        }
        logs.insert(0, log_entry)
        if len(logs) > 100:
            logs.pop()
        
        # Emit to all connected clients
        socketio.emit("log_update", log_entry)

def update_stats():
    print(f"Stats updated: {stats}")  # Console logging for debugging
    # Emit to all connected clients
    socketio.emit("stats_update", stats)

# === Flask Routes ===
@app.route('/')
def index():
    return render_template('index.html')

# === WebSocket Events ===
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Send current stats and recent logs to newly connected client
    emit('stats_update', stats)
    with log_lock:
        for log_entry in reversed(logs[-10:]):  # Send last 10 logs
            emit('log_update', log_entry)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('start_watch')
def start_watching():
    global watching, observer
    print("Received start_watch event")
    
    if not watching:
        try:
            event_handler = SupabaseSyncHandler()
            observer = Observer()
            observer.schedule(event_handler, path=WATCH_FOLDER, recursive=True)
            observer.start()
            watching = True
            log_event(f"Started watching folder: {WATCH_FOLDER}", "info")
            print("Observer started successfully")
        except Exception as e:
            log_event(f"Error starting watcher: {str(e)}", "error")
            stats["errors"] += 1
            update_stats()
    else:
        log_event("Already watching files", "info")

@socketio.on('stop_watch')
def stop_watching():
    global watching, observer
    print("Received stop_watch event")
    
    if watching and observer:
        try:
            observer.stop()
            observer.join()
            observer = None
            watching = False
            log_event("Stopped watching files", "info")
            print("Observer stopped successfully")
        except Exception as e:
            log_event(f"Error stopping watcher: {str(e)}", "error")
            stats["errors"] += 1
            update_stats()
    else:
        log_event("Not currently watching", "info")

@socketio.on('clear_logs')
def clear_logs():
    print("Received clear_logs event")
    with log_lock:
        logs.clear()
        socketio.emit("logs_cleared")
    log_event("Logs cleared", "info")

# === Entry Point ===
if __name__ == '__main__':
    print(f"Starting Supabase Sync Monitor...")
    print(f"Watch folder: {os.path.abspath(WATCH_FOLDER)}")
    print(f"Access the dashboard at: http://localhost:5000")
    
    # Import request for socketio events
    from flask import request
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)