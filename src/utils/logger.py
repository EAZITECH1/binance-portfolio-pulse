"""
Logging utilities for Binance PortfolioPulse AI.
"""
import logging
import sys
from typing import Optional


class Formatter(logging.Formatter):
    """Custom formatter with clean prefixes and optional ANSI color coding."""
    
    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    FORMAT_MAP = {
        logging.DEBUG: (GREY, "DEBUG"),
        logging.INFO: (BLUE, "INFO"),
        logging.WARNING: (YELLOW, "WARN"),
        logging.ERROR: (RED, "ERROR"),
        logging.CRITICAL: (RED + BOLD, "CRITICAL"),
    }

    def format(self, record: logging.LogRecord) -> str:
        color, tag = self.FORMAT_MAP.get(record.levelno, (self.RESET, "LOG"))
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        message = record.getMessage()
        if sys.stdout.isatty():
            prefix = f"{self.GREY}[{timestamp}]{self.RESET} {color}[{tag:^5}]{self.RESET} "
        else:
            prefix = f"[{timestamp}] [{tag:^5}] "
        return f"{prefix}{message}"


def setup_logger(name: str = "binance_pulse", level: int = logging.INFO) -> logging.Logger:
    """Set up and return the application logger directing to stderr so stdio protocol stdout remains clean."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(Formatter())
        logger.addHandler(handler)
        
    return logger


logger = setup_logger()

