"""Bot loggers"""

import logging
import os
import sys

# reading setings
import tomllib

from datetime import datetime
from logging import FileHandler, Formatter
from pathlib import Path
from typing import Optional

# bot settings
from bot.settings import bot_settings

# current timestamp & app directory
DATE_RUN = datetime.now()
WORK_DIR = Path(os.getcwd())


# get config
with bot_settings.log_settings_file.open("rb") as log_settings:
    LOG_SETTINGS = tomllib.load(log_settings)


# set basic config to logger
logging.basicConfig(
    format=LOG_SETTINGS["log"]["form"],
    level=LOG_SETTINGS["log"]["level"],
)

# get root logger
root_log = logging.getLogger()


def get_file_handler() -> Optional[FileHandler]:
    """Create file handler"""
    file_log = LOG_SETTINGS["log"]["file"]
    if file_log["enable"]:
        root_log.info("Logging to file enabled.")
        log_dir = WORK_DIR / file_log["path"]
        if not log_dir.is_dir():
            root_log.warning("Log directory doesn't exist.")
            try:
                root_log.info("Creating log directory...")
                log_dir.mkdir()
                root_log.info("Created log directory: %r.", log_dir.resolve())
            except IOError as ex:
                root_log.error("Exception occured: %s.", ex)
                root_log.info("Can't execute program.")
                sys.exit()
        log_date = DATE_RUN.strftime(file_log["date"])
        log_name = f"{file_log['pref']}{log_date}.log"
        log_file = log_dir / log_name
        root_log.info("Logging to file: %r.", log_name)
        # create file handler
        file_handler = FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(Formatter(file_log["form"]))
        file_handler.setLevel(file_log["level"])
        return file_handler
    root_log.info("Logging to file disabled.")
    return


def setup_logging():
    if FILE_HANDLER := get_file_handler():
        root_log.addHandler(FILE_HANDLER)
