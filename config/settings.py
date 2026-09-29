"""Environment-driven configuration.

Why a settings module instead of hardcoded values in tests? Because a framework
has to be usable against more than one environment. A test run should not need
editing when the target changes; it should read BASE_URL from the environment
and work the same way locally, in CI, and against staging.
"""

import os
from dataclasses import dataclass, field


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean from the environment.

    Anything other than the literal strings below counts as False, which keeps
    an unset or misspelled variable from silently enabling something.
    """
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Immutable settings object, created once and shared by every test."""

    api_base_url: str = os.getenv("API_BASE_URL", "https://dummyjson.com")
    ui_base_url: str = os.getenv("UI_BASE_URL", "https://example.com")
    environment: str = os.getenv("ENVIRONMENT", "local")
    headless: bool = _env_flag("HEADLESS", True)
    # A slow network makes a 5s default assertion timeout look like a product
    # bug. In CI the allowance is widened, but the default stays tight.
    default_timeout_ms: int = int(os.getenv("DEFAULT_TIMEOUT_MS", "10000"))
    # A soft performance budget per API call, used by the performance checks.
    api_budget_ms: int = int(os.getenv("API_BUDGET_MS", "5000"))
    # Never fail a CI run for a test that is already a documented defect.
    fail_on_xfail: bool = _env_flag("FAIL_ON_XFAIL", False)
    tags: list = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"env={self.environment} api={self.api_base_url} "
            f"ui={self.ui_base_url} headless={self.headless} "
            f"timeout={self.default_timeout_ms}ms budget={self.api_budget_ms}ms"
        )


settings = Settings()
