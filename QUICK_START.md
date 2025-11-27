# Quick Start Guide

**Complete setup in 20 minutes and start receiving daily portfolio updates!**

---

## Prerequisites

- Python 3.11+
- Poetry installed
- Google account (for Sheets & Gmail)
- GitHub account

---

## Step 1: Create Google Sheet (5 minutes)

1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet named **"Portfolio"** (case-sensitive)
3. Rename "Sheet1" to **"holdings"**
4. Add headers in row 1:
   ```
   Symbol | Shares | PurchaseDate
   ```
5. Add your positions:
   ```
   Symbol  | Shares | PurchaseDate
   --------|--------|-------------
   NVDY    | 100    | 01/15/2024
   MSTY    | 100    | 02/20/2024
   AMZY    | 100    | 03/10/2024
   ```

**Important**: Dates must be in mm/dd/yyyy format.

---

## Step 2: Generate OAuth Tokens (5 minutes)

```bash
poetry run python get_refresh_token.py
```

Follow the prompts to:
- Authorize Google Drive access
- Authorize Google Sheets access
- Copy the refresh token, client ID, and client secret

**Save these values** - you'll need them for GitHub secrets.

---

## Step 3: Get Gmail App Password (2 minutes)

1. Go to: [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to: App Passwords
4. Create password for "Mail" app
5. Copy the 16-character password (remove spaces)

---

## Step 4: Configure GitHub Secrets (5 minutes)

1. Push this code to your GitHub repository
2. Go to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

Add these 7 secrets:

| Secret Name | Example Value | Where to Get |
|-------------|---------------|--------------|
| `GOOGLE_CLIENT_ID` | `123.apps.googleusercontent.com` | Step 2 output |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-abc123` | Step 2 output |
| `GOOGLE_REFRESH_TOKEN` | `1//xyz789` | Step 2 output |
| `DRIVE_FOLDER_ID` | `1a2b3c4d5e6f` (optional) | Google Drive folder for backups |
| `EMAIL_USER` | `you@gmail.com` | Your Gmail address |
| `EMAIL_PASSWORD` | `abcdefghijklmnop` | Step 3 App Password |
| `EMAIL_TO` | `recipient@email.com` | Who receives reports (comma-separated for multiple) |

---

## Step 5: Test the Workflow (3 minutes)

1. Go to **Actions** tab in your GitHub repo
2. Select **"Daily Portfolio Update"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Watch the run complete (~2 minutes)

---

## Verify Success

### Check Your Email
- Subject: "Daily Portfolio Report"
- Body: Portfolio summary with daily changes (or "Historical tracking started" on first run)
- Attachments: CSV report, backtest chart, trend chart

### Check Google Sheets
Your "Portfolio" spreadsheet should now have 3 sheets:
- **holdings** - Your positions (you edit this)
- **snapshots** - Daily portfolio snapshots (auto-generated)
- **daily_changes** - Day-over-day changes (auto-generated)

### Check GitHub Actions
- Workflow shows green checkmark ✅
- Logs show: "Email sent successfully"

---

## What Happens Daily

Every day at **9:00 AM EST** (13:00 UTC), the tracker automatically:

1. Reads your portfolio from Google Sheets
2. Fetches current prices from Yahoo Finance
3. Calculates all metrics (P&L, dividends, returns, beta, etc.)
4. Creates historical snapshot
5. Calculates daily changes vs yesterday
6. Generates performance charts
7. Sends email with:
   - Daily value change
   - Top 3 gainers and losers
   - Full portfolio dashboard
   - Attached CSV and charts
   - **Mondays only**: Weekly summary section

---

## Daily Maintenance

### Update Your Portfolio

**Add a position**:
1. Open Google Sheets "Portfolio/holdings"
2. Insert new row: Symbol, Shares, PurchaseDate (mm/dd/yyyy)
3. Next run will include it

**Remove a position**:
1. Delete the entire row from holdings sheet
2. Daily changes will show it as sold

**Update shares**:
1. Edit the Shares column
2. Daily changes will detect the change

Changes take effect on the next scheduled run (9 AM EST).

### View Historical Data

- **Google Sheets**: Chart portfolio value over time using snapshots sheet
- **Email Charts**: 90-day trend chart attached to every email
- **CSV Exports**: Attached to each email for external analysis

---

## Troubleshooting

### Error: "Spreadsheet 'Portfolio' not found"
→ Spreadsheet name must be exactly "Portfolio" (case-sensitive)

### Error: "No data found in 'holdings' sheet"
→ Verify sheet name is "holdings" and has Symbol/Shares/PurchaseDate headers

### Error: "No valid Google Drive credentials found"
→ Regenerate token with Step 2, update GOOGLE_REFRESH_TOKEN secret

### Error: "Authentication failed" (Email)
→ Use Gmail App Password (16 characters), not your regular password

### Email not received
→ Check spam folder, verify EMAIL_USER and EMAIL_PASSWORD secrets

### Daily changes not showing
→ Normal for first run - need 2+ snapshots to compare. Check Day 2.

For detailed troubleshooting, see [TESTING_GUIDE.md](TESTING_GUIDE.md).

---

## Local Testing (Optional)

Test before pushing to GitHub:

```bash
# Set environment variables
export ENABLE_CLOUD="true"
export USE_SHEETS="true"
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REFRESH_TOKEN="your-refresh-token"

# Run tracker
poetry run portfolio-tracker
```

Expected output:
- "Loaded X positions from Google Sheets"
- "First snapshot created - historical tracking started!"
- Check "Portfolio" spreadsheet for new sheets

---

## Next Steps

After successful setup:

1. **Wait for Day 2** - Daily changes will appear in emails
2. **Monitor for 1 week** - Verify daily emails arrive consistently
3. **Explore historical data** - Use snapshots sheet for custom analysis
4. **Review documentation**:
   - [README.md](README.md) - Complete system overview
   - [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Detailed setup guide
   - [SHEETS_SCHEMA.md](SHEETS_SCHEMA.md) - Data structure reference

---

## Need Help?

1. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed troubleshooting
2. Check [CLOUD_SETUP.md](CLOUD_SETUP.md) for OAuth setup details
3. Review GitHub Actions logs for specific errors
4. Verify all secrets are configured correctly

---

**Total Setup Time**: ~20 minutes
**Daily Effort**: Zero (fully automated!)
**Historical Data**: Preserved forever in Google Sheets
