# Google Sheets Schema Documentation

This document describes the structure of the Google Sheets spreadsheet used for portfolio tracking.

## Spreadsheet Name

**Portfolio** (case-sensitive)

---

## Sheet 1: holdings

**Purpose**: Current portfolio positions (user-maintained input)

**Status**: User edits this sheet to update holdings

### Schema

| Column | Type | Format | Description | Example |
|--------|------|--------|-------------|---------|
| Symbol | TEXT | Ticker symbol | Stock ticker | NVDY |
| Shares | NUMBER | Integer or decimal | Number of shares owned | 100 |
| PurchaseDate | TEXT | mm/dd/yyyy | Date when position was purchased | 01/15/2024 |

### Example Data

```
Symbol  | Shares | PurchaseDate
--------|--------|-------------
NVDY    | 100    | 01/15/2024
MSTY    | 100    | 02/20/2024
AMZY    | 100    | 03/10/2024
```

### Notes

- **Do NOT delete the header row**
- Shares can be fractional (e.g., 100.5)
- Date must be in mm/dd/yyyy format (e.g., 01/15/2024, not 1/15/24)
- Symbol should be a valid ticker that yfinance can recognize
- To add a position: Insert a new row with Symbol, Shares, PurchaseDate
- To remove a position: Delete the entire row
- Spreadsheet automatically updates daily snapshots based on this data

---

## Sheet 2: snapshots

**Purpose**: Daily portfolio snapshots (append-only, auto-generated)

**Status**: Managed by tracker - DO NOT manually edit

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| timestamp | DATETIME | ISO 8601 timestamp of snapshot | 2025-01-15T13:00:00Z |
| date | DATE | Date only (for filtering/grouping) | 2025-01-15 |
| total_value | NUMBER | Current market value of portfolio | 125430.50 |
| total_cost | NUMBER | Total cost basis | 98500.00 |
| unrealized_pl | NUMBER | Unrealized profit/loss | 26930.50 |
| unrealized_pl_pct | NUMBER | Unrealized P&L as percentage | 27.34 |
| dividend_income | NUMBER | Total dividends received | 3420.00 |
| total_return | NUMBER | Total return (P&L + dividends) | 30350.50 |
| total_return_pct | NUMBER | Total return as percentage | 30.81 |
| position_count | NUMBER | Number of positions | 24 |
| snapshot_json | JSON STRING | Full portfolio state | {"positions": [...]} |

### snapshot_json Structure

```json
{
  "timestamp": "2025-01-15T13:00:00Z",
  "date": "2025-01-15",
  "summary": {
    "total_value": 125430.50,
    "total_cost": 98500.00,
    "unrealized_pl": 26930.50,
    "unrealized_pl_pct": 27.34,
    "dividend_income": 3420.00,
    "total_return": 30350.50,
    "total_return_pct": 30.81,
    "position_count": 24
  },
  "positions": [
    {
      "ticker": "NVDY",
      "qty": 100,
      "purchase_date": "2024-01-15",
      "purchase_price": 25.50,
      "current_price": 32.75,
      "cost_basis": 2550.00,
      "market_value": 3275.00,
      "unrealized_pl": 725.00,
      "pl_pct": 28.43,
      "dividend_income": 150.00,
      "total_return": 875.00,
      "total_return_pct": 34.31,
      "yield_on_cost": 5.88,
      "cagr": 28.50,
      "beta": 1.15
    }
  ]
}
```

### Notes

- New row appended daily at 13:00 UTC (9:00 AM EST)
- One snapshot per day
- snapshot_json contains complete state for historical reconstruction
- **Do not manually edit this sheet** - tracker manages it
- For analysis: Use columns A-J for charting/filtering, use snapshot_json for detailed drill-down

---

## Sheet 3: daily_changes

**Purpose**: Day-over-day changes and analytics (append-only, auto-generated)

**Status**: Managed by tracker - DO NOT manually edit

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | DATE | Date of current snapshot | 2025-01-15 |
| prev_date | DATE | Date of previous snapshot | 2025-01-14 |
| value_change | NUMBER | Change in total value | 1250.75 |
| value_change_pct | NUMBER | Percentage change in value | 1.01 |
| pl_change | NUMBER | Change in unrealized P&L | 1150.50 |
| div_change | NUMBER | New dividends received | 100.25 |
| return_change | NUMBER | Change in total return | 1250.75 |
| top_gainers | JSON STRING | Top 3 gainers | [{"ticker":"NVDY","price_change_pct":5.2}] |
| top_losers | JSON STRING | Top 3 losers | [{"ticker":"SLTY","price_change_pct":-2.1}] |
| notes | TEXT | Special events/notes | "Days between: 1" |

### top_gainers/top_losers JSON Structure

```json
[
  {
    "ticker": "NVDY",
    "price_change": 1.25,
    "price_change_pct": 5.20,
    "value_change": 125.00,
    "is_new": false
  },
  {
    "ticker": "MSTY",
    "price_change": 0.85,
    "price_change_pct": 3.10,
    "value_change": 85.00,
    "is_new": false
  }
]
```

### Special Position Flags

| Flag | Meaning | Example |
|------|---------|---------|
| `is_new: true` | New position added | Position didn't exist yesterday |
| `is_sold: true` | Position removed | Position existed yesterday but not today |
| `price_change_pct: 100.0` | New position | Full price shown as "change" |
| `price_change_pct: -100.0` | Sold position | Full price negated |

### Notes

- First row will NOT be created on first snapshot (no previous data to compare)
- Daily changes calculated as: current - previous
- top_gainers/top_losers sorted by price_change_pct
- notes field may contain days_between if snapshots are not consecutive days

---

## Sheet 4: position_history

**Purpose**: Daily values for each individual position (append-only, auto-generated)

**Status**: Managed by tracker - DO NOT manually edit

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date | DATE | Date of snapshot | 2025-01-15 |
| ticker | TEXT | Stock ticker symbol | NVDY |
| qty | NUMBER | Number of shares | 100 |
| purchase_date | DATE | Original purchase date | 2024-01-15 |
| purchase_price | NUMBER | Price paid per share | 25.50 |
| current_price | NUMBER | Current price per share | 32.75 |
| cost_basis | NUMBER | Total cost (qty × purchase price) | 2550.00 |
| market_value | NUMBER | Current value (qty × current price) | 3275.00 |
| unrealized_pl | NUMBER | Unrealized P&L ($ amount) | 725.00 |
| pl_pct | NUMBER | Unrealized P&L percentage | 28.43 |
| dividend_income | NUMBER | Total dividends received | 150.00 |
| total_return | NUMBER | Total return (P&L + dividends) | 875.00 |
| total_return_pct | NUMBER | Total return percentage | 34.31 |

### Example Data

```
date        | ticker | qty | purchase_date | purchase_price | current_price | cost_basis | market_value | unrealized_pl | pl_pct | dividend_income | total_return | total_return_pct
------------|--------|-----|---------------|----------------|---------------|------------|--------------|---------------|--------|-----------------|--------------|------------------
2025-01-15  | NVDY   | 100 | 2024-01-15    | 25.50          | 32.75         | 2550.00    | 3275.00      | 725.00        | 28.43  | 150.00          | 875.00       | 34.31
2025-01-15  | MSTY   | 100 | 2024-02-20    | 18.25          | 22.10         | 1825.00    | 2210.00      | 385.00        | 21.10  | 85.00           | 470.00       | 25.75
2025-01-16  | NVDY   | 100 | 2024-01-15    | 25.50          | 33.10         | 2550.00    | 3310.00      | 760.00        | 29.80  | 150.00          | 910.00       | 35.69
2025-01-16  | MSTY   | 100 | 2024-02-20    | 18.25          | 21.85         | 1825.00    | 2185.00      | 360.00        | 19.73  | 85.00           | 445.00       | 24.38
```

### Notes

- One row per position per day (if you have 20 positions, you get 20 rows per day)
- Allows you to track individual stock performance over time
- Can chart any single stock's value progression
- Can filter by ticker to see one stock's history
- Can compare multiple stocks side-by-side

### Use Cases

**Track a specific stock over time:**
```
Filter: ticker = "NVDY"
Result: See daily values for NVDY only
```

**Compare two stocks:**
```
Filter: ticker IN ("NVDY", "MSTY")
Chart: market_value over time, grouped by ticker
```

**Find best/worst performers:**
```
Filter: date = "2025-01-15"
Sort by: pl_pct DESC
Result: See which stocks performed best on that day
```

---

## Data Flow

```
User Updates → holdings sheet
                  ↓
         Daily GitHub Action runs
                  ↓
    Tracker reads holdings sheet
                  ↓
     Fetches prices from yfinance
                  ↓
    Calculates current metrics
                  ↓
    Retrieves last snapshot from snapshots sheet
                  ↓
    Calculates daily changes
                  ↓
    Appends new snapshot to snapshots sheet
                  ↓
    Appends position data to position_history sheet
                  ↓
    Appends daily changes to daily_changes sheet
                  ↓
         Sends email with report
```

---

## Querying Examples

### Get Latest Portfolio Value

```
=INDEX(snapshots!C:C, COUNTA(snapshots!C:C))
```

### Get 30-Day Return

```
=(LATEST_VALUE - VALUE_30_DAYS_AGO) / VALUE_30_DAYS_AGO
```

### Chart Portfolio Value Over Time

1. Select snapshots!B:C (date and total_value columns)
2. Insert → Chart
3. Chart type: Line chart
4. X-axis: date
5. Y-axis: total_value

---

## Maintenance

### Archive Old Data (Optional)

After 5 years, you may want to archive old snapshots:

1. Create new sheet: "snapshots_archive"
2. Move rows older than 5 years to archive sheet
3. Keep last 2 years in main snapshots sheet

### Backup

**Recommended**: Set up automatic backups

1. Google Sheets → File → Version history
2. Or use Google Takeout to export periodically

---

## Troubleshooting

### Issue: Duplicate snapshots on same date

**Cause**: Script ran twice in one day

**Solution**: Manually delete duplicate row (keep the later one)

### Issue: Missing snapshots for specific dates

**Cause**: GitHub Action failed or was skipped

**Solution**: Check GitHub Actions logs. Gaps are normal (weekends, holidays).

### Issue: snapshot_json is corrupted

**Cause**: Manual editing or script error

**Solution**: Delete corrupted row. Script will create new snapshot next run.

### Issue: holdings sheet changes not reflected

**Cause**: USE_SHEETS environment variable not set to "true"

**Solution**: Check GitHub workflow has `USE_SHEETS: "true"`

---

## Best Practices

1. **Never manually edit snapshots or daily_changes sheets**
2. **Always use mm/dd/yyyy format for PurchaseDate in holdings**
3. **Keep header rows intact in all sheets**
4. **Don't rename the spreadsheet or sheets**
5. **Back up data before making bulk changes to holdings**
6. **Verify ticker symbols are valid before adding to holdings**

---

## Version History

- **v1.0** (2025-01-27): Initial schema with historical tracking
