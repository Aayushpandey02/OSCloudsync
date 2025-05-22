import os
from drive_service import get_drive_service
from googleapiclient.http import MediaFileUpload

# ✅ Replace this with your actual folder ID inside quotes
GDRIVE_FOLDER_ID = '1Y6B-btOFaKd6S31CzTdYP3-cX7WjbdAe'

# 👀 Folder to watch
WATCH_FOLDER = 'watch_folder'

def upload_file_to_drive(filepath):
    try:
        print(f"🔄 Preparing to upload: {filepath}")
        drive_service = get_drive_service()
        filename = os.path.basename(filepath)

        file_metadata = {'name': filename}
        if GDRIVE_FOLDER_ID:
            file_metadata['parents'] = [GDRIVE_FOLDER_ID]

        media = MediaFileUpload(filepath, resumable=True)
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"✅ Uploaded: {filename} (File ID: {uploaded_file.get('id')})")
        return True
    except Exception as e:
        print(f"❌ Error uploading {filepath}: {e}")
        return False

def sync_all_files():
    if not os.path.exists(WATCH_FOLDER):
        print(f"⚠️ Watch folder '{WATCH_FOLDER}' does not exist.")
        return

    for filename in os.listdir(WATCH_FOLDER):
        filepath = os.path.join(WATCH_FOLDER, filename)
        if os.path.isfile(filepath):
            upload_file_to_drive(filepath)

if __name__ == "__main__":
    print("🚀 Starting sync for all files in watch folder...")
    sync_all_files()



