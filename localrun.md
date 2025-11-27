# Local Execution Guide

This guide explains how to run the EigenLedger Portfolio Tracker locally on your machine, both with and without cloud integration.

## Prerequisites

1.  **Python 3.11+**: Ensure Python is installed.
2.  **Poetry**: Dependency manager.
    ```bash
    pip install poetry
    ```
3.  **Install Dependencies**:
    ```bash
    poetry install
    ```

## 1. Basic Run (Local Only)

By default, the tracker runs in local mode. It reads `dad_tickers.txt` from the project root and prints the report to the console. It does **not** upload to Drive or send emails.

**Command:**
```powershell
poetry run python EigenLedger/portfolio_tracker.py
```

## 2. Run with Cloud Integration (Drive & Email)

To enable Google Drive uploads and Email notifications locally, follow these steps.

### Step A: Google Drive Setup
1.  Download your **OAuth Client ID** JSON file from Google Cloud Console.
2.  Rename it to `credentials.json` and place it in the project root.
3.  The first time you run the app, it will open a browser window asking you to log in.
4.  After logging in, it will create a `token.json` file locally. Future runs will use this token automatically.

### Step B: Environment Variables
You need to set the `ENABLE_CLOUD` variable to `true`. You also need to provide email credentials if you want email reports.

**PowerShell Command:**

```powershell
# Enable Cloud Features
$env:ENABLE_CLOUD="true"

# Google Drive Folder ID (Optional - if omitted, uploads to root)
$env:DRIVE_FOLDER_ID="your_drive_folder_id_here"

# Email Configuration (Required for emails)
$env:EMAIL_USER="your_email@gmail.com"
$env:EMAIL_PASSWORD="your_app_password"
$env:EMAIL_TO="recipient@example.com" # Optional, defaults to EMAIL_USER

# Run the Tracker
poetry run python EigenLedger/portfolio_tracker.py
```

### Step C: Cleanup (Optional)
To clear the environment variables after running:
```powershell
Remove-Item Env:\ENABLE_CLOUD
Remove-Item Env:\DRIVE_FOLDER_ID
Remove-Item Env:\EMAIL_USER
Remove-Item Env:\EMAIL_PASSWORD
Remove-Item Env:\EMAIL_TO
```

## Troubleshooting

*   **`credentials.json` not found**: Make sure the file is named exactly `credentials.json` and is in the same folder as `pyproject.toml`.
*   **Authentication Errors**: If `token.json` becomes invalid, delete it and run the script again to re-authenticate.
