"""Reusable Playwright/pytest test framework.

Public surface:

    from qa_framework import settings, logger, ApiClient, ApiResponse
"""

from qa_framework.api_client import ApiClient, ApiResponse
from qa_framework.logger import logger
from qa_framework.settings import Settings, settings

__all__ = ["Settings", "settings", "logger", "ApiClient", "ApiResponse"]
__version__ = "0.1.0"
