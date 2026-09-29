# Playwright QA Test Framework — Python

A reusable test framework built with [Playwright](https://playwright.dev) and
[pytest](https://docs.pytest.org), covering both API and UI layers.

**24 tests, all passing, running in parallel in about 4 seconds.**

This is the "framework" repository: it shows how the pieces from a UI suite and
an API suite are combined into something a team can run, extend and rely on.

## What this repo demonstrates

| Capability | Where to look |
| --- | --- |
| Environment-driven configuration | `config/settings.py` |
| Reusable fixtures | `conftest.py` |
| Logging to console and file | `utils/logger.py` |
| API client layer | `clients/api_client.py` |
| Risk-based test tagging | `pytest.ini` markers |
| Parallel execution | `-n auto` via pytest-xdist |
| Flakiness control | `--reruns 1` via pytest-rerunfailures |
| HTML reporting | `--html` via pytest-html |
| Multi-browser / multi-OS CI | `.github/workflows/ci.yml` |
| Performance budgets | `tests/api/test_contracts_and_boundaries.py` |
| Deterministic test data | `demo_app/` served locally |

## Architecture

```
conftest.py
   |
   +-- base_url ........... UI target, overridden per environment
   +-- api_client ......... shared HTTP client, closed after the session
   +-- timed_api_call ..... measures latency for budget checks
   +-- ui_page ............ page with the framework timeout applied
   +-- announce_settings .. prints the resolved config into the CI log
   |
config/settings.py ......... environment variables -> one frozen settings object
utils/logger.py ............ console + file logging
clients/api_client.py ...... endpoint knowledge, kept out of the tests
tests/api/ ................. contract, negative and performance tests
tests/ui/ .................. browser capability and behaviour tests
demo_app/ .................. deterministic app served locally
```

## Running the tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

pytest                       # everything, in parallel
pytest -m smoke              # fast gate only
pytest -m "not smoke"        # everything except the gate
pytest --headed              # watch it run in a real browser
pytest --browser=firefox     # run against another engine
pytest -n 0                  # disable parallelism
```

Reports land in `reports/report.html`, logs in `logs/test-run.log`.

## Configuration

Every value comes from the environment, so the same tests run anywhere. Copy
`config/.env.example` and export what you need:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | `local` | Name of the target environment |
| `API_BASE_URL` | `https://dummyjson.com` | API under test |
| `UI_BASE_URL` | *(bundled demo app)* | UI under test |
| `HEADLESS` | `true` | Run the browser headless |
| `DEFAULT_TIMEOUT_MS` | `10000` | Assertion and action timeout |
| `API_BUDGET_MS` | `5000` | Latency budget per API call |

Example:

```bash
ENVIRONMENT=staging \
UI_BASE_URL=https://staging.example.com \
HEADLESS=false \
pytest -m smoke
```

When `UI_BASE_URL` is set, it wins. When it is not, the bundled demo app is
served on a free port, so a fresh clone runs with no setup at all.

## Risk-based test selection

Tests are tagged by the risk they cover, so you can run the slice you need:

```bash
pytest -m smoke         # is anything working at all?
pytest -m contract      # are the API guarantees intact?
pytest -m negative      # do bad inputs fail properly?
pytest -m performance   # are we still inside the latency budget?
```

`smoke` runs on every commit. The rest can run before a release.

## Why the UI tests target a local app

The first version of this suite pointed at `example.com`. It broke within the
same session: the page no longer had an `<h1>`, and the site now states
explicitly that it should not be relied on for automated testing.

An external target introduces failures that have nothing to do with the product.
So the framework serves its own small app on a random free port, and
`UI_BASE_URL` remains available for pointing at a real environment. This is a
deliberate reliability decision, and it is the kind of judgement a QA engineer
is expected to make.

## Notes

- `Settings` is a frozen dataclass, so a value cannot be changed by accident
  halfway through a run.
- Timeouts are set centrally. A slow network should not turn into a stream of
  false failures.
- `--reruns 1` absorbs genuine timing noise. It is deliberately kept at one;
  raising it hides real defects.
- Port selection is dynamic, so the suite cannot collide with another process.
