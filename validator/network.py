"""DNS resolution and TCP connectivity validation."""

from __future__ import annotations

import ipaddress
import socket
import time

from validator.config import ValidationConfig
from validator.result import CheckResult, Status


def validate_dns(config: ValidationConfig) -> CheckResult:
    try:
        address = ipaddress.ip_address(config.host)
        return CheckResult(
            "network",
            "DNS Resolution",
            Status.SKIPPED,
            "IP address supplied",
            {"resolved_addresses": [str(address)]},
        )
    except ValueError:
        pass

    started = time.perf_counter()
    try:
        info = socket.getaddrinfo(config.host, config.port, type=socket.SOCK_STREAM)
        elapsed_ms = (time.perf_counter() - started) * 1000
        addresses = sorted({item[4][0] for item in info})
        return CheckResult(
            "network",
            "DNS Resolution",
            Status.PASS,
            f"{elapsed_ms:.0f} ms",
            {"host": config.host, "resolved_addresses": addresses, "latency_ms": round(elapsed_ms, 2)},
        )
    except socket.gaierror as exc:
        return CheckResult(
            "network",
            "DNS Resolution",
            Status.FAIL,
            "Resolution failed",
            {"host": config.host, "error": str(exc)},
        )


def validate_tcp(config: ValidationConfig) -> CheckResult:
    started = time.perf_counter()
    try:
        with socket.create_connection((config.host, config.port), timeout=config.timeout_seconds):
            elapsed_ms = (time.perf_counter() - started) * 1000
        return CheckResult(
            "network",
            f"TCP :{config.port}",
            Status.PASS,
            f"{elapsed_ms:.0f} ms",
            {
                "host": config.host,
                "port": config.port,
                "latency_ms": round(elapsed_ms, 2),
            },
        )
    except (TimeoutError, socket.timeout) as exc:
        return CheckResult(
            "network",
            f"TCP :{config.port}",
            Status.FAIL,
            "Connection timed out",
            {"host": config.host, "port": config.port, "error": str(exc), "error_type": "timeout"},
        )
    except OSError as exc:
        return CheckResult(
            "network",
            f"TCP :{config.port}",
            Status.FAIL,
            "Connection failed",
            {"host": config.host, "port": config.port, "error": str(exc), "error_type": "connection"},
        )
