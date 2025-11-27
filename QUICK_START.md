# Quick Start Guide

## Local Testing (5 minutes)

```bash
# 1. Test the tracker locally
poetry run portfolio-tracker

# Expected: Portfolio analysis runs successfully
```

---

## Cloud Setup (15 minutes)

### Step 1: Generate OAuth Tokens
```bash
poetry run python get_refresh_token.py
```
Save the output (Client ID, Client Secret, Refresh Token).

### Step 2: Prepare Google Drive
1. Create folder in Google Drive named "Portfolio Data"
2. Upload `dad_tickers.txt` to this folder
3. Copy Folder ID from URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`

### Step 3: Get Gmail App Password
1. Go to: Google Account → Security → 2-Step Verification → App Passwords
2. Create password for "Mail" app
3. Copy the 16-character password

### Step 4: Configure GitHub Secrets
Go to: **Repository Settings → Secrets → Actions → New secret**

Add these 7 secrets:

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | From Step 1 |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-xxx` | From Step 1 |
| `GOOGLE_REFRESH_TOKEN` | `1//xxx` | From Step 1 |
| `DRIVE_FOLDER_ID` | `1a2b3c4d5e6f...` | From Step 2 |
| `EMAIL_USER` | `your-email@gmail.com` | Your Gmail |
| `EMAIL_PASSWORD` | `abcd efgh ijkl mnop` | From Step 3 |
| `EMAIL_TO` | `recipient@email.com` | Who receives reports |

### Step 5: Test GitHub Action
1. Go to **Actions** tab
2. Click **"Daily Portfolio Update"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs for success

---

## Verify Success

After the workflow completes, check:

- ✅ **Email**: You received portfolio report email
- ✅ **Google Drive**: `portfolio_report.csv` and `portfolio_backtest.png` uploaded
- ✅ **GitHub Actions**: Workflow shows green checkmark

---

## Scheduled Runs

The workflow automatically runs at **9:00 AM EST** (13:00 UTC) every day.

No further action needed!

---

## Troubleshooting

### Error: "No valid Google Drive credentials found"
→ Check that all 3 Google secrets (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN) are set

### Error: "Authentication failed" (Email)
→ Use App Password, not regular Gmail password

### Error: "File not found in Drive"
→ Upload dad_tickers.txt to Drive folder, verify FOLDER_ID is correct

### Need detailed help?
→ See `TESTING_GUIDE.md` for comprehensive troubleshooting

---

## Daily Maintenance

### Update Portfolio Holdings
1. Edit `dad_tickers.txt` in Google Drive
2. Next scheduled run will use new data

### Check Reports
- Check your email daily for portfolio updates
- Review trends in Google Drive folder

### Monitor Workflow
- Visit Actions tab to see run history
- Green = success, Red = failure (will get email notification)

---

## Need Help?

1. Check `TESTING_GUIDE.md` for detailed instructions
2. Check `CLOUD_SETUP.md` for OAuth setup details
3. Review GitHub Actions logs for specific errors
4. Verify all secrets are spelled correctly (case-sensitive!)

---

**Total Setup Time**: ~20 minutes
**Daily Effort**: Zero (fully automated!)
