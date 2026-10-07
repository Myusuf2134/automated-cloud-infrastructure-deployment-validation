"""Rotating file logging for validation runs."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from validator.result import CheckResult, Status


def setup_logging(path: str | Path = "logs/validator.log") -> logging.Logger:
    logger = logging.getLogger("deployment_validator")
    if logger.handlers:
        return logger
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_result(logger: logging.Logger, result: CheckResult) -> None:
    level = logging.INFO
    if result.status == Status.WARNING:
        level = logging.WARNING
    elif result.status == Status.FAIL:
        level = logging.ERROR
    logger.log(level, "layer=%s check=%r status=%s summary=%r", result.layer, result.name, result.status.name, result.summary)
