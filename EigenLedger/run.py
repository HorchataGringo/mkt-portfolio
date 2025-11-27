from main import portfolio_analysis, Engine
import pandas as pd
import os

# Define custom data (Commented out to use dad_tickers)
# portfolio_data = pd.DataFrame({
#     "AAPL": [145.0, 147.0, 149.0],
#     "MSFT": [240.0, 242.0, 245.0],
#     "GOOGL": [2700.0, 2725.0, 2750.0],
# }, index=pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]))

# benchmark_data = pd.DataFrame({
#     "TGT": [420.0, 425.0, 430.0],
# }, index=pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]))

# Load dad_tickers.txt
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dad_tickers_path = os.path.join(base_dir, "dad_tickers.txt")

try:
    with open(dad_tickers_path, "r") as f:
        dad_tickers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Warning: {dad_tickers_path} not found. Using default symbols.")
    dad_tickers = []

initial_symbols = ["AAPL", "MSFT", "GOOGL"]
portfolio_symbols = list(set(initial_symbols + dad_tickers))

print(f"Running portfolio analysis for: {portfolio_symbols}")

portfolio = Engine(
    start_date="2023-01-01",
    portfolio=portfolio_symbols,
    weights=None, # Equal weights
    # data=portfolio_data, # Let it fetch from yfinance
    benchmark=["SPY"],
    # benchmark_data=benchmark_data
)

# Fetch benchmark data and analyze
# portfolio.fetch_benchmark_data() # Engine does this internally if needed or we can call it
portfolio_analysis(portfolio)

