from main import portfolio_analysis, Engine
import pandas as pd

print("Testing environment with standard tickers...")

portfolio = Engine(
    start_date="2023-01-01",
    portfolio=["AAPL", "MSFT", "GOOGL"],
    weights=[0.4, 0.3, 0.3],
    benchmark=["SPY"]
)

portfolio_analysis(portfolio)
print("Environment test passed!")
