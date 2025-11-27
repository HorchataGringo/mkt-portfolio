import yfinance as yf
import pandas as pd
import os

# Read dad_tickers.txt
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dad_tickers_path = os.path.join(base_dir, "dad_tickers.txt")

try:
    with open(dad_tickers_path, "r") as f:
        dad_tickers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Error: Could not find {dad_tickers_path}")
    dad_tickers = []

# Initial stock symbols
initial_symbols = ["AAPL", "MSFT", "GOOGL"]

# Combine symbols
portfolio_symbols = list(set(initial_symbols + dad_tickers))

print(f"Downloading data for {len(portfolio_symbols)} symbols: {portfolio_symbols}")

# Download data
try:
    data = yf.download(portfolio_symbols, start="2023-01-01", progress=True, auto_adjust=False)["Adj Close"]
    print("\nDownload complete.")
    print(data.head())
    print("\nSummary:")
    print(data.describe())
except Exception as e:
    print(f"Error downloading data: {e}")
