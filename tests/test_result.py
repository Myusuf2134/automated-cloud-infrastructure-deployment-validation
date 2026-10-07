from validator.result import CheckResult, Status, overall_status


def test_overall_pass() -> None:
    results = [
        CheckResult("network", "DNS", Status.SKIPPED, "IP supplied"),
        CheckResult("network", "TCP", Status.PASS, "1 ms"),
    ]
    assert overall_status(results) == Status.PASS


def test_overall_fail() -> None:
    results = [
        CheckResult("network", "TCP", Status.PASS, "1 ms"),
        CheckResult("application", "HTTP", Status.FAIL, "500"),
    ]
    assert overall_status(results) == Status.FAIL
