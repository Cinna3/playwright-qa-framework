"""Framework-level fixtures.

This is the heart of the framework: shared setup, teardown, and reporting that
every test can rely on without repeating itself.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import expect

from clients.api_client import ApiClient
from config.settings import settings
from utils.logger import logger

DEMO_APP_DIR = Path(__file__).parent / "demo_app"


def _free_port() -> int:
    """Ask the OS for an unused port instead of hardcoding one.

    A hardcoded port collides with whatever else is running on a developer
    machine or a CI runner, and the suite then fails for a reason that has
    nothing to do with the code under test.
    """
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def demo_app_server():
    """Serve the bundled demo app for the duration of the test session.

    Why host our own page instead of a public site? A public target can change
    or vanish without warning, and a suite that depends on one is a suite that
    fails for reasons unrelated to the product. example.com, for instance, now
    states it should not be used for automated testing.
    """
    port = _free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(DEMO_APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(50):
        try:
            with socket.create_connection(("localhost", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    else:
        process.terminate()
        raise RuntimeError("Demo app server failed to start")

    logger.info("Demo app served at http://localhost:%s", port)
    yield f"http://localhost:{port}"

    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="session", autouse=True)
def announce_settings():
    """Print the resolved configuration once, so a CI log is self-documenting."""
    logger.info("Test run starting: %s", settings.summary())
    yield
    logger.info("Test run finished.")


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


@pytest.fixture(scope="session")
def base_url(demo_app_server):
    """Supply the UI base URL.

    If UI_BASE_URL is set in the environment, that wins, so the same tests can
    be pointed at a deployed environment. Otherwise the bundled demo app is
    used, which keeps a fresh clone runnable with no extra setup.
    """
    import os

    if os.getenv("UI_BASE_URL"):
        return settings.ui_base_url
    return demo_app_server


@pytest.fixture
def ui_page(page):
    """A page pointed at the UI under test, with the framework timeout applied.

    Note: the built-in pytest-playwright `page` fixture is reused rather than a
    browser being launched here. Re-implementing it would mean losing the
    --headed and --browser command line options for no benefit.
    """
    page.set_default_timeout(settings.default_timeout_ms)
    expect.set_options(timeout=settings.default_timeout_ms)
    return page
