"""Layer-aware, deterministic troubleshooting context."""

from __future__ import annotations

from typing import Any

from validator.result import CheckResult, Status


def build_diagnostics(results: list[CheckResult]) -> dict[str, Any]:
    """Explain observed failures without claiming an unverified root cause."""

    failed = [result for result in results if result.status == Status.FAIL]
    if not failed:
        return {"failure_layer": None, "observed": [], "possible_investigation_areas": []}

    observed = [f"{result.name}: {result.summary}" for result in failed]
    failed_names = {result.name for result in failed}
    tcp_passed = any(result.name.startswith("TCP :") and result.status == Status.PASS for result in results)

    if "DNS Resolution" in failed_names:
        layer = "dns"
        areas = [
            "hostname spelling and deployment output",
            "local DNS resolver availability",
            "DNS records and propagation",
            "outbound network access to a DNS resolver",
        ]
    elif any(name.startswith("TCP :") for name in failed_names):
        layer = "tcp"
        areas = [
            "EC2 instance state and system status checks",
            "security group ingress rules",
            "public subnet route table and Internet Gateway attachment",
            "application listener and configured port",
            "Docker port publishing",
            "host firewall",
        ]
    elif any(name.startswith("GET ") for name in failed_names):
        layer = "http"
        if tcp_passed:
            observed.insert(0, "TCP connectivity succeeded; the target port is reachable.")
        areas = [
            "application process and container state",
            "application logs",
            "health endpoint path and expected HTTP status",
            "reverse proxy or HTTP server configuration",
            "application dependencies and startup errors",
        ]
    elif "Health Payload" in failed_names:
        layer = "application"
        if tcp_passed:
            observed.insert(0, "Network connectivity and the HTTP request succeeded.")
        areas = [
            "health endpoint response contract",
            "application readiness and dependencies",
            "application logs",
        ]
    else:
        layer = "infrastructure"
        areas = [
            "Terraform outputs and selected AWS account/region",
            "EC2 instance state",
            "expected resource tags and security group attachment",
        ]

    return {
        "failure_layer": layer,
        "observed": observed,
        "possible_investigation_areas": areas,
        "advisory": "Possible investigation areas are hypotheses and must be verified against system evidence.",
    }


def build_incident_context(results: list[CheckResult]) -> dict[str, Any]:
    """Structured context suitable for a future optional incident-analysis consumer."""

    return {
        "checks": {result.name: result.status.name for result in results},
        "diagnostics": build_diagnostics(results),
    }
