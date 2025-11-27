# Cloud Integration Setup Guide

To enable the automatic daily updates via GitHub Actions, you need to configure the following secrets in your GitHub repository.

## 1. Google Drive Integration (OAuth 2.0)

Since you are using a personal account, we will use OAuth 2.0 to access your Google Drive.

### Step 1: Configure Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (e.g., "Portfolio Tracker").
3.  **Enable APIs**:
    *   Go to **APIs & Services** > **Library**.
    *   Search for and enable **Google Drive API**.
4.  **Configure OAuth Consent Screen**:
    *   Go to **APIs & Services** > **OAuth consent screen**.
    *   Select **External** user type and click **Create**.
    *   Fill in the required fields (App name, User support email, Developer contact information).
    *   Click **Save and Continue**.
    *   **Scopes**: Add `https://www.googleapis.com/auth/drive` (See, Edit, Create, and Delete Google Drive files).
    *   **Test Users**: Add your own Google email address as a test user. This is crucial for personal apps in "Testing" mode.
5.  **Create Credentials**:
    *   Go to **APIs & Services** > **Credentials**.
    *   Click **Create Credentials** > **OAuth client ID**.
    *   Application type: **Desktop app**.
    *   Name: "Desktop Client" (or similar).
    *   Click **Create**.
    *   Download the JSON file or copy the **Client ID** and **Client Secret**.

### Step 2: Generate Refresh Token
You need a one-time Refresh Token to allow the GitHub Action to access your Drive offline.

1.  Ensure you have the necessary libraries installed locally:
    ```bash
    pip install google-auth-oauthlib
    ```
2.  Run the provided script `get_refresh_token.py` to generate your refresh token.
    *   Make sure you have placed your `credentials.json` file in the project root (downloaded from Google Cloud Console).
3.  Run the script: `python get_refresh_token.py`.
4.  A browser window will open. Log in with your Google account and allow access.
5.  Copy the **Refresh Token** printed in the terminal.

### Step 3: Create Folder
1.  Create a folder in your Google Drive (e.g., "Portfolio Data").
2.  Note the **Folder ID** from the URL (the string after `folders/`).
    *   Example: `https://drive.google.com/drive/folders/1a2b3c4d5e6f...` -> ID is `1a2b3c4d5e6f...`

### Step 4: GitHub Secrets
Go to your GitHub Repo > Settings > Secrets and variables > Actions > New repository secret.

Add the following secrets:

*   **Name**: `GOOGLE_CLIENT_ID`
    *   **Value**: Your OAuth Client ID.
*   **Name**: `GOOGLE_CLIENT_SECRET`
    *   **Value**: Your OAuth Client Secret.
*   **Name**: `GOOGLE_REFRESH_TOKEN`
    *   **Value**: The Refresh Token you generated in Step 2.
*   **Name**: `DRIVE_FOLDER_ID`
    *   **Value**: Your Folder ID.

## 2. Email Notifications

### Step 1: App Password (for Gmail)
1.  Go to your Google Account settings > Security.
2.  Enable 2-Step Verification if not already enabled.
3.  Search for "App Passwords".
4.  Create a new App Password for "Mail" / "Mac" (or custom name).
5.  Copy the 16-character password.

### Step 2: GitHub Secrets
-   **Name**: `EMAIL_USER`
    -   **Value**: Your Gmail address (e.g., `you@gmail.com`).
-   **Name**: `EMAIL_PASSWORD`
    -   **Value**: The 16-character App Password.
-   **Name**: `EMAIL_TO` (Optional)
    -   **Value**: The email address to receive reports (defaults to `EMAIL_USER`).

## 3. Testing
1.  Push these changes to GitHub.
2.  Go to the **Actions** tab.
3.  Select "Daily Portfolio Update".
4.  Click **Run workflow** to test manually.

## 4. Local Execution (Optional)

If you want to run the script locally on your machine:

1.  Download the **OAuth Client JSON** file from Google Cloud Console (Credentials > Download JSON).
2.  Rename it to `credentials.json` and place it in the root of the project.
3.  Run the script. A browser window will open for you to log in.
4.  After successful login, a `token.json` file will be created. This file stores your access and refresh tokens for future runs.
