"""The pytest plugin: fixtures every consumer of this package gets for free.

Registered through the ``pytest11`` entry point in ``pyproject.toml``, so
installing the package is enough. Nothing has to be imported and no suite needs
its own copy of this boilerplate.

Fixtures defined here are plain plugin fixtures, so a project can still override
any of them from its own ``conftest.py`` — a conftest always wins over a plugin.
"""

import time

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.logger import logger
from qa_framework.server import serve_directory
from qa_framework.settings import settings


@pytest.fixture(scope="session", autouse=True)
def announce_settings():
    """Print the resolved configuration once, so a CI log is self-documenting."""
    logger.info("Test run starting: %s", settings.summary())
    yield
    logger.info("Test run finished.")


@pytest.fixture(scope="session")
def demo_app_server():
    """Serve the project's demo app for the whole session, on a free port.

    The directory comes from DEMO_APP_DIR (default: ./demo_app), so each repo
    keeps its own application while sharing the launch and teardown logic.
    """
    with serve_directory(settings.demo_app_dir) as base_url:
        yield base_url


@pytest.fixture(scope="session")
def base_url(demo_app_server):
    """UI target: UI_BASE_URL wins if set, else the bundled demo app."""
    if settings.ui_base_url_configured:
        return settings.ui_base_url
    return demo_app_server


@pytest.fixture(scope="session")
def api_client(playwright):
    """HTTP client with base URL and headers configured from settings."""
    client = ApiClient(playwright.request, settings.api_base_url)
    yield client
    client.close()


@pytest.fixture
def timed_api_call(api_client):
    """Wrap a call to record how long it took.

    Usage:
        response, elapsed_ms = timed_api_call(api_client.get_product, 1)

    This is how the performance checks get their measurement without every test
    having to remember to time itself.
    """

    def _call(method, *args, **kwargs):
        start = time.perf_counter()
        response = method(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s -> %s in %.0f ms",
            getattr(method, "__name__", "call"),
            response.status,
            elapsed_ms,
        )
        return response, elapsed_ms

    return _call


@pytest.fixture
def ui_page(page):
    """A page pointed at the UI under test, with the framework timeout applied.

    Reuses the built-in pytest-playwright ``page`` fixture rather than launching
    a browser here, so ``--headed`` and ``--browser`` keep working.
    """
    from playwright.sync_api import expect

    page.set_default_timeout(settings.default_timeout_ms)
    expect.set_options(timeout=settings.default_timeout_ms)
    return page
