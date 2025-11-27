import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class HistoricalTracker:
    """Manages historical portfolio snapshots and daily changes in Google Sheets."""

    def __init__(self, drive_client, spreadsheet_name="Portfolio"):
        """
        Initialize Historical Tracker.

        Args:
            drive_client: DriveClient instance with Sheets API access
            spreadsheet_name: Name of the Google Sheets spreadsheet
        """
        self.drive_client = drive_client
        self.spreadsheet_name = spreadsheet_name
        self.spreadsheet_id = None
        self._init_spreadsheet()

    def _init_spreadsheet(self):
        """Find spreadsheet and ensure required sheets exist."""
        try:
            # Find spreadsheet by name
            self.spreadsheet_id = self.drive_client.find_spreadsheet_by_name(self.spreadsheet_name)
            if not self.spreadsheet_id:
                raise ValueError(f"Spreadsheet '{self.spreadsheet_name}' not found. Please create it first.")

            # Ensure 'snapshots' and 'daily_changes' sheets exist
            self.drive_client.get_or_create_sheet(self.spreadsheet_id, 'snapshots')
            self.drive_client.get_or_create_sheet(self.spreadsheet_id, 'daily_changes')

            # Initialize headers if sheets are empty
            self._init_snapshots_headers()
            self._init_daily_changes_headers()

            logging.info(f"Historical tracker initialized for spreadsheet '{self.spreadsheet_name}'")

        except Exception as e:
            logging.error(f"Error initializing historical tracker: {e}")
            raise

    def _init_snapshots_headers(self):
        """Initialize headers for snapshots sheet if empty."""
        try:
            values = self.drive_client.get_sheet_values(self.spreadsheet_id, 'snapshots!A1:K1')
            if not values:
                # Sheet is empty, add headers
                headers = [
                    'timestamp', 'date', 'total_value', 'total_cost', 'unrealized_pl',
                    'unrealized_pl_pct', 'dividend_income', 'total_return', 'total_return_pct',
                    'position_count', 'snapshot_json'
                ]
                self.drive_client.append_sheet_row(self.spreadsheet_id, 'snapshots!A1', headers)
                logging.info("Initialized snapshots sheet with headers")
        except Exception as e:
            logging.error(f"Error initializing snapshots headers: {e}")

    def _init_daily_changes_headers(self):
        """Initialize headers for daily_changes sheet if empty."""
        try:
            values = self.drive_client.get_sheet_values(self.spreadsheet_id, 'daily_changes!A1:J1')
            if not values:
                # Sheet is empty, add headers
                headers = [
                    'date', 'prev_date', 'value_change', 'value_change_pct', 'pl_change',
                    'div_change', 'return_change', 'top_gainers', 'top_losers', 'notes'
                ]
                self.drive_client.append_sheet_row(self.spreadsheet_id, 'daily_changes!A1', headers)
                logging.info("Initialized daily_changes sheet with headers")
        except Exception as e:
            logging.error(f"Error initializing daily_changes headers: {e}")

    def create_snapshot(self, portfolio_df, metrics_df):
        """
        Create a portfolio snapshot from current data.

        Args:
            portfolio_df: DataFrame with columns [Ticker, Qty, PurchaseDateObj, ...]
            metrics_df: DataFrame with portfolio metrics

        Returns:
            dict: Snapshot data with summary and positions
        """
        try:
            timestamp = datetime.now().isoformat()
            date = datetime.now().strftime('%Y-%m-%d')

            # Build positions list
            positions = []
            for _, row in metrics_df.iterrows():
                positions.append({
                    'ticker': row['Ticker'],
                    'qty': row['Qty'],
                    'purchase_date': row['Purch Date'],
                    'purchase_price': row['Purch Price'],
                    'current_price': row['Curr Price'],
                    'cost_basis': row['Cost Basis'],
                    'market_value': row['Mkt Value'],
                    'unrealized_pl': row['Unrealized P&L'],
                    'pl_pct': float(row['P&L %'].rstrip('%')),
                    'dividend_income': row['Div Income'],
                    'total_return': row['Total Ret ($)'],
                    'total_return_pct': float(row['Total Ret (%)'].rstrip('%')),
                    'yield_on_cost': float(row['Yield on Cost'].rstrip('%')),
                    'cagr': float(row['CAGR'].rstrip('%')),
                    'beta': row['Beta']
                })

            # Calculate summary metrics
            total_cost = metrics_df['Cost Basis'].sum()
            total_value = metrics_df['Mkt Value'].sum()
            unrealized_pl = metrics_df['Unrealized P&L'].sum()
            unrealized_pl_pct = (unrealized_pl / total_cost * 100) if total_cost > 0 else 0
            dividend_income = metrics_df['Div Income'].sum()
            total_return = unrealized_pl + dividend_income
            total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0

            snapshot = {
                'timestamp': timestamp,
                'date': date,
                'summary': {
                    'total_value': total_value,
                    'total_cost': total_cost,
                    'unrealized_pl': unrealized_pl,
                    'unrealized_pl_pct': unrealized_pl_pct,
                    'dividend_income': dividend_income,
                    'total_return': total_return,
                    'total_return_pct': total_return_pct,
                    'position_count': len(positions)
                },
                'positions': positions
            }

            logging.info(f"Created snapshot for {date} with {len(positions)} positions")
            return snapshot

        except Exception as e:
            logging.error(f"Error creating snapshot: {e}")
            return None

    def get_last_snapshot(self):
        """
        Retrieve the most recent snapshot from Sheets.

        Returns:
            dict: Previous snapshot data, or None if no snapshots exist
        """
        try:
            # Read all snapshots (we'll get the last row)
            values = self.drive_client.get_sheet_values(self.spreadsheet_id, 'snapshots!A:K')

            if not values or len(values) <= 1:
                # No snapshots (only header row or empty)
                logging.info("No previous snapshots found")
                return None

            # Get last row (most recent snapshot)
            last_row = values[-1]

            # Parse the snapshot
            snapshot = {
                'timestamp': last_row[0],
                'date': last_row[1],
                'summary': {
                    'total_value': float(last_row[2]),
                    'total_cost': float(last_row[3]),
                    'unrealized_pl': float(last_row[4]),
                    'unrealized_pl_pct': float(last_row[5]),
                    'dividend_income': float(last_row[6]),
                    'total_return': float(last_row[7]),
                    'total_return_pct': float(last_row[8]),
                    'position_count': int(last_row[9])
                },
                'positions': json.loads(last_row[10]) if len(last_row) > 10 else []
            }

            logging.info(f"Retrieved snapshot from {snapshot['date']}")
            return snapshot

        except Exception as e:
            logging.error(f"Error getting last snapshot: {e}")
            return None

    def save_snapshot(self, snapshot):
        """
        Save snapshot to 'snapshots' sheet.

        Args:
            snapshot: Snapshot dict from create_snapshot()

        Returns:
            bool: Success status
        """
        try:
            # Prepare row data
            row = [
                snapshot['timestamp'],
                snapshot['date'],
                snapshot['summary']['total_value'],
                snapshot['summary']['total_cost'],
                snapshot['summary']['unrealized_pl'],
                snapshot['summary']['unrealized_pl_pct'],
                snapshot['summary']['dividend_income'],
                snapshot['summary']['total_return'],
                snapshot['summary']['total_return_pct'],
                snapshot['summary']['position_count'],
                json.dumps(snapshot['positions'])  # Store positions as JSON string
            ]

            # Append to sheet
            success = self.drive_client.append_sheet_row(self.spreadsheet_id, 'snapshots!A:K', row)

            if success:
                logging.info(f"Saved snapshot for {snapshot['date']}")
            return success

        except Exception as e:
            logging.error(f"Error saving snapshot: {e}")
            return False

    def calculate_daily_changes(self, current_snapshot, previous_snapshot):
        """
        Calculate day-over-day changes between two snapshots.

        Args:
            current_snapshot: Today's snapshot
            previous_snapshot: Previous day's snapshot (or None)

        Returns:
            dict: Daily changes with deltas and analytics
        """
        try:
            if not previous_snapshot:
                # First run - no previous data
                return {
                    'is_first_run': True,
                    'date': current_snapshot['date'],
                    'prev_date': None,
                    'value_change': 0,
                    'value_change_pct': 0,
                    'pl_change': 0,
                    'div_change': 0,
                    'return_change': 0,
                    'top_gainers': [],
                    'top_losers': [],
                    'days_between': 0,
                    'message': "First snapshot - no comparison available"
                }

            curr = current_snapshot['summary']
            prev = previous_snapshot['summary']

            # Portfolio-level changes
            value_change = curr['total_value'] - prev['total_value']
            value_change_pct = (value_change / prev['total_value'] * 100) if prev['total_value'] > 0 else 0
            pl_change = curr['unrealized_pl'] - prev['unrealized_pl']
            div_change = curr['dividend_income'] - prev['dividend_income']
            return_change = curr['total_return'] - prev['total_return']

            # Calculate days between snapshots
            curr_date = datetime.fromisoformat(current_snapshot['timestamp'])
            prev_date = datetime.fromisoformat(previous_snapshot['timestamp'])
            days_between = (curr_date - prev_date).days

            # Position-level analysis
            curr_positions = {p['ticker']: p for p in current_snapshot['positions']}
            prev_positions = {p['ticker']: p for p in previous_snapshot['positions']}

            position_changes = []
            for ticker in curr_positions:
                curr_pos = curr_positions[ticker]
                prev_pos = prev_positions.get(ticker)

                if prev_pos:
                    # Calculate change for existing position
                    price_change = curr_pos['current_price'] - prev_pos['current_price']
                    price_change_pct = (price_change / prev_pos['current_price'] * 100) if prev_pos['current_price'] > 0 else 0
                    value_change_pos = curr_pos['market_value'] - prev_pos['market_value']

                    position_changes.append({
                        'ticker': ticker,
                        'price_change': price_change,
                        'price_change_pct': price_change_pct,
                        'value_change': value_change_pos,
                        'is_new': False
                    })
                else:
                    # New position added
                    position_changes.append({
                        'ticker': ticker,
                        'price_change': curr_pos['current_price'],
                        'price_change_pct': 100.0,
                        'value_change': curr_pos['market_value'],
                        'is_new': True
                    })

            # Check for removed positions
            for ticker in prev_positions:
                if ticker not in curr_positions:
                    position_changes.append({
                        'ticker': ticker,
                        'price_change': -prev_positions[ticker]['current_price'],
                        'price_change_pct': -100.0,
                        'value_change': -prev_positions[ticker]['market_value'],
                        'is_sold': True
                    })

            # Find top movers
            position_changes.sort(key=lambda x: x['price_change_pct'], reverse=True)
            top_gainers = position_changes[:3]
            top_losers = position_changes[-3:][::-1]

            return {
                'is_first_run': False,
                'date': current_snapshot['date'],
                'prev_date': previous_snapshot['date'],
                'value_change': value_change,
                'value_change_pct': value_change_pct,
                'pl_change': pl_change,
                'div_change': div_change,
                'return_change': return_change,
                'top_gainers': top_gainers,
                'top_losers': top_losers,
                'days_between': days_between
            }

        except Exception as e:
            logging.error(f"Error calculating daily changes: {e}")
            return None

    def save_daily_changes(self, daily_changes):
        """
        Save daily changes to 'daily_changes' sheet.

        Args:
            daily_changes: Dict from calculate_daily_changes()

        Returns:
            bool: Success status
        """
        try:
            if daily_changes['is_first_run']:
                # Don't save first run to daily_changes
                logging.info("Skipping daily_changes save for first run")
                return True

            # Prepare row data
            row = [
                daily_changes['date'],
                daily_changes['prev_date'],
                daily_changes['value_change'],
                daily_changes['value_change_pct'],
                daily_changes['pl_change'],
                daily_changes['div_change'],
                daily_changes['return_change'],
                json.dumps(daily_changes['top_gainers']),
                json.dumps(daily_changes['top_losers']),
                f"Days between: {daily_changes['days_between']}"
            ]

            # Append to sheet
            success = self.drive_client.append_sheet_row(self.spreadsheet_id, 'daily_changes!A:J', row)

            if success:
                logging.info(f"Saved daily changes for {daily_changes['date']}")
            return success

        except Exception as e:
            logging.error(f"Error saving daily changes: {e}")
            return False

    def generate_trend_chart(self, filename="portfolio_trends.png", days=90):
        """
        Generate historical trend chart from snapshots.

        Args:
            filename: Path to save chart
            days: Number of days to include (default 90)

        Returns:
            bool: Success status
        """
        try:
            # Read all snapshots
            values = self.drive_client.get_sheet_values(self.spreadsheet_id, 'snapshots!A:K')

            if not values or len(values) <= 1:
                logging.warning("Not enough data for trend chart")
                return False

            # Parse snapshots (skip header)
            dates = []
            values_list = []
            cost_basis_list = []

            for row in values[1:]:  # Skip header
                try:
                    date = datetime.strptime(row[1], '%Y-%m-%d')
                    total_value = float(row[2])
                    total_cost = float(row[3])

                    dates.append(date)
                    values_list.append(total_value)
                    cost_basis_list.append(total_cost)
                except Exception as e:
                    logging.warning(f"Skipping row due to parse error: {e}")
                    continue

            if not dates:
                logging.warning("No valid data points for trend chart")
                return False

            # Filter to last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_data = [(d, v, c) for d, v, c in zip(dates, values_list, cost_basis_list) if d >= cutoff_date]

            if not filtered_data:
                # Not enough historical data, use all available
                filtered_data = list(zip(dates, values_list, cost_basis_list))

            dates, values_list, cost_basis_list = zip(*filtered_data)

            # Create chart
            plt.figure(figsize=(14, 7))

            plt.plot(dates, values_list, label='Portfolio Value', linewidth=2, color='#2E86C1', marker='o', markersize=4)
            plt.plot(dates, cost_basis_list, label='Cost Basis', linewidth=2, color='#E74C3C', linestyle='--')

            plt.title(f'Portfolio Performance - Last {days} Days', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Value ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()

            plt.savefig(filename, dpi=150)
            plt.close()

            logging.info(f"Generated trend chart: {filename}")
            return True

        except Exception as e:
            logging.error(f"Error generating trend chart: {e}")
            return False
