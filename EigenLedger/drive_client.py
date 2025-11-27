import os
import io
import json
import logging

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# Scopes required for Drive and Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

class DriveClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self.sheets_service = None
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
                try:
                    self.service = build('drive', 'v3', credentials=self.creds)
                    logging.info("Drive service built successfully.")
                except Exception as e:
                    logging.error(f"Failed to build Drive service: {e}")
                    self.service = None

                try:
                    self.sheets_service = build('sheets', 'v4', credentials=self.creds)
                    logging.info("Sheets service built successfully.")
                except Exception as e:
                    logging.error(f"Failed to build Sheets service: {e}")
                    self.sheets_service = None

                if self.service or self.sheets_service:
                    logging.info("At least one Google API service initialized successfully.")
            else:
                logging.warning("No valid Google Drive credentials found. Drive and Sheets integration disabled.")

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

    # ========== Google Sheets API Methods ==========

    def find_spreadsheet_by_name(self, name):
        """Find spreadsheet by name and return its ID."""
        if not self.service:
            logging.warning("Drive service not initialized.")
            return None

        try:
            query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
            results = self.service.files().list(
                q=query, pageSize=1, fields="files(id, name)").execute()
            items = results.get('files', [])

            if items:
                logging.info(f"Found spreadsheet '{name}' (ID: {items[0]['id']})")
                return items[0]['id']
            else:
                logging.warning(f"Spreadsheet '{name}' not found.")
                return None
        except Exception as e:
            logging.error(f"Error finding spreadsheet: {e}")
            return None

    def get_sheet_values(self, spreadsheet_id, range_name):
        """Read values from a sheet range."""
        if not self.sheets_service:
            logging.warning("Sheets service not initialized.")
            return None

        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            logging.info(f"Read {len(values)} rows from '{range_name}'")
            return values
        except Exception as e:
            logging.error(f"Error reading sheet values: {e}")
            return None

    def append_sheet_row(self, spreadsheet_id, range_name, values):
        """Append a row to a sheet."""
        if not self.sheets_service:
            logging.warning("Sheets service not initialized.")
            return False

        try:
            body = {'values': [values]}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logging.info(f"Appended 1 row to '{range_name}'. Updated {result.get('updates').get('updatedCells')} cells.")
            return True
        except Exception as e:
            logging.error(f"Error appending to sheet: {e}")
            return False

    def batch_append_rows(self, spreadsheet_id, range_name, values_list):
        """Append multiple rows to a sheet at once."""
        if not self.sheets_service:
            logging.warning("Sheets service not initialized.")
            return False

        try:
            body = {'values': values_list}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            logging.info(f"Appended {len(values_list)} rows to '{range_name}'.")
            return True
        except Exception as e:
            logging.error(f"Error batch appending to sheet: {e}")
            return False

    def get_or_create_sheet(self, spreadsheet_id, sheet_name):
        """Get sheet ID by name, create if doesn't exist. Returns sheet_id."""
        if not self.sheets_service:
            logging.warning("Sheets service not initialized.")
            return None

        try:
            # Get spreadsheet metadata
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
            sheets = spreadsheet.get('sheets', [])

            # Check if sheet exists
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    logging.info(f"Sheet '{sheet_name}' already exists (ID: {sheet_id})")
                    return sheet_id

            # Sheet doesn't exist, create it
            logging.info(f"Creating new sheet '{sheet_name}'...")
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            response = self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=request_body).execute()
            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            logging.info(f"Created sheet '{sheet_name}' (ID: {sheet_id})")
            return sheet_id

        except Exception as e:
            logging.error(f"Error getting/creating sheet: {e}")
            return None

    def read_holdings_from_sheet(self, spreadsheet_name="Portfolio", sheet_name="holdings"):
        """Read holdings from Google Sheet, return as DataFrame."""
        import pandas as pd
        from datetime import datetime

        if not self.sheets_service:
            logging.warning("Sheets service not initialized.")
            return pd.DataFrame()

        try:
            # Find spreadsheet by name
            spreadsheet_id = self.find_spreadsheet_by_name(spreadsheet_name)
            if not spreadsheet_id:
                raise ValueError(f"Spreadsheet '{spreadsheet_name}' not found")

            # Read holdings sheet
            range_name = f"{sheet_name}!A:C"  # Symbol, Shares, PurchaseDate
            values = self.get_sheet_values(spreadsheet_id, range_name)

            if not values:
                logging.warning(f"No data found in '{sheet_name}' sheet")
                return pd.DataFrame()

            # Convert to DataFrame
            # First row should be headers: Symbol, Shares, PurchaseDate
            headers = values[0]
            data_rows = values[1:]

            df = pd.DataFrame(data_rows, columns=headers)

            # Normalize column names (user said: Symbol, Shares, PurchaseDate)
            # Map to our internal format: Tickers, Quantity, PurchaseDate
            column_mapping = {
                'Symbol': 'Tickers',
                'Shares': 'Quantity',
                'PurchaseDate': 'PurchaseDate'
            }

            df = df.rename(columns=column_mapping)

            # Convert data types
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')

            # Parse PurchaseDate (format: mm/dd/yyyy)
            def parse_date(date_str):
                try:
                    return datetime.strptime(date_str, '%m/%d/%Y')
                except:
                    logging.warning(f"Could not parse date: {date_str}")
                    return None

            df['PurchaseDateObj'] = df['PurchaseDate'].apply(parse_date)

            # Remove rows with invalid data
            df = df.dropna(subset=['Tickers', 'Quantity', 'PurchaseDateObj'])

            logging.info(f"Loaded {len(df)} holdings from Google Sheets '{spreadsheet_name}/{sheet_name}'")
            return df

        except Exception as e:
            logging.error(f"Error reading holdings from sheet: {e}")
            return pd.DataFrame()
