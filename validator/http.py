"""HTTP health endpoint validation."""

from __future__ import annotations

import time
from typing import Any, Protocol

import requests

from validator.config import ValidationConfig
from validator.result import CheckResult, Status


class HTTPClient(Protocol):
    def get(self, url: str, *, timeout: float) -> Any: ...


def validate_http(config: ValidationConfig, client: HTTPClient = requests) -> list[CheckResult]:
    started = time.perf_counter()
    try:
        response = client.get(config.health_url, timeout=config.timeout_seconds)
        elapsed_ms = (time.perf_counter() - started) * 1000
    except requests.RequestException as exc:
        return [
            CheckResult(
                "application",
                f"GET {config.health_path}",
                Status.FAIL,
                "Request failed",
                {"url": config.health_url, "error": str(exc)},
            ),
            CheckResult("application", "Health Payload", Status.SKIPPED, "No HTTP response"),
        ]

    status_ok = response.status_code == config.expected_status
    response_result = CheckResult(
        "application",
        f"GET {config.health_path}",
        Status.PASS if status_ok else Status.FAIL,
        f"{response.status_code} / {elapsed_ms:.0f} ms",
        {
            "url": config.health_url,
            "status_code": response.status_code,
            "expected_status": config.expected_status,
            "latency_ms": round(elapsed_ms, 2),
        },
    )
    if not status_ok:
        return [response_result, CheckResult("application", "Health Payload", Status.SKIPPED, "Status mismatch")]

    try:
        body = response.json()
    except (ValueError, requests.JSONDecodeError) as exc:
        return [
            response_result,
            CheckResult(
                "application",
                "Health Payload",
                Status.FAIL,
                "Malformed JSON",
                {"error": str(exc)},
            ),
        ]
    healthy = isinstance(body, dict) and body.get("status") == "healthy"
    return [
        response_result,
        CheckResult(
            "application",
            "Health Payload",
            Status.PASS if healthy else Status.FAIL,
            "healthy" if healthy else "Expected status=healthy",
            {"body": body},
        ),
    ]
