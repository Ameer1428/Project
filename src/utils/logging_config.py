import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(service_name):
    """Configure logging for the specified service."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / f'{service_name}.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Setup logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Add performance logging
    perf_handler = logging.handlers.RotatingFileHandler(
        log_dir / f'{service_name}_performance.log',
        maxBytes=10485760,
        backupCount=5
    )
    perf_handler.setFormatter(formatter)
    perf_logger = logging.getLogger(f'{service_name}_performance')
    perf_logger.setLevel(logging.INFO)
    perf_logger.addHandler(perf_handler)

    return logger, perf_logger

def log_performance(logger, operation, start_time, end_time, **metrics):
    """Log performance metrics."""
    duration = end_time - start_time
    metrics_str = ' '.join(f'{k}={v}' for k, v in metrics.items())
    logger.info(f'Operation={operation} Duration={duration:.3f}s {metrics_str}')
