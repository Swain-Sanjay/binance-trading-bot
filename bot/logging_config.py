from __future__ import annotations

import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = PROJECT_ROOT / "bot.log"

_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure application logging once and return the project logger."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    existing_handler_names = {handler.get_name() for handler in root_logger.handlers}
    formatter = logging.Formatter(_FORMAT)

    if "trading_bot_file" not in existing_handler_names:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.set_name("trading_bot_file")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if "trading_bot_console" not in existing_handler_names:
        console_handler = logging.StreamHandler()
        console_handler.set_name("trading_bot_console")
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    return logging.getLogger("trading_bot")

