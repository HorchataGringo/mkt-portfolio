import yfinance as yf
import pandas as pd

try:
    print("Downloading multiple tickers with GOOGL...")
    data = yf.download(["AAPL", "MSFT", "GOOGL"], start="2023-01-01", progress=False, auto_adjust=False)
    adj_close = data["Adj Close"]
    print("Adj Close Head:\n", adj_close.head())
    
    dropped = adj_close.bfill().dropna()
    print("Dropped Shape:", dropped.shape)
    print("Dropped Head:\n", dropped.head())

except Exception as e:
    print(f"Error: {e}")
