"""Framework-level fixtures.

Almost everything this suite needs arrives from the installed ``qa_framework``
pytest plugin (see the ``pytest11`` entry point in ``pyproject.toml``), so there
is nothing to repeat here.

The one fixture defined below is deliberate. ``base_url`` is claimed by both
pytest-base-url and pytest-playwright, and which plugin wins is decided by
registration order. A conftest always wins over plugins, so the mapping from
``base_url`` to the framework's UI target is pinned here and cannot drift.
"""

import pytest


@pytest.fixture(scope="session")
def base_url(ui_base_url):
    """Point pytest-playwright's ``base_url`` at the framework's UI target."""
    return ui_base_url
