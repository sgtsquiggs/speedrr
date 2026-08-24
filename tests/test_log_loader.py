import logging

import pytest

from helpers.log_loader import ColourFormatter

RESET = "\x1b[39m"


def make_record(level: int) -> logging.LogRecord:
    return logging.LogRecord(
        name="speedrr",
        level=level,
        pathname="/home/main.py",
        lineno=42,
        msg="hello",
        args=(),
        exc_info=None,
    )


@pytest.mark.parametrize(
    "level,prefix",
    [
        (logging.DEBUG, "\x1b[90m"),
        (logging.INFO, ""),
        (logging.WARNING, "\x1b[33m"),
        (logging.ERROR, "\x1b[91m"),
        (logging.CRITICAL, "\x1b[31m"),
    ],
)
def test_each_level_gets_its_ansi_colour(level, prefix):
    """Pins the level-to-escape mapping.

    These escapes came from colorama's Fore constants. The dependency was
    dropped in favour of the literals, so this test is what guarantees the
    swap was equivalent -- and what would catch a future edit to them.
    """
    output = ColourFormatter().format(make_record(level))

    assert output.startswith(prefix + "[")
    assert output.endswith(RESET)
    assert "hello" in output
    assert "(main.py:42)" in output


def test_unknown_level_falls_back_to_plain_format():
    # FORMATS.get() returns None for an unmapped level, and logging.Formatter
    # then uses its own default -- no colour, no crash.
    output = ColourFormatter().format(make_record(logging.NOTSET))

    assert "hello" in output
    assert "\x1b[" not in output
