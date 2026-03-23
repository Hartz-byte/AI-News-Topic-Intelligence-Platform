import sys
import logging
from loguru import logger
from .config import get_settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def filter_noise(record):
    msg = str(record["message"])
    if "discarding data" in msg:
        return False
    return True

def setup_logging() -> None:
    settings = get_settings()
    
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in ("uvicorn.access", "uvicorn.error", "uvicorn", "fastapi", "apscheduler"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
        filter=filter_noise
    )
    logger.add(
        "app.log",
        rotation="1 MB",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        filter=filter_noise
    )
