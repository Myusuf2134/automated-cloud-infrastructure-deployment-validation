#!/usr/bin/env python3
"""CLI entry point for layered deployment validation."""

from __future__ import annotations

import argparse
import sys

from validator.config import ConfigurationError, ValidationConfig
from validator.logging_config import log_result, setup_logging
from validator.report import render_json, render_text
from validator.result import Status, overall_status
from validator.terraform_output import load_terraform_outputs
from validator.validator import run_validation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a cloud deployment layer by layer.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--host", help="Public IP or hostname to validate")
    source.add_argument("--terraform-dir", help="Directory whose Terraform outputs describe the target")
    parser.add_argument("--port", type=int, default=80, help="Application TCP port (default: 80)")
    parser.add_argument("--health-path", default="/health", help="HTTP health path")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-check timeout in seconds")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON output")
    parser.add_argument("--aws", action="store_true", help="Attempt optional read-only AWS state checks")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger = setup_logging()
    try:
        if args.terraform_dir:
            config = load_terraform_outputs(args.terraform_dir, args.timeout)
        else:
            config = ValidationConfig(
                host=args.host,
                port=args.port,
                health_path=args.health_path,
                timeout_seconds=args.timeout,
            )
    except ConfigurationError as exc:
        logger.error("configuration_error=%r", str(exc))
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    logger.info("validation_start target=%s port=%s", config.host, config.port)
    try:
        results = run_validation(config, include_aws=args.aws)
    except Exception as exc:
        logger.exception("unexpected_validation_error target=%s", config.host)
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2
    for result in results:
        log_result(logger, result)
    logger.info("validation_end target=%s status=%s", config.host, overall_status(results).name)
    print(render_json(config.host, results) if args.json_output else render_text(config.host, results))
    return 1 if overall_status(results) == Status.FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
