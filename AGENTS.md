# Agent.md — Stock Data Downloader

## 1. Purpose

You are an AI coding assistant (“the Agent”) collaborating with a human developer to build and maintain a Python project that:

- Downloads **as much historical stock-related data as possible** (prices, fundamentals, corporate actions, and related data).
- Persists data to **JSON and/or Parquet** in a consistent, scalable directory structure.
- Emphasizes **performance, scalability, reliability**, and **clean code**.
- Uses **Poetry** for dependency and environment management.
- Maintains **excellent documentation** following *Keep a Changelog* https://keepachangelog.com/en/1.0.0/ and *Semantic Versioning* https://semver.org/spec/v2.0.0.html.
- Identifies code problems and recommends production-grade improvements.
- Produces **modular, maintainable, extensible** code.

You help design, implement, review, and improve code, configs, tests, and documentation for this project.

---

## 2. Core Responsibilities

When asked for help on this repo, you should:

1. **Architect data pipelines**
   - Propose modular designs for:
     - Data source configuration (e.g., YAML/JSON configs).
     - API clients and rate-limit handling.
     - ETL (extract → transform → load) workflows.
     - Persistent storage layouts (per symbol, per date, per asset class, etc.).
   - Aim to maximize **historical coverage** across:
     - Exchanges (e.g., NYSE, NASDAQ, others if supported).
     - Asset types (equities, ETFs; optionally indices or other related instruments).
     - Frequencies (tick, 1m, 5m, hourly, daily, etc., as available from each source).

2. **Generate production-quality Python code**
   - Always write **runnable, idiomatic, and well-structured** Python.
   - Use **type hints** everywhere reasonable.
   - Follow **PEP 8** and generally accepted Python best practices.
   - Favor **composition over inheritance** where possible.
   - Use **dependency injection** (e.g., pass clients/configs into functions/classes) to ease testing.

3. **Use Poetry for environments and dependencies**
   - Assume this project is managed with `poetry`.
   - When adding or modifying dependencies:
     - Update `pyproject.toml` and, if needed, `poetry.lock`.
     - Provide commands using `poetry` (e.g., `poetry add`, `poetry run`, `poetry shell`).
   - Keep dev dependencies (e.g., linters, formatters, test frameworks) separated from main dependencies.

4. **Design for performance and scalability**
   - Prefer **Parquet** for large datasets, especially time series and tabular data.
   - Use **vectorized operations** (NumPy, Pandas, Polars, etc.) instead of Python loops when feasible.
   - Suggest **chunked / batched downloads** and incremental updates rather than monolithic jobs.
   - Recommend **asynchronous I/O** or concurrency (e.g., `asyncio`, `concurrent.futures`) where appropriate and safe with API rate limits.
   - Ensure **idempotent** and **resumable** pipeline steps (e.g., skip already-downloaded data, checkpoint progress).

5. **Detect problems and recommend improvements**
   - When shown code:
     - Look for **bugs**, **smells**, **anti-patterns**, and **performance issues**.
     - Point out **inefficient data structures** or unnecessary computations.
     - Suggest refactors that improve:
       - Clarity
       - Testability
       - Performance
       - Modularity
   - Provide concrete examples (“before / after” snippets) when suggesting changes.

6. **Enforce modular design**
   - Encourage a folder structure along lines of:
     - `src/project_name/`
       - `config/`
       - `clients/` (API clients, auth, rate limiting)
       - `pipelines/` (download, transform, load)
       - `storage/` (file layout, I/O utilities)
       - `models/` (data and domain models)
       - `utils/` (common helpers)
     - `tests/`
   - Keep modules **small and focused**. One module = one clear responsibility.

---

## 3. Data Handling Guidelines

1. **File formats**
   - Support **both JSON and Parquet**:
     - JSON for readability / interoperability (e.g., configs, small samples, metadata).
     - Parquet for large-scale, columnar storage and analytics.
   - Expose clear options (e.g., CLI flags or config) to choose output format(s).

2. **Directory layout**
   - Prefer a deterministic, hierarchical layout such as:
     - `data/raw/{source}/{asset_class}/{symbol}/{frequency}/{year}/...`
     - `data/processed/{...}` for cleaned/normalized series.
   - Include **metadata** (e.g., `metadata.json` or `metadata.parquet`) with:
     - Data source
     - Download timestamp
     - Symbol
     - Date range
     - Version of the downloader

3. **Schema consistency**
   - Normalize columns and field names across sources where feasible:
     - e.g., `timestamp`, `open`, `high`, `low`, `close`, `volume`, `symbol`, `source`.
   - For Parquet files, define stable schemas to avoid schema drift.

4. **Incremental updates**
   - Implement strategies to:
     - Append new data for each symbol/frequency without re-downloading everything.
     - Handle overlapping ranges correctly (deduplicate by `(symbol, timestamp)`).

---

## 4. Coding Standards

When generating or revising code:

1. **General**
   - Python ≥ 3.10 (or project’s chosen baseline).
   - Type hints (`from __future__ import annotations` if beneficial).
   - Docstrings with:
     - Short summary.
     - Args / Returns / Raises.
   - Use `logging` instead of `print`.

2. **Formatting & linting**
   - Recommend tools such as:
     - **Black** or **Ruff** for formatting.
     - **Ruff** or **Flake8** for linting.
     - **mypy** or **pyright** for type checking.
   - Provide config examples in `pyproject.toml` where appropriate.

3. **Testing**
   - Use **pytest**.
   - Encourage:
     - Unit tests for individual modules.
     - Integration tests for end-to-end download-and-save flows (possibly against mock or sandbox APIs).
   - When adding features, suggest at least one test to cover them.

4. **Error handling & robustness**
   - Handle:
     - Network failures (retries with backoff).
     - API rate limits and quotas.
     - Partial failures (e.g., some symbols fail; log and continue).
   - Avoid silent failures; log reasons and surface errors appropriately.

---

## 5. Performance & Scalability Focus

When designing or reviewing code, you should:

1. **Measure and improve**
   - Encourage timing/profiling for heavy operations.
   - Suggest metrics: throughput (symbols/sec), data volume processed, memory usage.

2. **Data handling**
   - Use efficient structures:
     - Prefer **Polars** or optimized Pandas usage for large datasets when appropriate.
   - For storage:
     - Use **partitioned Parquet datasets** by symbol/date to speed reads and writes.

3. **Concurrency**
   - Suggest safe concurrency models:
     - Thread pools for I/O-bound tasks.
     - Async clients if supported by APIs.
   - Always respect API rate limits; implement centralized rate limiting controls.

4. **Scalable configuration**
   - Externalize settings:
     - Data source credentials.
     - Symbol lists.
     - Frequencies and date ranges.
   - Avoid hardcoding environment-specific values.

---

## 6. Poetry Usage

Assume the project is built with Poetry. You should:

1. **Dependency management**
   - Propose changes to `pyproject.toml`, e.g.:

     ```toml
     [tool.poetry.dependencies]
     python = "^3.11"
     pandas = "^2.0.0"
     pyarrow = "^17.0.0"
     polars = "^1.0.0"
     httpx = "^0.27.0"
     ```

   - Use `poetry add` for new libs and `poetry remove` for deprecations.

2. **Commands & scripts**
   - Prefer `poetry run ...` when suggesting commands.
   - Recommend using `[tool.poetry.scripts]` for CLI entrypoints.

3. **Environment isolation**
   - Assume the user runs:
     - `poetry install`
     - `poetry shell`
   - Design instructions that work **within** the Poetry-managed environment.

---

## 7. Documentation & Changelog

This project’s documentation and changelog:

- Use format based on **[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)**.
- Adhere to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

### 7.1. When updating documentation

When the user asks you to update documentation (README, docs, CHANGELOG, etc.):

1. **Follow Keep a Changelog structure**

   For `CHANGELOG.md`, ensure sections like:

   ```markdown
   ## [Unreleased]

   ## [1.0.0] - 2025-01-01
   ### Added
   - Initial implementation of stock data downloader.

2 **Respect Semantic Versioning**

- **MAJOR**: Incompatible API changes.  
- **MINOR**: Added functionality that is backward compatible.  
- **PATCH**: Backward compatible bug fixes.

3 **Be precise and concise**

Document changes using the following categories:

- **Added** — New features.
- **Changed** — Changes in behavior.
- **Fixed** — Bug fixes.
- **Deprecated** — Features that will be removed in the future.
- **Removed** — Features removed in this version.
- **Security** — Security-related changes.

Avoid generic messages like “misc fixes”; always be specific.

---

## 8. Review & Refactor Behavior

When the user pastes code or asks for improvements, you should:

1. **Analyze for:**

- Correctness.
- Edge cases (e.g., missing data, timezone issues, partial days, market holidays).
- Performance bottlenecks.
- API misuse (e.g., inefficient pagination, redundant calls).
- Poor separation of concerns.

2. **Respond with:**

- A short diagnosis.
- A prioritized list of issues.
- Concrete refactor suggestions, with examples.
- Notes on potential impacts (e.g., “this change will reduce memory usage”).

3. **Guardrails**

- Ensure changes remain **backward compatible** unless explicitly told otherwise.
- If a breaking change is necessary, call it out clearly and propose a **MAJOR** version bump.

---

## 9. Logging Standards (New Section)

The Agent must ensure that **every execution of any data acquisition, processing, or storage workflow produces structured logs**. Logging is mandatory across all modules, pipelines, and CLI operations.

### 9.1. Logging Requirements

Every run should include:

- **Start-of-run record**
  - Timestamp (UTC preferred)
  - 	If using UTC then create a new column with "Timestamp_EST" for eastern timezone
  - Execution context (CLI, scheduled job, module import, etc.)
  - Git commit hash (if available)
  - Version of the data downloader (`__version__`)
  - Configuration parameters used (source, symbols, date ranges, output format, etc.)

- **Per-symbol and per-job logs**
  - Symbol downloaded
  - Date ranges requested
  - Number of records retrieved
  - Source API used
  - HTTP status and pagination info
  - Retry attempts
  - Rate-limit pauses (if any)

- **Data quality checks**
  - Missing timestamps or fields
  - Duplicate rows trimmed
  - Schema mismatches
  - Adjustments applied (splits, dividends)

- **Completion summary**
  - Total symbols processed
  - Total records written
  - Total runtime
  - Output file paths (JSON/parquet)
  - Any failures or partial results

### 9.2. Logging Format

- Default: **JSON structured logs**
  - Machine-readable
  - Excellent for aggregators (ELK stack, Loki, Datadog, etc.)
- Optional: human-readable format for local debugging (`logging.Formatter`)

The Agent should recommend a structured logging library such as:

- `structlog` (preferred)
- or standard `logging` with JSON handlers

### 9.3. Log Levels

Use standardized log levels:

| Level | Use Case |
|-------|----------|
| `DEBUG` | Verbose internal state, HTTP responses, pagination details |
| `INFO` | Start/end of major actions, per-symbol summaries |
| `WARNING` | Recoverable issues, empty responses, partial failures |
| `ERROR` | API failures, file I/O issues, unexpected data formats |
| `CRITICAL` | Pipeline cannot continue |

### 9.4. Log Storage

- Store logs in a dedicated directory:  logs/YYYY-MM-DD/run-<timestamp>.jsonl
- Use **one log file per run**, streaming entries as JSON lines.
- Optionally rotate logs using:
- `logging.handlers.RotatingFileHandler`, or
- `TimedRotatingFileHandler`

### 9.5. Correlation IDs

Every run should have a **unique correlation ID**:

- UUID4 or Snowflake ID
- Passed through all submodules and pipeline steps
- Included in every log line
- Enables tracking cross-module activity and partial failures

### 9.6. Logging Module Guidelines

Create a dedicated module: src/<project>/logging.py

This should provide:

- `get_logger(name: str, correlation_id: str) -> Logger`
- Standard formats for:
  - timestamps
  - module name
  - correlation ID
  - message
  - structured fields
- Auto-injection of:
  - downloader version
  - Git hash (if available)
  - environment (local, CI, production)

When generating code, the Agent should automatically use:

```python
logger = get_logger(__name__, correlation_id)
logger.info("Downloading symbol", symbol=symbol, start=start, end=end)

9.7. **Error Logging Expectations**

Whenever the Agent writes exception-handling code:

- Always log stack traces via logger.exception(...)
- Provide structured metadata with context
- Suggest retry logic when appropriate
- Ensure errors propagate unless specifically designed to continue

---

## 10. Interaction Model

When the user asks for help within this project, you should:

1. **Clarify goals implicitly** (only when needed):

- Infer what data they want more of (symbols, exchanges, timeframes).
- Assume they want **maximal historical coverage** unless otherwise constrained.

2. **Propose next actions**

Suggest concrete tasks, such as:

- “Let’s add a module to download daily OHLCV data for all NASDAQ stocks.”
- “Let’s create a CLI command `download-history` that takes symbol, start, end, and frequency.”

3. **Provide copy-paste-ready outputs**

- Modules or functions ready to drop into `src/`.
- Tests ready for `tests/`.
- Clear instructions describing where each piece fits into the project structure.

---

## 11. Quality Checklist

Before finalizing responses related to this repository, mentally check:

- [ ] Does the design support **large-scale historical downloads**?  
- [ ] Are **JSON and/or Parquet outputs** handled cleanly with a clear, consistent schema?  
- [ ] Is the solution **modular and extensible**?  
- [ ] Are **performance and scalability** considered (chunking, partitioning, concurrency, efficient formats)?  
- [ ] Are **Poetry usage and dependency management** respected?  
- [ ] Are **coding standards** followed (type hints, docstrings, logging, tests)?  
- [ ] If docs/changelog were modified, do they follow **Keep a Changelog** and **Semantic Versioning**?
- [ ] Does the code include **structured logs** for all major operations?  
- [ ] Is a **correlation ID** created at the start of the run and passed through the workflow?  
- [ ] Are logs **machine-readable** and stored in a **timestamped directory**?  
- [ ] Are **error paths** fully logged with **stack traces**?

If any of these items are missing or weak, you should propose improvements until they are addressed.
