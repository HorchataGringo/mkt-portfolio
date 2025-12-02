import pandas as pd
import yfinance as yf
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt

def excel_date_to_datetime(serial):
    # Excel base date is usually Dec 30, 1899
    base = datetime(1899, 12, 30)
    delta = timedelta(days=serial)
    return base + delta

def load_portfolio(filepath, drive_client=None, use_sheets=None):
    """
    Load portfolio from Google Sheets or CSV file.

    Priority controlled by USE_SHEETS environment variable:
    - If USE_SHEETS=true and drive_client provided: Read from Sheets
    - Otherwise: Read from CSV file (filepath)

    Args:
        filepath: Path to CSV file (fallback or local testing)
        drive_client: DriveClient instance (optional)
        use_sheets: Override env variable (for testing)

    Returns:
        DataFrame with columns: Tickers, Quantity, PurchaseDateObj
    """
    import logging

    # Determine source based on env variable
    if use_sheets is None:
        use_sheets = os.environ.get("USE_SHEETS", "false").lower() == "true"

    try:
        # Try Sheets first if enabled and drive_client available
        if use_sheets and drive_client and hasattr(drive_client, 'sheets_service') and drive_client.sheets_service:
            try:
                logging.info("Attempting to load portfolio from Google Sheets...")
                df = drive_client.read_holdings_from_sheet()
                if not df.empty:
                    logging.info(f"Successfully loaded {len(df)} positions from Google Sheets")
                    return df
                else:
                    logging.warning("Sheets returned empty DataFrame. Falling back to CSV.")
            except Exception as e:
                logging.warning(f"Could not read from Sheets: {e}. Falling back to CSV.")

        # Fallback to CSV
        logging.info(f"Loading portfolio from CSV file: {filepath}")
        df = pd.read_csv(filepath)
        # Convert Excel serial date to datetime
        df['PurchaseDateObj'] = df['PurchaseDate'].apply(excel_date_to_datetime)
        logging.info(f"Loaded {len(df)} positions from CSV")
        return df

    except Exception as e:
        logging.error(f"Error loading portfolio: {e}")
        return pd.DataFrame()

def get_column_definitions():
    return pd.DataFrame([
        {"Column": "Ticker", "Definition": "Stock Symbol"},
        {"Column": "Qty", "Definition": "Quantity of shares held"},
        {"Column": "Purch Date", "Definition": "Date of purchase"},
        {"Column": "Purch Price", "Definition": "Price per share at purchase"},
        {"Column": "Cost Basis", "Definition": "Total cost of investment (Qty * Purch Price)"},
        {"Column": "Curr Price", "Definition": "Current market price per share"},
        {"Column": "Mkt Value", "Definition": "Current market value of position (Qty * Curr Price)"},
        {"Column": "Unrealized P&L", "Definition": "Profit or Loss (Mkt Value - Cost Basis)"},
        {"Column": "P&L %", "Definition": "Percentage Profit or Loss"},
        {"Column": "Div Income (4 weeks)", "Definition": "Dividends received in the last 4 weeks"},
        {"Column": "Div Income to date", "Definition": "Total dividends received since purchase"},
        {"Column": "Total Ret ($)", "Definition": "Total Return in dollars (Unrealized P&L + Div Income)"},
        {"Column": "Total Ret (%)", "Definition": "Total Return percentage"},
        {"Column": "Yield on Cost", "Definition": "Annualized dividend yield based on cost basis"},
        {"Column": "CAGR", "Definition": "Compound Annual Growth Rate"},
        {"Column": "Beta", "Definition": "Volatility relative to SPY"}
    ])

def get_portfolio_metrics(portfolio_df):
    tickers = portfolio_df['Tickers'].unique().tolist()
    
    # Add SPY for Beta calculation
    if "SPY" not in tickers:
        download_tickers = tickers + ["SPY"]
    else:
        download_tickers = tickers
        
    print(f"Fetching data for {len(download_tickers)} tickers (including SPY)...")
    
    # We need history from the earliest purchase date to now
    min_date = portfolio_df['PurchaseDateObj'].min()
    start_date = (min_date - timedelta(days=5)).strftime('%Y-%m-%d') # Buffer
    
    # Fetch data including dividends
    data = yf.download(download_tickers, start=start_date, progress=True, actions=True, auto_adjust=False)
    
    # Prepare results list
    results = []
    
    adj_close = data["Adj Close"]
    dividends = data["Dividends"] if "Dividends" in data.columns else pd.DataFrame(0, index=adj_close.index, columns=adj_close.columns)
    
    # Calculate daily returns for Beta
    daily_returns = adj_close.pct_change().dropna()
    spy_returns = daily_returns["SPY"]
    
    current_prices = adj_close.iloc[-1]
    
    for index, row in portfolio_df.iterrows():
        ticker = row['Tickers']
        qty = row['Quantity']
        purchase_date = row['PurchaseDateObj']
        
        # 1. Estimate Purchase Price (Close on Purchase Date)
        try:
            # Get index of date nearest to purchase_date
            idx = adj_close.index.get_indexer([purchase_date], method='nearest')[0]
            purchase_price = adj_close[ticker].iloc[idx]
            actual_purchase_date = adj_close.index[idx]
        except Exception as e:
            print(f"Could not find price for {ticker} on {purchase_date}: {e}")
            purchase_price = 0
            actual_purchase_date = purchase_date

        # 2. Current Metrics
        current_price = current_prices[ticker]
        cost_basis = qty * purchase_price
        market_value = qty * current_price
        unrealized_pl = market_value - cost_basis
        unrealized_pl_pct = (unrealized_pl / cost_basis) * 100 if cost_basis else 0
        
        # 3. Dividend Income
        ticker_divs = dividends[ticker]
        
        # Div Income to date
        relevant_divs = ticker_divs[ticker_divs.index >= actual_purchase_date]
        divs_per_share = relevant_divs.sum()
        total_div_income = divs_per_share * qty
        
        # Div Income (4 weeks)
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        recent_divs = ticker_divs[ticker_divs.index >= four_weeks_ago]
        recent_divs_income = recent_divs.sum() * qty
        
        # 4. Total Return
        total_return = unrealized_pl + total_div_income
        total_return_pct = (total_return / cost_basis) * 100 if cost_basis else 0
        
        # 5. Advanced Metrics
        # Yield on Cost
        yield_on_cost = (divs_per_share / purchase_price) * 100 if purchase_price else 0
        
        # Annualized Return (CAGR)
        days_held = (datetime.now() - actual_purchase_date).days
        years_held = days_held / 365.25
        if years_held > 0 and cost_basis > 0:
            # Ending Value = Market Value + Dividends
            ending_value = market_value + total_div_income
            cagr = ((ending_value / cost_basis) ** (1 / years_held)) - 1
            cagr_pct = cagr * 100
        else:
            cagr_pct = 0
            
        # Beta
        # Calculate beta using returns since purchase date
        try:
            asset_returns = daily_returns[ticker][daily_returns.index >= actual_purchase_date]
            bench_returns = spy_returns[spy_returns.index >= actual_purchase_date]
            
            # Align indices
            common_idx = asset_returns.index.intersection(bench_returns.index)
            asset_returns = asset_returns.loc[common_idx]
            bench_returns = bench_returns.loc[common_idx]
            
            covariance = asset_returns.cov(bench_returns)
            variance = bench_returns.var()
            beta = covariance / variance if variance != 0 else 0
        except Exception as e:
            beta = 0
        
        results.append({
            "Ticker": ticker,
            "Qty": qty,
            "Purch Date": actual_purchase_date.strftime('%Y-%m-%d'),
            "Purch Price": round(purchase_price, 2),
            "Cost Basis": round(cost_basis, 2),
            "Curr Price": round(current_price, 2),
            "Mkt Value": round(market_value, 2),
            "Unrealized P&L": round(unrealized_pl, 2),
            "P&L %": f"{round(unrealized_pl_pct, 2)}%",
            "Div Income (4 weeks)": round(recent_divs_income, 2),
            "Div Income to date": round(total_div_income, 2),
            "Total Ret ($)": round(total_return, 2),
            "Total Ret (%)": f"{round(total_return_pct, 2)}%",
            "Yield on Cost": f"{round(yield_on_cost, 2)}%",
            "CAGR": f"{round(cagr_pct, 2)}%",
            "Beta": round(beta, 2)
        })
        
    return pd.DataFrame(results)

class BacktestEngine:
    """Simple backtest engine for buy-and-hold portfolio analysis."""
    
    def __init__(self, portfolio_df):
        self.portfolio_df = portfolio_df
        self.historical_data = None
        self.portfolio_value_history = None
        self.benchmark_value_history = None

    def _fetch_historical_data(self):
        tickers = self.portfolio_df['Tickers'].unique().tolist()
        # Add SPY as benchmark
        if "SPY" not in tickers:
            tickers_with_benchmark = tickers + ["SPY"]
        else:
            tickers_with_benchmark = tickers
            
        min_date = self.portfolio_df['PurchaseDateObj'].min()
        start_date = (min_date - timedelta(days=5)).strftime('%Y-%m-%d')
        
        print(f"\nFetching historical data for backtest...")
        data = yf.download(tickers_with_benchmark, start=start_date, progress=False, actions=True, auto_adjust=False)
        self.historical_data = data

    def run_backtest(self):
        if self.historical_data is None:
            self._fetch_historical_data()

        if self.historical_data.empty:
            print("No historical data available for backtesting.")
            return

        adj_close = self.historical_data["Adj Close"]
        dividends = self.historical_data["Dividends"] if "Dividends" in self.historical_data.columns else pd.DataFrame(0, index=adj_close.index, columns=adj_close.columns)
        
        # Initialize portfolio value series
        portfolio_value = pd.Series(0.0, index=adj_close.index)
        
        # Track initial investment for comparison
        total_initial_investment = 0
        
        for index, row in self.portfolio_df.iterrows():
            ticker = row['Tickers']
            qty = row['Quantity']
            purchase_date = row['PurchaseDateObj']
            
            if ticker not in adj_close.columns:
                print(f"Warning: Ticker {ticker} not found in historical data. Skipping.")
                continue

            # Find the actual purchase date in the historical data
            try:
                idx = adj_close.index.get_indexer([purchase_date], method='nearest')[0]
                actual_purchase_date = adj_close.index[idx]
                purchase_price = adj_close[ticker].iloc[idx]
                total_initial_investment += purchase_price * qty
            except Exception:
                print(f"Could not find purchase date for {ticker} on {purchase_date}. Skipping.")
                continue

            # Calculate the value of this position over time (from purchase date onward)
            position_value = adj_close[ticker].loc[actual_purchase_date:].copy() * qty
            
            # Add cumulative dividends received
            if ticker in dividends.columns:
                ticker_divs = dividends[ticker].loc[actual_purchase_date:]
                cumulative_divs = ticker_divs.cumsum() * qty
                position_value = position_value + cumulative_divs.reindex(position_value.index, fill_value=0)
            
            # Add to total portfolio value
            portfolio_value = portfolio_value.add(position_value, fill_value=0)
        
        # Only keep dates after first purchase
        self.portfolio_value_history = portfolio_value[portfolio_value > 0]
        
        # Calculate benchmark (SPY) performance for comparison
        if "SPY" in adj_close.columns:
            spy_start_date = self.portfolio_df['PurchaseDateObj'].min()
            spy_idx = adj_close.index.get_indexer([spy_start_date], method='nearest')[0]
            spy_start_price = adj_close["SPY"].iloc[spy_idx]
            
            # Normalize SPY to same initial investment
            spy_shares = total_initial_investment / spy_start_price
            self.benchmark_value_history = (adj_close["SPY"].loc[adj_close.index[spy_idx]:] * spy_shares).dropna()
        
        print("✅ Backtest completed.")

    def plot_results(self, filename="portfolio_backtest.png"):
        if self.portfolio_value_history is None or self.portfolio_value_history.empty:
            print("No backtest results to plot. Run backtest first.")
            return

        plt.figure(figsize=(14, 7))
        
        # Plot portfolio
        plt.plot(self.portfolio_value_history.index, self.portfolio_value_history.values, 
                 label='Your Portfolio', linewidth=2, color='#2E86C1')
        
        # Plot benchmark if available
        if self.benchmark_value_history is not None and not self.benchmark_value_history.empty:
            plt.plot(self.benchmark_value_history.index, self.benchmark_value_history.values, 
                     label='SPY Benchmark', linewidth=2, color='#E74C3C', linestyle='--')
        
        import matplotlib.ticker as mtick
        
        plt.title('Portfolio Historical Performance (Buy & Hold)', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Portfolio Value ($)', fontsize=12)
        plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        plt.tight_layout()
        
        try:
            plt.savefig(filename, dpi=150)
            print(f"📊 Backtest chart saved to: {filename}")
        except Exception as e:
            print(f"Error saving plot: {e}")
        
        plt.show()

def format_movers(movers_list):
    """Format top gainers/losers for email display."""
    if not movers_list:
        return "  No data"

    lines = []
    for i, mover in enumerate(movers_list, 1):
        ticker = mover['ticker']
        pct = mover['price_change_pct']
        is_new = mover.get('is_new', False)
        is_sold = mover.get('is_sold', False)

        if is_new:
            lines.append(f"  {i}. {ticker}: NEW POSITION")
        elif is_sold:
            lines.append(f"  {i}. {ticker}: SOLD")
        else:
            lines.append(f"  {i}. {ticker}: {pct:+.2f}%")

    return "\n".join(lines)


def format_email_with_changes(summary_str, dashboard_str, daily_changes):
    """Format email body with daily changes and summary."""
    from datetime import datetime

    # Header
    email_body = f"Daily Portfolio Update - {datetime.now().strftime('%A, %B %d, %Y')}\n"
    email_body += "=" * 80 + "\n\n"

    # Daily changes section (if available)
    if daily_changes and not daily_changes.get('is_first_run'):
        email_body += f"📊 DAILY CHANGES (vs {daily_changes['prev_date']})\n"
        email_body += "=" * 80 + "\n"
        email_body += f"Portfolio Value Change: ${daily_changes['value_change']:,.2f} ({daily_changes['value_change_pct']:+.2f}%)\n"
        email_body += f"P&L Change:            ${daily_changes['pl_change']:,.2f}\n"
        email_body += f"New Dividends:         ${daily_changes['div_change']:,.2f}\n"
        email_body += f"Total Return Change:   ${daily_changes['return_change']:,.2f}\n\n"

        email_body += "🔥 Top Gainers:\n"
        email_body += format_movers(daily_changes['top_gainers']) + "\n\n"

        email_body += "📉 Top Losers:\n"
        email_body += format_movers(daily_changes['top_losers']) + "\n\n"

    elif daily_changes and daily_changes.get('is_first_run'):
        email_body += "📊 HISTORICAL TRACKING STARTED\n"
        email_body += "=" * 80 + "\n"
        email_body += "This is the first snapshot. Daily changes will appear in tomorrow's report!\n\n"

    # Weekly summary on Mondays
    day_of_week = datetime.now().strftime('%A')
    if day_of_week == 'Monday':
        email_body += "📅 WEEKLY SUMMARY\n"
        email_body += "=" * 80 + "\n"
        email_body += "Check the attached trend chart for 90-day performance history.\n"
        email_body += "Review your position allocations and rebalance if needed.\n\n"

    # Portfolio summary
    email_body += "📈 PORTFOLIO SUMMARY\n"
    email_body += "=" * 80 + "\n"
    email_body += summary_str + "\n"

    # Dashboard
    email_body += "📊 PORTFOLIO DASHBOARD\n"
    email_body += "=" * 80 + "\n"
    email_body += dashboard_str + "\n\n"

    # Footer
    email_body += "=" * 80 + "\n"
    email_body += "Attachments:\n"
    email_body += "  - portfolio_report.csv (detailed metrics)\n"
    email_body += "  - portfolio_report.xlsx (Excel report)\n"
    email_body += "  - portfolio_backtest.png (performance vs SPY)\n"
    email_body += "  - portfolio_trends.png (90-day trend chart)\n\n"
    email_body += "Generated by EigenLedger Portfolio Tracker\n"

    return email_body


def main():
    """Main entry point for portfolio tracker."""
    # Cloud Integration Imports
    from EigenLedger.drive_client import DriveClient
    from EigenLedger.email_client import EmailClient
    import logging

    logging.basicConfig(level=logging.INFO)

    # Use pathlib for better path handling
    base_dir = Path(__file__).parent.parent
    dad_tickers_path = base_dir / "dad_tickers.txt"

    # Check for Cloud Mode
    ENABLE_CLOUD = os.environ.get("ENABLE_CLOUD", "false").lower() == "true"
    drive_client = None
    email_client = None

    if ENABLE_CLOUD:
        logging.info("Cloud mode enabled. Initializing clients...")
        drive_client = DriveClient()
        email_client = EmailClient()

        # Download tickers from Drive only if not using Sheets
        USE_SHEETS = os.environ.get("USE_SHEETS", "false").lower() == "true"
        FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

        if not USE_SHEETS:
            # Only download CSV file if we're not reading from Sheets
            if drive_client.download_file("dad_tickers.txt", str(dad_tickers_path), folder_id=FOLDER_ID):
                logging.info("Downloaded dad_tickers.txt from Drive.")
            else:
                logging.warning("Could not download dad_tickers.txt from Drive. Using local copy if available.")
        else:
            logging.info("USE_SHEETS=true - Will read portfolio from Google Sheets instead of CSV")

    # Load portfolio (from Sheets if USE_SHEETS=true, otherwise CSV)
    print(f"Loading portfolio...")
    df = load_portfolio(str(dad_tickers_path), drive_client=drive_client)

    if df.empty:
        logging.error("Portfolio data is empty or invalid. Exiting.")
        sys.exit(1)

    metrics = get_portfolio_metrics(df)

    print("\n" + "="*80)
    print("📊 PORTFOLIO DASHBOARD")
    print("="*80)
    # Reorder columns for readability
    cols = ["Ticker", "Qty", "Purch Date", "Purch Price", "Cost Basis", "Curr Price", "Mkt Value", "Unrealized P&L", "P&L %", "Div Income (4 weeks)", "Div Income to date", "Total Ret ($)", "Total Ret (%)", "Yield on Cost", "CAGR", "Beta"]
    
    # Create formatted version for Output (Console, CSV, Excel)
    display_metrics = metrics.copy()
    currency_cols = ["Purch Price", "Cost Basis", "Curr Price", "Mkt Value", "Unrealized P&L", 
                     "Div Income (4 weeks)", "Div Income to date", "Total Ret ($)"]
    for col in currency_cols:
        display_metrics[col] = display_metrics[col].apply(lambda x: f"${x:,.2f}")

    dashboard_str = display_metrics[cols].to_string(index=False)
    print(dashboard_str)

    print("\n" + "="*80)
    print("📈 PORTFOLIO SUMMARY")
    print("="*80)
    total_invested = metrics["Cost Basis"].sum()
    total_value = metrics["Mkt Value"].sum()
    total_divs = metrics["Div Income to date"].sum()
    total_pl = total_value - total_invested
    total_ret = total_pl + total_divs

    summary_str = f"""
Total Invested:   ${total_invested:,.2f}
Current Value:    ${total_value:,.2f}
Unrealized P&L:   ${total_pl:,.2f} ({(total_pl/total_invested)*100:.2f}%)
Dividend Income:  ${total_divs:,.2f}
Total Return:     ${total_ret:,.2f} ({(total_ret/total_invested)*100:.2f}%)
"""
    print(summary_str)

    # Backtest Analysis
    print("="*80)
    print("⏳ RUNNING BACKTEST ANALYSIS")
    print("="*80)

    engine = BacktestEngine(df)
    engine.run_backtest()

    backtest_plot_path = base_dir / "portfolio_backtest.png"
    engine.plot_results(str(backtest_plot_path))

    # Historical Tracking (Sheets Integration)
    daily_changes = None
    trend_chart_path = base_dir / "portfolio_trends.png"

    # Debug logging for Sheets integration
    logging.info(f"ENABLE_CLOUD: {ENABLE_CLOUD}")
    logging.info(f"drive_client exists: {drive_client is not None}")
    if drive_client:
        logging.info(f"drive_client.sheets_service exists: {hasattr(drive_client, 'sheets_service')}")
        logging.info(f"drive_client.sheets_service value: {drive_client.sheets_service is not None if hasattr(drive_client, 'sheets_service') else 'N/A'}")

    if ENABLE_CLOUD and drive_client and hasattr(drive_client, 'sheets_service') and drive_client.sheets_service:
        print("\n" + "="*80)
        print("📈 HISTORICAL TRACKING")
        print("="*80)

        try:
            from EigenLedger.historical_tracker import HistoricalTracker

            # Initialize tracker
            logging.info("Initializing HistoricalTracker...")
            tracker = HistoricalTracker(drive_client)

            # Create current snapshot
            logging.info("Creating current snapshot...")
            current_snapshot = tracker.create_snapshot(df, metrics)

            # Get previous snapshot
            logging.info("Retrieving previous snapshot...")
            previous_snapshot = tracker.get_last_snapshot()

            # Calculate daily changes
            logging.info("Calculating daily changes...")
            daily_changes = tracker.calculate_daily_changes(current_snapshot, previous_snapshot)

            # Save current snapshot
            logging.info("Saving current snapshot...")
            tracker.save_snapshot(current_snapshot)

            # Save position history (individual stock values)
            logging.info("Saving position history...")
            tracker.save_position_history(current_snapshot)

            # Save daily changes
            if daily_changes:
                tracker.save_daily_changes(daily_changes)

                if daily_changes['is_first_run']:
                    print("✅ First snapshot created - historical tracking started!")
                    logging.info("First snapshot created successfully")
                else:
                    print(f"✅ Daily changes calculated (vs {daily_changes['prev_date']})")
                    print(f"   Portfolio Value Change: ${daily_changes['value_change']:,.2f} ({daily_changes['value_change_pct']:+.2f}%)")
                    logging.info(f"Daily changes saved: {daily_changes['date']} vs {daily_changes['prev_date']}")

            # Generate trend chart
            logging.info("Generating trend chart...")
            tracker.generate_trend_chart(filename=str(trend_chart_path), days=90)

        except Exception as e:
            logging.error(f"Error in historical tracking: {e}", exc_info=True)
            logging.warning("Continuing without historical tracking...")
    else:
        logging.warning("Historical tracking skipped - Sheets service not available")
        logging.warning("This means snapshots and daily changes will NOT be saved to Google Sheets")

    # Save report to CSV (Local)
    report_csv_path = base_dir / "portfolio_report.csv"
    display_metrics.to_csv(str(report_csv_path), index=False)
    print(f"Saved CSV report to {report_csv_path}")
    
    # Save report to Excel (Cloud/Local)
    report_xlsx_path = base_dir / "portfolio_report.xlsx"
    try:
        with pd.ExcelWriter(report_xlsx_path, engine='openpyxl') as writer:
            display_metrics.to_excel(writer, sheet_name='Portfolio Metrics', index=False)
            get_column_definitions().to_excel(writer, sheet_name='Definitions', index=False)
        print(f"Saved Excel report to {report_xlsx_path}")
    except Exception as e:
        print(f"Error saving Excel report: {e}")

    # Cloud Actions: Upload and Email
    if ENABLE_CLOUD:
        # Upload to Drive
        if drive_client:
            # Upload Excel file instead of CSV
            drive_client.upload_file(str(report_xlsx_path), folder_id=FOLDER_ID)
            if backtest_plot_path.exists():
                drive_client.upload_file(str(backtest_plot_path), folder_id=FOLDER_ID)
            if trend_chart_path.exists():
                drive_client.upload_file(str(trend_chart_path), folder_id=FOLDER_ID)

        # Send Email
        if email_client:
            # Build email body with daily changes if available
            email_body = format_email_with_changes(summary_str, dashboard_str, daily_changes)

            to_email = os.environ.get("EMAIL_TO", email_client.username)
            attachments = [str(report_xlsx_path)] # Attach Excel
            if backtest_plot_path.exists():
                attachments.append(str(backtest_plot_path))
            if trend_chart_path.exists():
                attachments.append(str(trend_chart_path))

            # Determine subject based on day of week
            from datetime import datetime
            day_of_week = datetime.now().strftime('%A')
            if day_of_week == 'Monday':
                subject = "Weekly Portfolio Summary + Daily Update"
            else:
                subject = "Daily Portfolio Report"

            print(f"Attempting to send email to {to_email}...")
            if email_client.send_email(subject, email_body, to_email, attachments=attachments):
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email. Check logs for details.")

    print("\n" + "="*80)
    print("✅ Portfolio analysis complete!")
    print("="*80)


if __name__ == "__main__":
    main()
