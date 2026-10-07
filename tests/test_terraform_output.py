import json
from pathlib import Path

import pytest

from validator.config import ConfigurationError
from validator.terraform_output import load_terraform_outputs, parse_terraform_outputs


OUTPUTS = {
    "public_ip": {"value": "198.51.100.10"},
    "application_port": {"value": 80},
    "health_url": {"value": "http://198.51.100.10:80/health"},
    "instance_id": {"value": "i-example"},
    "aws_region": {"value": "us-east-1"},
    "project_name": {"value": "cloud-deployment-validator"},
}


def test_terraform_output_parsing() -> None:
    config = parse_terraform_outputs(OUTPUTS)
    assert config.host == "198.51.100.10"
    assert config.instance_id == "i-example"
    assert config.health_url == "http://198.51.100.10:80/health"


def test_missing_required_terraform_output() -> None:
    with pytest.raises(ConfigurationError, match="health_url.*public_ip"):
        parse_terraform_outputs({})


def test_terraform_command_output_is_parsed(monkeypatch, tmp_path: Path) -> None:
    completed = type("Completed", (), {"stdout": json.dumps(OUTPUTS)})()
    monkeypatch.setattr("validator.terraform_output.subprocess.run", lambda *args, **kwargs: completed)
    assert load_terraform_outputs(tmp_path).instance_id == "i-example"
