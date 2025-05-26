# ☁️ OSCloudSync

A real-time file sync monitor using **Flask**, **Socket.IO**, and **Watchdog** that watches a local folder and queues file operations (create/modify/delete) for synchronization with Supabase Storage.

## 🚀 Features

- 🔍 Monitors a folder in real-time for file changes
- ⏱️ Queued processing of file operations (via `FileSyncQueue`)
- 📦 Socket.IO powered live dashboard with logs and stats
- 📁 Automatically creates a `watch_folder` to monitor
- 🔒 Thread-safe logging with stats tracking
- 🧠 Modular design for easy extension and Supabase integration

## 📂 Project Structure
   OSCloudSync/
   ├── app.py # Main Flask application
   ├── app_utils.py # Logging and stats utilities
   ├── queued_processor.py # Job queue for file sync tasks
   ├── templates/
   │ └── index.html # Dashboard UI
   ├── watch_folder/ # Folder to be watched (auto-created)
   ├── requirements.txt # Python dependencies
   └── README.md # This file
  

## 🧠 How It Works
  1.Watches watch_folder/ using watchdog.

  2.On file change (create/modify/delete), a job is added to FileSyncQueue.

  3.Flask-SocketIO serves a live dashboard showing log updates and stats.

  4.You can start/stop watching and clear logs from the dashboard UI.



