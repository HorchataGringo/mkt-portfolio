import os
import io
import json
import logging
from google.oauth2 import service_account
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
        """Authenticate using Service Account JSON from environment variable."""
        try:
            creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            if not creds_json:
                logging.warning("GOOGLE_CREDENTIALS_JSON not found in environment variables. Drive integration disabled.")
                return

            creds_dict = json.loads(creds_json)
            self.creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=self.creds)
            logging.info("Successfully authenticated with Google Drive API.")
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
