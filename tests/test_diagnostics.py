from validator.diagnostics import build_diagnostics
from validator.result import CheckResult, Status


def test_tcp_failure_diagnostics() -> None:
    results = [CheckResult("network", "TCP :80", Status.FAIL, "Connection timed out")]
    diagnostics = build_diagnostics(results)
    assert diagnostics["failure_layer"] == "tcp"
    assert "security group ingress rules" in diagnostics["possible_investigation_areas"]


def test_http_failure_diagnostics_acknowledge_tcp() -> None:
    results = [
        CheckResult("network", "TCP :80", Status.PASS, "10 ms"),
        CheckResult("application", "GET /health", Status.FAIL, "500 / 20 ms"),
    ]
    diagnostics = build_diagnostics(results)
    assert diagnostics["failure_layer"] == "http"
    assert diagnostics["observed"][0].startswith("TCP connectivity succeeded")
