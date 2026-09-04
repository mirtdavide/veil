import logging
import os

from pythonjsonlogger.json import JsonFormatter

from app.config import settings

os.makedirs(os.path.dirname(settings.security_log_path), exist_ok=True)

security_logger = logging.getLogger("veil.security")
security_logger.setLevel(logging.INFO)

handler = logging.FileHandler(settings.security_log_path)
handler.setFormatter(JsonFormatter())
security_logger.addHandler(handler)


def log_security_event(event_type: str, **fields) -> None:
    security_logger.info(event_type, extra=fields)