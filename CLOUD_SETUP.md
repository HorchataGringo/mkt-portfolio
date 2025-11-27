# Cloud Integration Setup Guide

To enable the automatic daily updates via GitHub Actions, you need to configure the following secrets in your GitHub repository.

## 1. Google Drive Integration

### Step 1: Create a Service Account
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (e.g., "Portfolio Tracker").
3.  Enable the **Google Drive API** for this project.
4.  Go to **IAM & Admin** > **Service Accounts**.
5.  Create a Service Account and download the JSON key file.
6.  **Important**: Open the JSON file and copy its entire content.

### Step 2: Share Folder
1.  Create a folder in your Google Drive (e.g., "Portfolio Data").
2.  Note the **Folder ID** from the URL (the string after `folders/`).
3.  **Share** this folder with the `client_email` address found in your JSON key file (give "Editor" access).

### Step 3: GitHub Secrets
Go to your GitHub Repo > Settings > Secrets and variables > Actions > New repository secret.

-   **Name**: `GOOGLE_CREDENTIALS_JSON`
    -   **Value**: Paste the content of your JSON key file.
-   **Name**: `DRIVE_FOLDER_ID`
    -   **Value**: Your Folder ID.

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
