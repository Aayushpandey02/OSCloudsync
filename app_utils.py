# app_utils.py
import time
from flask_socketio import socketio  # Ensure socketio is imported correctly
from threading import Lock

log_lock = Lock()
logs = []
stats = {"synced": 0, "deleted": 0, "errors": 0, "last_sync": "Never"}

def log_event(message, status):
    with log_lock:
        entry = {
            "message": message,
            "status": status,
            "timestamp": time.strftime("%H:%M:%S")
        }
        logs.insert(0, entry)
        if len(logs) > 100:
            logs.pop()
        socketio.emit("log_update", entry)

def update_stats(key):
    stats[key] += 1
    if key == "synced":
        stats["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
    socketio.emit("stats_update", stats)
