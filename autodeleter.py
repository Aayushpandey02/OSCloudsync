import os
import time
from datetime import datetime, timedelta
import threading

WATCH_FOLDER = 'watch_folder'
DELETE_AFTER_DAYS = 10  # days of inactivity

def auto_delete_old_files():
    while True:
        now = time.time()
        cutoff_time = now - (DELETE_AFTER_DAYS * 86400)  # 10 days in seconds

        for root, dirs, files in os.walk(WATCH_FOLDER):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    last_modified = os.path.getmtime(filepath)
                    if last_modified < cutoff_time:
                        os.remove(filepath)
                        print(f"🗑️ Deleted due to inactivity: {filepath}")
                except Exception as e:
                    print(f"❌ Error checking/deleting file {filepath}: {e}")

        time.sleep(86400)  # Check once every 24 hours

def start_auto_deleter():
    thread = threading.Thread(target=auto_delete_old_files, daemon=True)
    thread.start()
