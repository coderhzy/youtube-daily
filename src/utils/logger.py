"""
Logging configuration
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = 'blockchain_daily', log_dir: str = 'logs') -> logging.Logger:
    """
    Setup logger with file and console handlers

    Args:
        name: Logger name
        log_dir: Directory to store log files

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler
    log_file = log_path / f'blockchain_daily_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get existing logger or create new one

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
