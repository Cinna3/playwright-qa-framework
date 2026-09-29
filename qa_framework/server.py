"""Static file server used to host a project's own test target.

The mechanism lives here rather than in each conftest so that a repo can ship
its application folder and inherit the launch, readiness check and teardown.
"""

import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from qa_framework.logger import logger


def free_port() -> int:
    """Ask the OS for an unused port instead of hardcoding one.

    A hardcoded port collides with whatever else is running on a developer
    machine or a CI runner, and the suite then fails for a reason that has
    nothing to do with the code under test.
    """
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


@contextmanager
def serve_directory(directory: Path):
    """Serve ``directory`` on a free port for the duration of the ``with`` block.

    Why host our own page instead of a public site? A public target can change
    or vanish without warning, and a suite that depends on one is a suite that
    fails for reasons unrelated to the product. example.com, for instance, now
    states it should not be used for automated testing.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"demo app directory not found: {directory.resolve()}")

    port = free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(directory),
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
        raise RuntimeError(f"{directory.name} server failed to start")

    logger.info("%s served at http://localhost:%s", directory.name, port)
    try:
        yield f"http://localhost:{port}"
    finally:
        process.terminate()
        process.wait(timeout=5)
