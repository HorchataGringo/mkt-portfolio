# Migration Guide: Adding Daily Portfolio Tracking with Google Sheets

This guide will help you migrate from the current snapshot-only system to the new historical tracking system with Google Sheets integration.

---

## What's New

✅ **Daily Historical Snapshots** - Complete portfolio state saved daily
✅ **Day-over-Day Changes** - Track daily deltas, top gainers/losers
✅ **90-Day Trend Charts** - Visualize performance over time
✅ **Google Sheets Storage** - All data stored in your "Portfolio" spreadsheet
✅ **Enhanced Emails** - Daily changes + weekly summaries on Mondays
✅ **Flexible Data Source** - Read holdings from Sheets OR CSV (your choice)

---

## Prerequisites

- Existing portfolio tracker running successfully
- Google Account with Google Drive access
- GitHub repository with working GitHub Actions

---

## Migration Steps

### Step 1: Create Google Sheet (5 minutes)

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. **Name it exactly "Portfolio"** (case-sensitive)
4. Rename "Sheet1" to "holdings"
5. Add column headers in row 1:
   ```
   Symbol | Shares | PurchaseDate
   ```
6. Copy your positions from `dad_tickers.txt` to the holdings sheet:
   - Column A: Symbol (ticker, e.g., NVDY)
   - Column B: Shares (quantity, e.g., 100)
   - Column C: PurchaseDate in mm/dd/yyyy format (e.g., 01/15/2024)

**Example:**
```
Symbol  | Shares | PurchaseDate
--------|--------|-------------
ABNY    | 100    | 01/15/2024
XOMO    | 100    | 03/25/2024
MSTY    | 100    | 02/28/2024
```

**Important Notes:**
- Date format must be mm/dd/yyyy (NOT yyyy-mm-dd)
- If you have Excel serial dates in dad_tickers.txt (like 45684), convert them to mm/dd/yyyy
- Keep the header row intact

### Step 2: Regenerate OAuth Token (10 minutes)

**Critical**: The new Sheets API permission requires regenerating your refresh token.

1. **Pull the latest code** (includes updated scopes):
   ```bash
   git pull origin main
   ```

2. **Run the token generator**:
   ```bash
   poetry run python get_refresh_token.py
   ```

3. A browser will open - **log in with your Google account**

4. **Grant permissions** - You'll see TWO permission requests:
   - ✅ "View and manage the files in your Google Drive"
   - ✅ **"View and manage your spreadsheets in Google Drive"** ← NEW

5. Click "Allow"

6. **Copy the output** - Save these values:
   ```
   GOOGLE_REFRESH_TOKEN: 1//xxx...
   GOOGLE_CLIENT_ID: xxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET: GOCSPX-xxx...
   ```

### Step 3: Update GitHub Secrets (2 minutes)

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

2. **Update existing secret**:
   - Click on `GOOGLE_REFRESH_TOKEN`
   - Click "Update secret"
   - Paste the **NEW** refresh token from Step 2
   - Click "Update secret"

3. **Verify other secrets are still present**:
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET
   - DRIVE_FOLDER_ID
   - EMAIL_USER
   - EMAIL_PASSWORD
   - EMAIL_TO

**Note**: CLIENT_ID and CLIENT_SECRET should be the same, but the REFRESH_TOKEN **must** be updated.

### Step 4: Test Locally (Optional but Recommended)

Before running in GitHub Actions, test locally:

1. **Set environment variables**:
   ```bash
   # Windows (PowerShell)
   $env:ENABLE_CLOUD="true"
   $env:USE_SHEETS="true"
   $env:GOOGLE_CLIENT_ID="your-client-id"
   $env:GOOGLE_CLIENT_SECRET="your-client-secret"
   $env:GOOGLE_REFRESH_TOKEN="your-new-refresh-token"

   # Or use credentials.json approach (interactive)
   # Just run without setting env vars
   ```

2. **Run the tracker**:
   ```bash
   poetry run portfolio-tracker
   ```

3. **Verify output**:
   - ✅ "Loaded X positions from Google Sheets"
   - ✅ "First snapshot created - historical tracking started!"
   - ✅ Check "Portfolio" spreadsheet for new "snapshots" and "daily_changes" sheets

### Step 5: Run GitHub Action (2 minutes)

1. Go to **Actions** tab in your GitHub repository

2. Select **"Daily Portfolio Update"** workflow

3. Click **"Run workflow"** → **"Run workflow"** (green button)

4. **Monitor the run** - Click on the running workflow to see logs

5. **Check for success indicators**:
   ```
   ✅ Loaded 24 positions from Google Sheets 'Portfolio/holdings'
   ✅ First snapshot created - historical tracking started!
   ✅ Generated trend chart: portfolio_trends.png
   ✅ Appended 1 row to 'snapshots!A:K'
   ✅ Email sent successfully
   ```

6. **Verify in Google Sheets**:
   - Open your "Portfolio" spreadsheet
   - Should now have 3 sheets: holdings, snapshots, daily_changes
   - snapshots sheet should have 2 rows (header + today's snapshot)
   - daily_changes sheet should have only headers (no data yet - need 2+ snapshots)

7. **Check your email**:
   - Subject: "Daily Portfolio Report"
   - Body should show: "HISTORICAL TRACKING STARTED"
   - Attachments: portfolio_report.csv, portfolio_backtest.png, portfolio_trends.png

---

## Post-Migration Verification

### Day 1 (First Run)

**Expected Behavior:**
- ✅ First snapshot created
- ✅ Email says "Historical tracking started"
- ✅ No daily changes (need 2+ snapshots to compare)
- ✅ Trend chart may show single point or be empty

### Day 2 (Second Run)

**Expected Behavior:**
- ✅ Second snapshot created
- ✅ Email shows daily changes (value change, P&L change, etc.)
- ✅ Top gainers and losers populated
- ✅ Trend chart shows line connecting 2 points

### Ongoing

**Expected Behavior:**
- ✅ Daily snapshots appended
- ✅ Daily changes calculated
- ✅ Trend chart shows last 90 days
- ✅ Monday emails include "WEEKLY SUMMARY" section

---

## Rollback Plan

If something goes wrong, you can rollback:

### Option 1: Disable Sheets, Use CSV

Set environment variable in GitHub Actions workflow:
```yaml
USE_SHEETS: "false"  # Change from "true" to "false"
```

The tracker will fallback to reading from `dad_tickers.txt`.

### Option 2: Revert Code

```bash
git revert <commit-hash>
git push
```

**Note**: Historical data in Sheets will be preserved even if you rollback.

---

## Troubleshooting

### Error: "Spreadsheet 'Portfolio' not found"

**Solution**: Check spreadsheet name is exactly "Portfolio" (case-sensitive)

### Error: "No valid Google Drive credentials found"

**Solution**: Regenerate refresh token (Step 2) and update GitHub secret

### Error: "Could not parse date: XX/XX/XXXX"

**Solution**: Ensure PurchaseDate column uses mm/dd/yyyy format, not yyyy-mm-dd

### Error: "Sheets service not initialized"

**Solution**:
1. Verify `USE_SHEETS="true"` in GitHub workflow
2. Regenerate token with new scopes
3. Update `GOOGLE_REFRESH_TOKEN` secret

### Error: "No data found in 'holdings' sheet"

**Solution**:
1. Check holdings sheet has data (not just headers)
2. Verify column names: Symbol, Shares, PurchaseDate

### Daily changes not showing in email

**Solution**: This is normal for first run. Wait until Day 2 for daily changes to appear.

---

## Data Source Control

### Use Sheets (Recommended for GitHub Actions)

```yaml
# In .github/workflows/daily_run.yml
env:
  USE_SHEETS: "true"
```

### Use CSV (Local testing)

```bash
# Set environment variable
export USE_SHEETS="false"
poetry run portfolio-tracker
```

### Priority

1. If `USE_SHEETS=true` and Sheets available → Read from Sheets
2. Otherwise → Read from `dad_tickers.txt` CSV

---

## Updating Holdings

### Before Migration
Edit `dad_tickers.txt` file locally

### After Migration
Edit "holdings" sheet in Google Sheets:
- Add new position: Insert row with Symbol, Shares, PurchaseDate
- Remove position: Delete entire row
- Update shares: Edit Shares column

Changes take effect on next daily run.

---

## FAQ

**Q: Do I need to keep dad_tickers.txt?**
A: Keep it as a backup. The tracker can fallback to CSV if Sheets fails.

**Q: Can I run historical analysis on past data?**
A: Yes! The snapshots sheet contains all daily snapshots. Use Google Sheets charting or export to CSV for analysis.

**Q: How long does historical data persist?**
A: Forever (or until you delete it). Sheets has no expiration. For very long histories (5+ years), consider archiving old data.

**Q: Can I manually edit snapshots or daily_changes sheets?**
A: **No!** These are auto-generated. Manual edits may cause errors. Only edit the "holdings" sheet.

**Q: What if I miss a day?**
A: The tracker calculates days_between and shows total change since last snapshot. Gaps are handled gracefully.

**Q: Can I use a different spreadsheet name?**
A: Not currently. The code expects "Portfolio". You can modify `drive_client.py` if needed.

---

## Next Steps

After successful migration:

1. **Monitor for 1 week** - Ensure daily emails arrive
2. **Verify data accuracy** - Compare metrics to broker statements
3. **Set up Sheets backups** - Use Google Takeout or version history
4. **Explore historical data** - Create custom charts in Sheets
5. **Share feedback** - Report any issues or enhancement ideas

---

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review [CLOUD_SETUP.md](CLOUD_SETUP.md) for detailed setup
3. Review [SHEETS_SCHEMA.md](SHEETS_SCHEMA.md) for data structure
4. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for troubleshooting

---

**Estimated Total Migration Time**: 20-30 minutes

**Complexity**: Medium (requires OAuth re-authentication)

**Risk**: Low (can rollback easily, historical data preserved)
