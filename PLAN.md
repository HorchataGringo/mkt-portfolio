\# Development Plan for EigenLedger



\## Phase 1: Environment Setup \& Initialization

\*Objective: Establish a reproducible local development environment.\*



2\.  \*\*Create a Virtual Environment\*\*

&nbsp;   \* Create a clean isolated environment to avoid dependency conflicts with poetry package for python.



3\.  \*\*Install Dependencies\*\*

&nbsp;   \* Install the package in "editable" mode so changes are reflected immediately.

&nbsp;   \* \*Note: This utilizes `pyproject.toml` to identify required packages (QuantStats, PyPortfolioOpt, etc.).\*

&nbsp;   ```bash

&nbsp;   pip install -e .

&nbsp;   ```

&nbsp;   \* \*Optional: Install dev tools (if not already present)\*

&nbsp;   ```bash

&nbsp;   pip install pytest black flake8

&nbsp;   ```



\## Phase 2: Verification \& Exploration

\*Objective: Confirm the current codebase works as expected before making changes.\*



1\.  \*\*Run the Quickstart Script\*\*

&nbsp;   \* Create a file named `test\_run.py` with the following content to verify the core `Engine` works:

&nbsp;   ```python

&nbsp;   from EigenLedger import portfolio\_analysis, Engine

&nbsp;   

&nbsp;   # Simple portfolio test

&nbsp;   portfolio = Engine(

&nbsp;       start\_date="2020-01-01",

&nbsp;       portfolio=\["AAPL", "GOOG"],

&nbsp;       weights=\[0.5, 0.5],

&nbsp;       benchmark=\["SPY"]

&nbsp;   )

&nbsp;   portfolio\_analysis(portfolio)

&nbsp;   ```

&nbsp;   \* Run it: `python test\_run.py`



2\.  \*\*Explore the Source (`EigenLedger/`)\*\*

&nbsp;   \* Locate the bundled `empyrical` module (recently added to fix dependency issues).

&nbsp;   \* Review `portfolio\_analysis` function to understand how it wraps `QuantStats`.



\## Phase 3: Infrastructure \& Quality Assurance

\*Objective: Add missing safety nets (tests) to allow for confident refactoring.\*



1\.  \*\*Initialize Test Suite\*\*

&nbsp;   \* The repository currently lacks a visible top-level `tests/` directory.

&nbsp;   \* \*\*Action:\*\* Create a `tests/` directory at the root.

&nbsp;   \* \*\*Action:\*\* Create `tests/test\_engine.py`.

&nbsp;   \* \*\*Action:\*\* Write a simple unit test that mocks `yfinance` data (to avoid API calls during testing) and asserts that `Engine` initializes correctly.



2\.  \*\*Linting \& Formatting\*\*

&nbsp;   \* Standardize the code style.

&nbsp;   \* \*\*Action:\*\* Run `black .` to format code.

&nbsp;   \* \*\*Action:\*\* Run `flake8 EigenLedger` to find potential bugs or unused imports.



3\.  \*\*CI/CD Setup (GitHub Actions)\*\*

&nbsp;   \* \*\*Action:\*\* Create `.github/workflows/test.yml`.

&nbsp;   \* \*\*Content:\*\* A workflow that runs on `push` to `main`, installs dependencies, and runs `pytest`.



\## Phase 4: Feature Development \& Refactoring

\*Objective: Implement new features and clean up technical debt.\*



1\.  \*\*Refactor Bundled Dependencies\*\*

&nbsp;   \* Review the bundled `empyrical` code. If it is a direct copy, verify license headers and check if it can be modernized or stripped down to only what is needed.



2\.  \*\*Feature: Custom Data Support\*\*

&nbsp;   \* \*Current limitation:\* The engine relies heavily on `yfinance` tickers.

&nbsp;   \* \*\*Task:\*\* Allow the `Engine` to accept a local Pandas DataFrame of prices instead of just a list of ticker strings.

&nbsp;   \* \*\*Implementation:\*\* Modify `Engine.\_\_init\_\_` to check if `portfolio` input is a DataFrame.



3\.  \*\*Feature: Enhanced Reporting\*\*

&nbsp;   \* \*\*Task:\*\* Add an option to export the analysis results to a PDF or HTML report (leveraging `QuantStats` reporting features if not fully exposed).



\## Phase 5: Documentation \& Release

\*Objective: Make the project accessible to new users.\*



1\.  \*\*Update `README.md`\*\*

&nbsp;   \* Add a "Development" section explaining how to run tests.

&nbsp;   \* Document any new features (e.g., Custom Data Support).



2\.  \*\*Version Bump\*\*

&nbsp;   \* Update `version` in `pyproject.toml` (or `setup.py` if applicable) following Semantic Versioning.

