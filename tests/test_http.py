import requests

from validator.config import ValidationConfig
from validator.http import validate_http
from validator.result import Status


CONFIG = ValidationConfig(host="service.test", port=8080)


class Response:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


class Client:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def get(self, url, *, timeout):
        if self.error:
            raise self.error
        return self.response


def test_successful_http_validation() -> None:
    results = validate_http(CONFIG, Client(Response(payload={"status": "healthy"})))
    assert [result.status for result in results] == [Status.PASS, Status.PASS]


def test_http_500_failure() -> None:
    results = validate_http(CONFIG, Client(Response(status_code=500, payload={})))
    assert results[0].status == Status.FAIL
    assert results[0].details["status_code"] == 500
    assert results[1].status == Status.SKIPPED


def test_http_timeout_handling() -> None:
    results = validate_http(CONFIG, Client(error=requests.Timeout("slow")))
    assert results[0].status == Status.FAIL
    assert "slow" in results[0].details["error"]


def test_malformed_health_response() -> None:
    results = validate_http(CONFIG, Client(Response(json_error=ValueError("bad json"))))
    assert results[0].status == Status.PASS
    assert results[1].status == Status.FAIL
    assert results[1].summary == "Malformed JSON"


def test_unhealthy_health_payload() -> None:
    results = validate_http(CONFIG, Client(Response(payload={"status": "starting"})))
    assert results[1].status == Status.FAIL
