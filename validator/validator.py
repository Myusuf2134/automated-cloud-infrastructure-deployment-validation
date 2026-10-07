"""Validation workflow orchestration."""

from __future__ import annotations

from validator.config import ValidationConfig
from validator.result import CheckResult, Status


def validate_configuration(config: ValidationConfig) -> CheckResult:
    return CheckResult(
        "infrastructure",
        "Deployment Target",
        Status.PASS,
        f"{config.host}:{config.port}",
        {"health_url": config.health_url},
    )


def run_validation(config: ValidationConfig) -> list[CheckResult]:
    """Run the currently available validation layers."""

    return [validate_configuration(config)]
