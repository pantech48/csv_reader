import logging
from logging.handlers import RotatingFileHandler
import os

import config


def setup_logger(name, log_file, level=logging.INFO) -> logging.Logger:
    """Function to setup as many loggers as you want"""

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)

    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    handler = RotatingFileHandler(
        log_file_path,
        maxBytes=config.LOG_FILE_MAX_BYTES,
        backupCount=config.LOG_FILE_BACKUP_COUNT,
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create a default logger
logger = setup_logger("app", config.LOG_FILE_NAME)
