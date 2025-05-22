import os
import time
import logging
from datetime import datetime

WATCH_FOLDER = 'watch_folder'
DAYS_INACTIVE = 20
LOG_FILE = 'logs/deleted_files.log'

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def cleanup_old_files(folder_path, days_threshold=20):
    now = time.time()
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.isfile(file_path):
                    last_accessed = os.path.getatime(file_path)
                    # Delete only if inactive for more than X days
                    if (now - last_accessed) > (days_threshold * 86400):
                        os.remove(file_path)
                        logging.info(f"✅ Deleted {file_path} (inactive for over {days_threshold} days)")
                        print(f"✅ Deleted {file_path}")
            except Exception as e:
                logging.error(f"❌ Error deleting {file_path}: {e}")
                print(f"❌ Error deleting {file_path}: {e}")

if __name__ == "__main__":
    cleanup_old_files(WATCH_FOLDER, DAYS_INACTIVE)

