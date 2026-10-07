"""Validation workflow orchestration."""

from __future__ import annotations

from validator.config import ValidationConfig
from validator.http import validate_http
from validator.network import validate_dns, validate_tcp
from validator.result import CheckResult, Status


def validate_configuration(config: ValidationConfig) -> CheckResult:
    return CheckResult(
        "infrastructure",
        "Deployment Target",
        Status.PASS,
        f"{config.host}:{config.port}",
        {"health_url": config.health_url},
    )


def run_validation(config: ValidationConfig, include_aws: bool = False) -> list[CheckResult]:
    """Run validation in dependency order, skipping downstream checks when blocked."""

    results = [validate_configuration(config)]
    if include_aws:
        from validator.aws_validation import validate_aws_state

        results.extend(validate_aws_state(config))
    dns = validate_dns(config)
    results.append(dns)
    if dns.status == Status.FAIL:
        results.extend(
            [
                CheckResult("network", f"TCP :{config.port}", Status.SKIPPED, "Blocked by DNS failure"),
                CheckResult("application", f"GET {config.health_path}", Status.SKIPPED, "Blocked by DNS failure"),
                CheckResult("application", "Health Payload", Status.SKIPPED, "No HTTP response"),
            ]
        )
        return results
    tcp = validate_tcp(config)
    results.append(tcp)
    if tcp.status == Status.FAIL:
        results.extend(
            [
                CheckResult("application", f"GET {config.health_path}", Status.SKIPPED, "Blocked by TCP failure"),
                CheckResult("application", "Health Payload", Status.SKIPPED, "No HTTP response"),
            ]
        )
        return results
    results.extend(validate_http(config))
    return results
