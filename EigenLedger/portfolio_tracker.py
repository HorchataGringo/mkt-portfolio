import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

def excel_date_to_datetime(serial):
    # Excel base date is usually Dec 30, 1899
    base = datetime(1899, 12, 30)
    delta = timedelta(days=serial)
    return base + delta

def load_portfolio(filepath):
    try:
        df = pd.read_csv(filepath)
        # Convert Excel serial date to datetime
        df['PurchaseDateObj'] = df['PurchaseDate'].apply(excel_date_to_datetime)
        return df
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return pd.DataFrame()

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
        relevant_divs = ticker_divs[ticker_divs.index >= actual_purchase_date]
        divs_per_share = relevant_divs.sum()
        total_div_income = divs_per_share * qty
        
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
            "Div Income": round(total_div_income, 2),
            "Total Ret ($)": round(total_return, 2),
            "Total Ret (%)": f"{round(total_return_pct, 2)}%",
            "Yield on Cost": f"{round(yield_on_cost, 2)}%",
            "CAGR": f"{round(cagr_pct, 2)}%",
            "Beta": round(beta, 2)
        })
        
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Cloud Integration Imports
    from EigenLedger.drive_client import DriveClient
    from EigenLedger.email_client import EmailClient
    import logging

    logging.basicConfig(level=logging.INFO)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dad_tickers_path = os.path.join(base_dir, "dad_tickers.txt")
    
    # Check for Cloud Mode
    ENABLE_CLOUD = os.environ.get("ENABLE_CLOUD", "false").lower() == "true"
    drive_client = None
    email_client = None

    if ENABLE_CLOUD:
        logging.info("Cloud mode enabled. Initializing clients...")
        drive_client = DriveClient()
        email_client = EmailClient()
        
        # Download tickers from Drive
        FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
        if drive_client.download_file("dad_tickers.txt", dad_tickers_path, folder_id=FOLDER_ID):
            logging.info("Downloaded dad_tickers.txt from Drive.")
        else:
            logging.warning("Could not download dad_tickers.txt from Drive. Using local copy if available.")

    print(f"Loading portfolio from {dad_tickers_path}...")
    df = load_portfolio(dad_tickers_path)
    
    if not df.empty:
        metrics = get_portfolio_metrics(df)
        
        print("\n--- Portfolio Dashboard ---")
        # Reorder columns for readability
        cols = ["Ticker", "Qty", "Purch Date", "Purch Price", "Curr Price", "Cost Basis", "Mkt Value", "P&L %", "Div Income", "Total Ret (%)", "Yield on Cost", "CAGR", "Beta"]
        dashboard_str = metrics[cols].to_string(index=False)
        print(dashboard_str)
        
        print("\n--- Summary ---")
        total_invested = metrics["Cost Basis"].sum()
        total_value = metrics["Mkt Value"].sum()
        total_divs = metrics["Div Income"].sum()
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
        
        # Cloud Actions: Upload and Email
        if ENABLE_CLOUD:
            # Save report to CSV
            report_path = os.path.join(base_dir, "portfolio_report.csv")
            metrics.to_csv(report_path, index=False)
            
            # Upload to Drive
            if drive_client:
                drive_client.upload_file(report_path, folder_id=FOLDER_ID)
                
            # Send Email
            if email_client:
                email_body = f"Daily Portfolio Update:\n\n{summary_str}\n\nDashboard:\n{dashboard_str}"
                to_email = os.environ.get("EMAIL_TO", email_client.username) # Default to self if not specified
                email_client.send_email("Daily Portfolio Report", email_body, to_email, attachments=[report_path])

