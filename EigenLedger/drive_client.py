import os
import io
import json
import logging

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# Scopes required for Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate using OAuth 2.0 (Local/Env) or Service Account."""
        try:
            # 1. Try Local OAuth 2.0 (token.json)
            if os.path.exists('token.json'):
                try:
                    self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                    logging.info("Loaded credentials from token.json")
                except Exception as e:
                    logging.warning(f"Error loading token.json: {e}")

            # 2. Refresh valid token if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    logging.info("Refreshed expired token")
                except Exception as e:
                    logging.warning(f"Error refreshing token: {e}")
                    self.creds = None

            # 3. If no valid creds yet, try Env Vars (CI/CD)
            if not self.creds or not self.creds.valid:
                client_id = os.environ.get('GOOGLE_CLIENT_ID')
                client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
                refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')

                if client_id and client_secret and refresh_token:
                    self.creds = Credentials(
                        None,
                        refresh_token=refresh_token,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=SCOPES
                    )
                    logging.info("Authenticated with Google Drive API (Env Vars).")

            # 4. If still no creds, try Interactive Local Flow (credentials.json)
            if (not self.creds or not self.creds.valid) and os.path.exists('credentials.json'):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
                    logging.info("Authenticated via Interactive Local Flow.")
                except Exception as e:
                    logging.error(f"Interactive login failed: {e}")



            if self.creds and self.creds.valid:
                self.service = build('drive', 'v3', credentials=self.creds)
                logging.info("Drive Service built successfully.")
            else:
                logging.warning("No valid Google Drive credentials found. Drive integration disabled.")

        except Exception as e:
            logging.error(f"Failed to authenticate with Google Drive: {e}")

    def download_file(self, filename, destination_path, folder_id=None):
        """Download a file by name from a specific folder (optional)."""
        if not self.service:
            logging.warning("Drive service not initialized. Skipping download.")
            return False

        try:
            # Search for the file
            query = f"name = '{filename}' and trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query, pageSize=1, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                logging.warning(f"File '{filename}' not found in Drive.")
                return False

            file_id = items[0]['id']
            logging.info(f"Found file '{filename}' (ID: {file_id}). Downloading...")

            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # logging.info(f"Download {int(status.progress() * 100)}%.")
            
            logging.info(f"Successfully downloaded '{filename}' to {destination_path}.")
            return True

        except Exception as e:
            logging.error(f"Error downloading file from Drive: {e}")
            return False

    def upload_file(self, filepath, folder_id=None):
        """Upload a file to Drive."""
        if not self.service:
            logging.warning("Drive service not initialized. Skipping upload.")
            return False

        try:
            filename = os.path.basename(filepath)
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(filepath, resumable=True)

            # Check if file already exists to update it instead of creating duplicate
            query = f"name = '{filename}' and trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query, pageSize=1, fields="files(id)").execute()
            items = results.get('files', [])

            if items:
                file_id = items[0]['id']
                logging.info(f"File '{filename}' exists (ID: {file_id}). Updating...")
                file = self.service.files().update(
                    fileId=file_id, media_body=media).execute()
            else:
                logging.info(f"Uploading new file '{filename}'...")
                file = self.service.files().create(
                    body=file_metadata, media_body=media, fields='id').execute()

            logging.info(f"Successfully uploaded file. File ID: {file.get('id')}")
            return True

        except Exception as e:
            logging.error(f"Error uploading file to Drive: {e}")
            return False

    def list_files(self, page_size=10):
        """List files in the Drive."""
        if not self.service:
            logging.warning("Drive service not initialized. Skipping list files.")
            return []

        try:
            results = self.service.files().list(
                pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)").execute()
            items = results.get('files', [])
            return items
        except Exception as e:
            logging.error(f"Error listing files: {e}")
            return []
