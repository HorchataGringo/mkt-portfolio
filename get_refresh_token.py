from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Scopes required for Drive and Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

def main():
    print("--- Google Drive Refresh Token Generator ---")
    print("This script will help you generate a Refresh Token for GitHub Secrets.")
    
    # Check for credentials.json
    if not os.path.exists('credentials.json'):
        print("\nError: 'credentials.json' not found.")
        print("Please download your OAuth Client ID JSON from Google Cloud Console,")
        print("rename it to 'credentials.json', and place it in this directory.")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            SCOPES
        )
        
        # We need to specify access_type='offline' to get a refresh token
        # and include_granted_scopes='true' for incremental auth
        creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent' # Force consent to ensure refresh token is returned
        )

        print("\n--- SUCCESS! ---")
        print("Here is your Refresh Token (save this as a GitHub Secret 'GOOGLE_REFRESH_TOKEN'):")
        print(creds.refresh_token)
        print("\nAlso save these as secrets:")
        print(f"GOOGLE_CLIENT_ID: {creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET: {creds.client_secret}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == '__main__':
    main()
