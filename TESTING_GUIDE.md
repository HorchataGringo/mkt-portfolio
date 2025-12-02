# Testing Guide for Portfolio Tracker

## Pre-Flight Checklist

Before running the GitHub Action for the first time, complete these steps:

### 1. Local Testing

Test the script locally to ensure it works:

```bash
# Test local mode (no cloud integration)
poetry run portfolio-tracker
```

Expected output:
- ✅ Portfolio loads from dad_tickers.txt
- ✅ Metrics calculated for all tickers
- ✅ Backtest chart generated (portfolio_backtest.png)
- ✅ No errors in price lookups

### 2. Generate OAuth Tokens

Run the token generator script:

```bash
poetry run python get_refresh_token.py
```

This will:
1. Open a browser for Google login
2. Display your refresh token, client ID, and client secret
3. Save these values - you'll need them for GitHub Secrets

### 3. Upload Test Data to Google Drive

1. Create a folder in Google Drive (e.g., "Portfolio Data")
2. Upload `dad_tickers.txt` to this folder
3. Copy the Folder ID from the URL:
   - URL: `https://drive.google.com/drive/folders/1a2b3c4d5e6f...`
   - Folder ID: `1a2b3c4d5e6f...`

### 4. Configure GitHub Secrets

Go to: **Repository Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

#### Google Drive OAuth
- **GOOGLE_CLIENT_ID**: From step 2
- **GOOGLE_CLIENT_SECRET**: From step 2
- **GOOGLE_REFRESH_TOKEN**: From step 2
- **DRIVE_FOLDER_ID**: From step 3

#### Email Configuration
- **EMAIL_USER**: Your Gmail address (e.g., `you@gmail.com`)
- **EMAIL_PASSWORD**: Gmail App Password (NOT your regular password)
  - Get this from: Google Account → Security → 2-Step Verification → App Passwords
- **EMAIL_TO**: Email to receive reports (optional, defaults to EMAIL_USER)

### 5. Test Cloud Mode Locally (Optional)

Before running the GitHub Action, test cloud mode locally:

```bash
# Set environment variables
export ENABLE_CLOUD=true
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REFRESH_TOKEN="your-refresh-token"
export DRIVE_FOLDER_ID="your-folder-id"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_TO="recipient@email.com"

# Run the tracker
poetry run portfolio-tracker
```

Expected output:
- ✅ "Cloud mode enabled. Initializing clients..."
- ✅ "Downloaded dad_tickers.txt from Drive."
- ✅ Portfolio analysis completes
- ✅ Files uploaded to Drive
- ✅ Email sent successfully

---

## Running the GitHub Action

### Manual Test Run

1. Go to: **Actions tab** in your GitHub repository
2. Select: **"Daily Portfolio Update"**
3. Click: **"Run workflow"** → **"Run workflow"** (green button)
4. Monitor the workflow execution

### What to Check in Logs

Look for these success indicators:

```
✅ Drive Service built successfully
✅ Downloaded dad_tickers.txt from Drive
✅ Fetching data for X tickers
✅ Backtest completed
✅ Successfully uploaded file. File ID: ...
✅ Email sent successfully to ...
✅ Portfolio analysis complete!
```

### Common Errors & Solutions

#### Error: "No valid Google Drive credentials found"
**Solution**:
- Verify `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` are set in GitHub Secrets
- Check for typos in secret names
- Re-run `get_refresh_token.py` if token expired

#### Error: "Drive API has not been enabled"
**Solution**:
- Go to Google Cloud Console → APIs & Services → Library
- Search "Google Drive API" and enable it

#### Error: "Authentication failed" (Email)
**Solution**:
- Ensure you're using an **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled on your Google account
- Check EMAIL_USER and EMAIL_PASSWORD secrets

#### Error: "File 'dad_tickers.txt' not found in Drive"
**Solution**:
- Upload dad_tickers.txt to your Google Drive folder
- Verify DRIVE_FOLDER_ID matches your folder ID

#### Error: "Invalid purchase price ($0.0) for TICKER"
**Solution**:
- Check ticker symbol is valid
- Verify purchase date is not before ticker IPO date
- Stock may have been delisted

---

## Monitoring & Maintenance

### Check Email Reports

After each run, you should receive an email with:
- Portfolio dashboard table
- Summary metrics
- Attachments: portfolio_report.csv, portfolio_backtest.png

### Check Google Drive

Your Drive folder should contain:
- `dad_tickers.txt` (input)
- `portfolio_report.csv` (updated daily)
- `portfolio_backtest.png` (updated daily)

### Scheduled Runs

The workflow runs automatically at **13:00 UTC (9:00 AM EST)** daily.

To change the schedule, edit `.github/workflows/daily_run.yml`:
```yaml
schedule:
  - cron: '0 13 * * *'  # Change this
```

Use [crontab.guru](https://crontab.guru/) to help with cron syntax.

---

## Troubleshooting Workflow Failures

### View Detailed Logs

1. Go to Actions tab
2. Click on the failed workflow run
3. Click on "run-tracker" job
4. Expand each step to see detailed output

### Re-run Failed Workflow

Click "Re-run jobs" → "Re-run failed jobs"

### Check Rate Limits

yfinance may rate-limit if downloading too many tickers. If this happens:
- Reduce the number of tickers in dad_tickers.txt
- Or add delays between API calls (requires code modification)

---

## Post-Deployment Checklist

After successful first run:

- [ ] Email received with portfolio report
- [ ] Files uploaded to Google Drive
- [ ] No errors in GitHub Actions log
- [ ] Metrics look accurate (compare with broker statement)
- [ ] Backtest chart displays correctly
- [ ] Scheduled run time is appropriate for your timezone

---

## Next Steps

1. **Set up failure notifications**:
   - GitHub sends email notifications for workflow failures by default
   - Check: Settings → Notifications → Actions

2. **Add monitoring**:
   - Create a status badge for your README
   - Set up alerts for workflow failures

3. **Backup your data**:
   - Keep a local copy of dad_tickers.txt
   - Export Google Drive folder periodically

4. **Update tickers**:
   - Modify dad_tickers.txt in Google Drive
   - Next workflow run will use updated data

---

## Support

If you encounter issues:

1. Check this guide first
2. Review error logs in GitHub Actions
3. Verify all secrets are set correctly
4. Test locally with cloud mode enabled
5. Check CLOUD_SETUP.md for OAuth setup details
