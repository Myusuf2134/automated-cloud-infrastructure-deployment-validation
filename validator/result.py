"""Shared validation result types and status aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Any


class Status(IntEnum):
    PASS = 0
    SKIPPED = 1
    WARNING = 2
    FAIL = 3


@dataclass
class CheckResult:
    layer: str
    name: str
    status: Status
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.name
        return value


def overall_status(results: list[CheckResult]) -> Status:
    if not results:
        return Status.SKIPPED
    if any(result.status == Status.FAIL for result in results):
        return Status.FAIL
    if any(result.status == Status.WARNING for result in results):
        return Status.WARNING
    if all(result.status == Status.SKIPPED for result in results):
        return Status.SKIPPED
    return Status.PASS
