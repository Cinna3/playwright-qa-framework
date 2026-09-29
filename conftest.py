"""Framework-level fixtures.

Empty by design. Every fixture this suite needs arrives from the installed
``qa_framework`` pytest plugin (see the ``pytest11`` entry point in
``pyproject.toml``), so there is nothing to repeat here.

A project can still override any fixture by defining it below — a conftest
always wins over a plugin.
"""
