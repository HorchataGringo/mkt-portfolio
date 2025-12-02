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

1.  **Install dependencies** with Poetry:
    ```bash
    poetry install
    ```
2.  Run the provided script `get_refresh_token.py` to generate your refresh token:
    *   Make sure you have placed your `credentials.json` file in the project root (downloaded from Google Cloud Console in Step 1).
    
    ```bash
    poetry run python get_refresh_token.py
    ```
3.  A browser window will open. Log in with your Google account and **allow access**.
4.  Copy the **Refresh Token**, **Client ID**, and **Client Secret** printed in the terminal.
    *   You will use these to configure GitHub Secrets in Step 4.

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

## 3. Update GitHub Default Branch (Important!)

If you renamed your local branch from `master` to `main`, you must also update GitHub's default branch:

1.  Go to your GitHub repository: **Settings** → **Branches**
2.  Under "Default branch", click the switch icon next to `master`
3.  Select `main` as the new default branch
4.  Click **Update**
5.  Go to **Branches** (under Code tab) and delete the old `master` branch

This ensures the GitHub Action runs on the correct branch.

## 4. Google Sheets Integration Setup

The portfolio tracker now uses Google Sheets for:
- **Reading portfolio holdings** from the "holdings" sheet
- **Storing daily snapshots** in the "snapshots" sheet (auto-created)
- **Tracking daily changes** in the "daily_changes" sheet (auto-created)

### Spreadsheet Setup

1. **Create a Google Sheet named exactly "Portfolio"** (case-sensitive)
2. **Create a sheet tab named "holdings"** with these columns:
   ```
   Symbol | Shares | PurchaseDate
   ```
   - Symbol: Ticker symbol (e.g., NVDY)
   - Shares: Number of shares (e.g., 100)
   - PurchaseDate: Date in mm/dd/yyyy format (e.g., 01/15/2024)

3. **Add your current positions** to the holdings sheet
4. The tracker will automatically create "snapshots" and "daily_changes" sheets on first run

**Example holdings sheet:**
```
Symbol  | Shares | PurchaseDate
--------|--------|-------------
NVDY    | 100    | 01/15/2024
MSTY    | 100    | 02/20/2024
AMZY    | 100    | 03/10/2024
```

For detailed schema documentation, see [SHEETS_SCHEMA.md](SHEETS_SCHEMA.md).

### IMPORTANT: Regenerate OAuth Token

**The Sheets API requires a new permission scope.** Your existing refresh token will NOT work.

**You MUST regenerate your refresh token:**

1. The `get_refresh_token.py` script has been updated with new scopes
2. Run it again:
   ```bash
   poetry run python get_refresh_token.py
   ```
3. A browser will open - **log in and grant permissions** (you'll see a new Sheets permission request)
4. Copy the new `GOOGLE_REFRESH_TOKEN` from the output
5. **Update the GitHub secret** `GOOGLE_REFRESH_TOKEN` with the new value

**Without regenerating, the tracker will fail with authentication errors.**

## 5. Testing

**Important:** The GitHub Action uses **OAuth 2.0** with the Refresh Token you generated. This means:
- The workflow does **NOT** require interactive login
- It uses the `GOOGLE_REFRESH_TOKEN`, `GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET` secrets
- The refresh token is valid long-term and will automatically refresh the access token
- **New**: The token now includes Sheets API permissions

**To Test:**
1.  Ensure the "Portfolio" spreadsheet exists with "holdings" sheet populated
2.  Ensure you've regenerated your refresh token (see Step 4 above)
3.  Ensure all secrets are configured in GitHub (including new GOOGLE_REFRESH_TOKEN)
4.  Go to the **Actions** tab in your repository
5.  Select **"Daily Portfolio Update"**
6.  Click **Run workflow** → **Run workflow** (green button)
7.  Watch the workflow execute and check for:
    - "Loaded X positions from Google Sheets" in logs
    - "First snapshot created" or "Daily changes calculated" in logs
    - Email received with daily update
8.  Check your "Portfolio" spreadsheet for new "snapshots" and "daily_changes" sheets

## 5. Local Execution (Optional)

If you want to run the script locally on your machine:

1.  Download the **OAuth Client JSON** file from Google Cloud Console (Credentials > Download JSON).
2.  Rename it to `credentials.json` and place it in the root of the project.
3.  Run the script. A browser window will open for you to log in.
4.  After successful login, a `token.json` file will be created. This file stores your access and refresh tokens for future runs.


