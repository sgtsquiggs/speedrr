import datetime
import logging
import pathlib
import sys
import traceback
from types import TracebackType

# ANSI SGR foreground colours. These were previously sourced via colorama's
# Fore constants, but colorama.init() was never called -- on Linux, the only
# runtime this ships to, it supplied these five literals and nothing else.
GREY = "\x1b[90m"
YELLOW = "\x1b[33m"
LIGHT_RED = "\x1b[91m"
RED = "\x1b[31m"
RESET = "\x1b[39m"

logger_name = "speedrr"
default_stdout_log_level = logging.INFO
file_log_name = f"{datetime.datetime.now():%Y-%m-%d %H.%M.%S}.log"
log_format = "[%(asctime)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"


class ColourFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: GREY + log_format + RESET,
        logging.INFO: log_format + RESET,
        logging.WARNING: YELLOW + log_format + RESET,
        logging.ERROR: LIGHT_RED + log_format + RESET,
        logging.CRITICAL: RED + log_format + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(default_stdout_log_level)
stdout_handler.setFormatter(ColourFormatter())
logger.addHandler(stdout_handler)


def set_file_handler(folder: str, level: int) -> None:
    path = pathlib.Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(str(pathlib.Path(folder, file_log_name)), encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(
        "Uncaught exception: "
        + " ".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )


sys.excepthook = handle_exception
