"""Optional, read-only AWS state validation."""

from __future__ import annotations

from typing import Any

from validator.config import ValidationConfig
from validator.result import CheckResult, Status


def validate_aws_state(config: ValidationConfig, ec2_client: Any | None = None) -> list[CheckResult]:
    if not config.instance_id:
        return [CheckResult("infrastructure", "AWS State", Status.SKIPPED, "No instance ID")]
    if ec2_client is None:
        try:
            import boto3
        except ImportError:
            return [
                CheckResult(
                    "infrastructure",
                    "AWS State",
                    Status.SKIPPED,
                    "boto3 not installed",
                )
            ]
        try:
            ec2_client = boto3.client("ec2", region_name=config.aws_region)
        except Exception as exc:
            return [CheckResult("infrastructure", "AWS State", Status.WARNING, "Client unavailable", {"error": str(exc)})]
    try:
        response = ec2_client.describe_instances(InstanceIds=[config.instance_id])
        instances = [instance for reservation in response["Reservations"] for instance in reservation["Instances"]]
        if not instances:
            return [CheckResult("infrastructure", "AWS Instance State", Status.FAIL, "Not found")]
        instance = instances[0]
        state = instance["State"]["Name"]
        tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
        project_ok = not config.expected_project_tag or tags.get("Project") == config.expected_project_tag
        security_groups = instance.get("SecurityGroups", [])
        return [
            CheckResult(
                "infrastructure",
                "AWS Instance State",
                Status.PASS if state == "running" else Status.FAIL,
                state,
                {"instance_id": config.instance_id},
            ),
            CheckResult(
                "infrastructure",
                "AWS Project Tag",
                Status.PASS if project_ok else Status.FAIL,
                tags.get("Project", "missing"),
                {"expected": config.expected_project_tag},
            ),
            CheckResult(
                "infrastructure",
                "AWS Security Group",
                Status.PASS if security_groups else Status.FAIL,
                security_groups[0]["GroupId"] if security_groups else "missing",
            ),
        ]
    except Exception as exc:
        return [
            CheckResult(
                "infrastructure",
                "AWS State",
                Status.WARNING,
                "Read-only check unavailable",
                {"error": str(exc)},
            )
        ]
