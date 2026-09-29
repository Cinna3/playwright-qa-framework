"""Test logging.

A test run that only prints PASS/FAIL is hard to debug later. This writes a
readable log per run so you can answer "what did the suite actually do, and
how long did each call take?" after the fact.
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")


def setup_logging(level=logging.INFO) -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("qa")
    logger.setLevel(level)
    logger.handlers.clear()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
    logger.addHandler(console)

    file_handler = logging.FileHandler(LOG_DIR / "test-run.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    )
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
