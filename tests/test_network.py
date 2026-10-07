import socket

from validator.config import ValidationConfig
from validator.network import validate_dns, validate_tcp
from validator.result import Status


CONFIG = ValidationConfig(host="service.test", port=8080, timeout_seconds=1)


class FakeSocket:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def test_successful_tcp_validation(monkeypatch) -> None:
    monkeypatch.setattr("validator.network.socket.create_connection", lambda *args, **kwargs: FakeSocket())
    result = validate_tcp(CONFIG)
    assert result.status == Status.PASS
    assert result.details["port"] == 8080


def test_failed_tcp_validation(monkeypatch) -> None:
    def refuse(*args, **kwargs):
        raise ConnectionRefusedError("refused")

    monkeypatch.setattr("validator.network.socket.create_connection", refuse)
    result = validate_tcp(CONFIG)
    assert result.status == Status.FAIL
    assert result.details["error_type"] == "connection"


def test_tcp_timeout(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise socket.timeout("timed out")

    monkeypatch.setattr("validator.network.socket.create_connection", timeout)
    result = validate_tcp(CONFIG)
    assert result.status == Status.FAIL
    assert result.details["error_type"] == "timeout"


def test_dns_failure(monkeypatch) -> None:
    def fail(*args, **kwargs):
        raise socket.gaierror("not known")

    monkeypatch.setattr("validator.network.socket.getaddrinfo", fail)
    result = validate_dns(CONFIG)
    assert result.status == Status.FAIL
    assert result.details["host"] == "service.test"


def test_ip_address_skips_dns() -> None:
    result = validate_dns(ValidationConfig(host="192.0.2.10"))
    assert result.status == Status.SKIPPED
