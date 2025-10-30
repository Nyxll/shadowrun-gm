"""
Logging utilities for consistent output across all tools

This module provides standardized logging configuration
to ensure all tools and tests use the same log format.
"""
import logging
import sys
from typing import Optional
from datetime import datetime

def setup_logger(
    name: str, 
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with consistent formatting
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default INFO)
        log_file: Optional file path for file logging
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logger(__name__)
        logger.info("Starting operation")
        logger.error("Operation failed")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format: [2025-10-29 00:32:45] INFO: Message
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_operation(
    logger: logging.Logger, 
    operation: str, 
    details: Optional[str] = None,
    level: int = logging.INFO
):
    """Log an operation with consistent formatting
    
    Args:
        logger: Logger instance
        operation: Operation name (e.g., "IMPORT", "CHECK", "FIX")
        details: Optional details about the operation
        level: Log level (default INFO)
    
    Example:
        logger = setup_logger(__name__)
        log_operation(logger, "IMPORT", "Importing characters from file")
        log_operation(logger, "ERROR", "Failed to connect", level=logging.ERROR)
    """
    msg = f"[{operation}]"
    if details:
        msg += f" {details}"
    logger.log(level, msg)

def log_success(logger: logging.Logger, message: str):
    """Log a success message with ✓ symbol
    
    Args:
        logger: Logger instance
        message: Success message
    """
    logger.info(f"✓ {message}")

def log_failure(logger: logging.Logger, message: str):
    """Log a failure message with ✗ symbol
    
    Args:
        logger: Logger instance
        message: Failure message
    """
    logger.error(f"✗ {message}")

def log_warning(logger: logging.Logger, message: str):
    """Log a warning message with ⚠ symbol
    
    Args:
        logger: Logger instance
        message: Warning message
    """
    logger.warning(f"⚠ {message}")

def log_progress(logger: logging.Logger, current: int, total: int, item: str = "items"):
    """Log progress information
    
    Args:
        logger: Logger instance
        current: Current count
        total: Total count
        item: Item name (default "items")
    
    Example:
        log_progress(logger, 5, 10, "characters")
        # Output: [2025-10-29 00:32:45] INFO: Progress: 5/10 characters (50%)
    """
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"Progress: {current}/{total} {item} ({percentage:.0f}%)")

def log_section(logger: logging.Logger, title: str):
    """Log a section header
    
    Args:
        logger: Logger instance
        title: Section title
    
    Example:
        log_section(logger, "Database Connection")
        # Output:
        # ======================================================================
        # Database Connection
        # ======================================================================
    """
    separator = "=" * 70
    logger.info(separator)
    logger.info(title)
    logger.info(separator)

def log_table(logger: logging.Logger, headers: list, rows: list):
    """Log data in table format
    
    Args:
        logger: Logger instance
        headers: List of column headers
        rows: List of row data (each row is a list)
    
    Example:
        log_table(logger, 
            ["Name", "Type", "Status"],
            [
                ["Platinum", "Street Samurai", "Active"],
                ["Oak", "Shaman", "Active"]
            ]
        )
    """
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)
    
    logger.info(header_line)
    logger.info(separator)
    
    # Format rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        logger.info(row_line)

class OperationTimer:
    """Context manager for timing operations
    
    Example:
        logger = setup_logger(__name__)
        with OperationTimer(logger, "Character Import"):
            # Do work
            import_characters()
        # Output: [2025-10-29 00:32:45] INFO: Character Import completed in 2.34s
    """
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if exc_type is None:
            self.logger.info(f"{self.operation} completed in {elapsed:.2f}s")
        else:
            self.logger.error(f"{self.operation} failed after {elapsed:.2f}s")
        return False  # Don't suppress exceptions
