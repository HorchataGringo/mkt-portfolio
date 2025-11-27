import yfinance as yf
import pandas as pd

try:
    print("Downloading AAPL...")
    data = yf.download("AAPL", start="2023-01-01", progress=False, auto_adjust=False)
    print("Shape:", data.shape)
    print("Columns:", data.columns)
    print("Adj Close empty?", data["Adj Close"].empty)
    
    print("\nDownloading INVALID_TICKER...")
    data_bad = yf.download("INVALID_TICKER_XYZ", start="2023-01-01", progress=False, auto_adjust=False)
    print("Shape:", data_bad.shape)
    print("Columns:", data_bad.columns)
    if "Adj Close" in data_bad.columns:
        print("Adj Close empty?", data_bad["Adj Close"].empty)
    else:
        print("Adj Close not in columns")

except Exception as e:
    print(f"Error: {e}")
