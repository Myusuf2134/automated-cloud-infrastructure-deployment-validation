"""Read deployment target information from Terraform outputs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from validator.config import ConfigurationError, ValidationConfig


def _value(outputs: dict[str, Any], name: str, default: Any = None) -> Any:
    item = outputs.get(name, default)
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    return item


def parse_terraform_outputs(outputs: dict[str, Any], timeout_seconds: float = 5.0) -> ValidationConfig:
    health_url = _value(outputs, "health_url")
    host = _value(outputs, "public_ip")
    if not health_url and not host:
        raise ConfigurationError("Terraform outputs must contain 'health_url' or 'public_ip'.")
    common = {
        "timeout_seconds": timeout_seconds,
        "instance_id": _value(outputs, "instance_id"),
        "aws_region": _value(outputs, "aws_region"),
        "expected_project_tag": _value(outputs, "project_name"),
    }
    if health_url:
        return ValidationConfig.from_url(str(health_url), **common)
    return ValidationConfig(
        host=str(host),
        port=int(_value(outputs, "application_port", 80)),
        **common,
    )


def load_terraform_outputs(directory: str | Path, timeout_seconds: float = 5.0) -> ValidationConfig:
    path = Path(directory)
    if not path.is_dir():
        raise ConfigurationError(f"Terraform directory not found: {path}")
    try:
        completed = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ConfigurationError("Terraform executable was not found.") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or "No Terraform state/output is available."
        raise ConfigurationError(f"Could not read Terraform outputs: {detail}") from exc
    try:
        outputs = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Terraform returned invalid JSON: {exc}") from exc
    return parse_terraform_outputs(outputs, timeout_seconds)
