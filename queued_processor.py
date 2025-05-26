# queued_processor.py
import time
import threading
from queue import PriorityQueue
from supabase_sync import upload_file_to_supabase, delete_file_from_supabase
from app_utils import log_event, update_stats

WATCH_FOLDER = 'watch_folder'
BUCKET_NAME = 'user-files'
DEST_FOLDER = 'synced'

class FileJob:
    def __init__(self, priority, operation, filepath):
        self.priority = priority
        self.operation = operation
        self.filepath = filepath

    def __lt__(self, other):
        return self.priority < other.priority  # Lower value = higher priority

class FileSyncQueue:
    def __init__(self):
        self.queue = PriorityQueue()
        self.running = False
        self.thread = threading.Thread(target=self._worker)
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self._worker)
            self.thread.start()

    def stop(self):
        self.running = False
        self.queue.put((99, None))  # Dummy job to unblock queue

    def add_job(self, priority, operation, filepath):
        self.queue.put((priority, FileJob(priority, operation, filepath)))

    def _worker(self):
        while self.running:
            priority, job = self.queue.get()
            if job is None:
                continue

            rel_path = os.path.relpath(job.filepath, WATCH_FOLDER)
            supabase_path = f"{DEST_FOLDER}/{rel_path}"

            try:
                if job.operation == "delete":
                    delete_file_from_supabase(BUCKET_NAME, supabase_path)
                    log_event(f"Deleted from Supabase: {supabase_path}", "deleted")
                    update_stats("deleted")
                elif job.operation in ("create", "modify"):
                    if os.path.exists(job.filepath):
                        upload_file_to_supabase(BUCKET_NAME, job.filepath, supabase_path)
                        log_event(f"Uploaded to Supabase: {supabase_path}", "synced")
                        update_stats("synced")
            except Exception as e:
                log_event(f"Error during {job.operation} for {supabase_path}: {str(e)}", "error")
                update_stats("errors")
