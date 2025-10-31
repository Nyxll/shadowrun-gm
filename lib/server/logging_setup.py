"""
Logging Configuration with Trace ID Support and Daily Rotation
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from contextvars import ContextVar
from .config import LOG_DIR


# Context variable for trace ID (thread-safe)
trace_id_var: ContextVar[str] = ContextVar('trace_id', default=None)


class TraceIDFormatter(logging.Formatter):
    """Custom formatter that handles missing trace_id"""
    
    def format(self, record):
        if not hasattr(record, 'trace_id'):
            record.trace_id = 'no-trace'
        return super().format(record)


class TraceIDLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that includes trace_id in log records"""
    
    def process(self, msg, kwargs):
        trace_id = trace_id_var.get(None) or 'no-trace'
        return msg, {**kwargs, 'extra': {'trace_id': trace_id}}


def setup_logging():
    """Setup structured logging with trace ID support and daily rotation"""
    
    detailed_formatter = TraceIDFormatter(
        '%(asctime)s | %(levelname)-8s | [Trace: %(trace_id)s] | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Main application log (with daily rotation at midnight)
    app_handler = TimedRotatingFileHandler(
        LOG_DIR / 'shadowrun-gm.log',
        when='midnight',      # Rotate at midnight
        interval=1,           # Every 1 day
        backupCount=30,       # Keep 30 days of logs
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    app_handler.suffix = '%Y-%m-%d'  # Add date suffix to rotated files
    
    # Error log (with daily rotation at midnight)
    error_handler = TimedRotatingFileHandler(
        LOG_DIR / 'shadowrun-gm-errors.log',
        when='midnight',      # Rotate at midnight
        interval=1,           # Every 1 day
        backupCount=30,       # Keep 30 days of logs
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    error_handler.suffix = '%Y-%m-%d'  # Add date suffix to rotated files
    
    # Console handler (simpler format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


# Initialize logging
logger = setup_logging()

# Create trace-aware logger
trace_logger = TraceIDLoggerAdapter(logger, {})
