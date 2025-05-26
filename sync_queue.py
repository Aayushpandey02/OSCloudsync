import os
import time
from queue import PriorityQueue
from supabase_sync import upload_file_to_supabase

WATCH_FOLDER = 'watch_folder'
DEST_FOLDER = 'synced'
BUCKET_NAME = 'user-files'

class RevertableSyncQueue:
    def __init__(self):
        self.queue = PriorityQueue()

    def add_to_queue(self, filepath, priority=0):
        relative_path = os.path.relpath(filepath, WATCH_FOLDER)
        self.queue.put((priority, filepath, relative_path))

    def process_queue(self, log_event, update_stats):
        while not self.queue.empty():
            priority, filepath, relative_path = self.queue.get()
            supabase_path = f"{DEST_FOLDER}/{relative_path}"
            try:
                if os.path.exists(filepath):  # only upload if file still exists
                    upload_file_to_supabase(BUCKET_NAME, filepath, supabase_path)
                    log_event(f"Re-synced (priority {priority}): {supabase_path}", "synced")
                else:
                    log_event(f"File missing on retry: {filepath}", "error")
                update_stats()
            except Exception as e:
                log_event(f"Failed re-sync {supabase_path}: {str(e)}", "error")
                update_stats()
                # Requeue with higher priority for retry
                self.add_to_queue(filepath, priority=priority - 1)

sync_queue = RevertableSyncQueue()
