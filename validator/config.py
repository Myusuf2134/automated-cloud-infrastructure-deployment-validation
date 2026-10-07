"""Validator configuration and input validation."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


class ConfigurationError(ValueError):
    """Raised when required deployment information is invalid."""


@dataclass(frozen=True)
class ValidationConfig:
    host: str
    port: int = 80
    health_path: str = "/health"
    expected_status: int = 200
    timeout_seconds: float = 5.0
    instance_id: str | None = None
    aws_region: str | None = None
    expected_project_tag: str | None = None

    def __post_init__(self) -> None:
        if not self.host or not self.host.strip():
            raise ConfigurationError("A non-empty deployment host is required.")
        if not 1 <= self.port <= 65535:
            raise ConfigurationError("Port must be between 1 and 65535.")
        if not self.health_path.startswith("/"):
            raise ConfigurationError("Health path must begin with '/'.")
        if not 100 <= self.expected_status <= 599:
            raise ConfigurationError("Expected HTTP status must be between 100 and 599.")
        if self.timeout_seconds <= 0:
            raise ConfigurationError("Timeout must be greater than zero.")

    @property
    def health_url(self) -> str:
        host = self.host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        return f"http://{host}:{self.port}{self.health_path}"

    @classmethod
    def from_url(cls, url: str, **kwargs) -> "ValidationConfig":
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ConfigurationError("Application URL must use http:// or https:// and include a host.")
        default_port = 443 if parsed.scheme == "https" else 80
        return cls(
            host=parsed.hostname,
            port=parsed.port or default_port,
            health_path=parsed.path or "/health",
            **kwargs,
        )
