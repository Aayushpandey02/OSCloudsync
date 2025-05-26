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

