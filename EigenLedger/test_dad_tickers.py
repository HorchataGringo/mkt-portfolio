import pandas as pd
import os
from main import portfolio_analysis, Engine

# Read dad_tickers.txt
# Assuming the script is run from EigenLedger directory or root, we need to find the file.
# The file is at the root of the repo: c:\Users\seano\Code\Portfolio_Mgmt\EigenLedger-main\dad_tickers.txt

# Get the absolute path to the file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dad_tickers_path = os.path.join(base_dir, "dad_tickers.txt")

# Load dad_tickers.txt using pandas since it's now a CSV
try:
    dad_df = pd.read_csv(dad_tickers_path)
    dad_tickers = dad_df["Tickers"].tolist()
except Exception as e:
    print(f"Error reading dad_tickers.txt: {e}")
    dad_tickers = []

# Initial stock symbols from run.py
initial_symbols = ["AAPL", "MSFT", "GOOGL"]

# Combine symbols
portfolio_symbols = list(set(initial_symbols + dad_tickers))

print(f"Testing with {len(portfolio_symbols)} symbols: {portfolio_symbols}")

# Initialize Engine
# We let it fetch data from yfinance by not providing 'data' argument
portfolio = Engine(
    start_date="2023-01-01",
    portfolio=portfolio_symbols,
    weights=None, # Defaults to equal weights
    benchmark=["SPY"]
)

# Analyze
portfolio_analysis(portfolio)
