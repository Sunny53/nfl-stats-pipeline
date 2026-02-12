"""
Logging utility for NFL Stats ETL Pipeline.
Provides structured logging with console and file output.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

from src.config import LOGGING_CONFIG, settings


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional custom log file path
        level: Optional log level (defaults to settings.log_level)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Update log file if custom path provided
    if log_file:
        LOGGING_CONFIG['handlers']['file']['filename'] = log_file
    
    # Update log level if provided
    if level:
        LOGGING_CONFIG['handlers']['console']['level'] = level
        LOGGING_CONFIG['handlers']['file']['level'] = level
        LOGGING_CONFIG['root']['level'] = level
    
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get logger
    logger = logging.getLogger(name)
    
    return logger


def log_api_request(logger: logging.Logger, endpoint: str, params: dict = None):
    """Log API request details."""
    logger.info(
        "API Request",
        extra={
            'endpoint': endpoint,
            'params': params or {},
            'event': 'api_request'
        }
    )


def log_api_response(
    logger: logging.Logger,
    endpoint: str,
    status_code: int,
    response_time: float
):
    """Log API response details."""
    logger.info(
        "API Response",
        extra={
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'event': 'api_response'
        }
    )


def log_data_quality(
    logger: logging.Logger,
    table_name: str,
    records_processed: int,
    records_valid: int,
    records_invalid: int
):
    """Log data quality metrics."""
    logger.info(
        "Data Quality Check",
        extra={
            'table': table_name,
            'processed': records_processed,
            'valid': records_valid,
            'invalid': records_invalid,
            'success_rate': round((records_valid / records_processed * 100), 2) if records_processed > 0 else 0,
            'event': 'data_quality'
        }
    )


def log_metric_calculation(
    logger: logging.Logger,
    metric_name: str,
    entity_type: str,
    entities_calculated: int,
    calculation_time: float
):
    """Log metric calculation details."""
    logger.info(
        "Metric Calculation",
        extra={
            'metric': metric_name,
            'entity_type': entity_type,
            'entities': entities_calculated,
            'calculation_time_ms': round(calculation_time * 1000, 2),
            'event': 'metric_calculation'
        }
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table_name: str,
    rows_affected: int,
    duration: float
):
    """Log database operation details."""
    logger.info(
        "Database Operation",
        extra={
            'operation': operation,
            'table': table_name,
            'rows_affected': rows_affected,
            'duration_ms': round(duration * 1000, 2),
            'event': 'database_operation'
        }
    )


def log_pipeline_stage(
    logger: logging.Logger,
    stage_name: str,
    status: str,
    duration: Optional[float] = None,
    details: Optional[dict] = None
):
    """Log ETL pipeline stage completion."""
    extra_data = {
        'stage': stage_name,
        'status': status,
        'event': 'pipeline_stage'
    }
    
    if duration:
        extra_data['duration_seconds'] = round(duration, 2)
    
    if details:
        extra_data.update(details)
    
    if status == 'success':
        logger.info(f"Pipeline Stage: {stage_name}", extra=extra_data)
    elif status == 'failed':
        logger.error(f"Pipeline Stage Failed: {stage_name}", extra=extra_data)
    else:
        logger.warning(f"Pipeline Stage Warning: {stage_name}", extra=extra_data)


# Example usage
if __name__ == "__main__":
    # Test logger setup
    logger = setup_logger(__name__)
    
    logger.info("Testing logger configuration")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test structured logging
    log_api_request(logger, "/scoreboard", {"season": 2024})
    log_api_response(logger, "/scoreboard", 200, 0.342)
    log_data_quality(logger, "games", 100, 98, 2)
    log_metric_calculation(logger, "Clutch Performance Index", "player", 500, 2.5)
    log_pipeline_stage(logger, "extraction", "success", 45.2)
    
    print("\nLogger test complete! Check logs/ directory for output.")
