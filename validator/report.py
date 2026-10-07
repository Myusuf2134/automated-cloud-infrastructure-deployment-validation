"""Human-readable and JSON validation reports."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from validator.diagnostics import build_diagnostics
from validator.result import CheckResult, Status, overall_status


def build_payload(target: str, results: list[CheckResult]) -> dict[str, Any]:
    status = overall_status(results)
    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": status.name,
        "target": target,
        "checks": [result.to_dict() for result in results],
        "diagnostics": build_diagnostics(results),
    }


def render_json(target: str, results: list[CheckResult]) -> str:
    return json.dumps(build_payload(target, results), indent=2)


def render_text(target: str, results: list[CheckResult]) -> str:
    status = overall_status(results)
    lines = [
        "AUTOMATED CLOUD DEPLOYMENT VALIDATION",
        "=" * 54,
        f"Target: {target}",
    ]
    current_layer = None
    for result in results:
        if result.layer != current_layer:
            current_layer = result.layer
            lines.extend(["", current_layer.upper()])
        lines.append(f"{result.name:<26} {result.summary:<20} {result.status.name}")
    label = "PASSED" if status == Status.PASS else status.name
    diagnostics = build_diagnostics(results)
    if diagnostics["failure_layer"]:
        lines.extend(["", "FAILURE DIAGNOSTICS", "Observed facts:"])
        lines.extend(f"- {item}" for item in diagnostics["observed"])
        lines.append("Possible investigation areas:")
        lines.extend(f"- {item}" for item in diagnostics["possible_investigation_areas"])
        lines.append(f"Advisory: {diagnostics['advisory']}")
    lines.extend(["", "-" * 54, f"DEPLOYMENT STATUS: {label}", "-" * 54])
    return "\n".join(lines)
