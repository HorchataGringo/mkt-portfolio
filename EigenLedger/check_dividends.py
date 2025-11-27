import yfinance as yf
import pandas as pd

try:
    print("Fetching actions for AAPL and MSFT...")
    # Try fetching with actions=True
    data = yf.download(["AAPL", "MSFT"], start="2023-01-01", actions=True, progress=False)
    
    print("Columns:", data.columns)
    if "Dividends" in data.columns:
        print("Dividends found!")
        print(data["Dividends"].head())
        print("Total Dividends:\n", data["Dividends"].sum())
    else:
        print("Dividends column NOT found in bulk download.")

    # Try fetching via Ticker for comparison (slower but maybe more reliable?)
    print("\nFetching via Ticker for AAPL...")
    aapl = yf.Ticker("AAPL")
    divs = aapl.dividends
    print("AAPL Dividends (Ticker):\n", divs.loc["2023-01-01":].head())

except Exception as e:
    print(f"Error: {e}")
