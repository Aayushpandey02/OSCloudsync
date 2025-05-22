import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the Google Drive API scopes your app needs
# 'drive.file' lets your app see and manage the files it created or opened.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to your OAuth 2.0 Client ID JSON file downloaded from Google Cloud Console
CREDENTIALS_FILE = 'credential_@.json'

# Token file to store access and refresh tokens after user authorization
TOKEN_FILE = 'token.json'


def get_drive_service():
    """
    Authenticate user and return an authorized Google Drive API service instance.

    - Loads token from TOKEN_FILE if it exists and is valid.
    - Otherwise, runs OAuth flow using CREDENTIALS_FILE and saves token.
    - Handles token refresh automatically.
    """

    creds = None

    # Check if token.json file exists with saved credentials
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials available, request user login via OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the expired token automatically
            creds.refresh(Request())
        else:
            # Start OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next runs
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    # Build the Drive API client with authorized credentials
    service = build('drive', 'v3', credentials=creds)
    return service


if __name__ == "__main__":
    # Quick test to check if Drive API service is created successfully
    drive_service = get_drive_service()
    print("Google Drive service created successfully!")


