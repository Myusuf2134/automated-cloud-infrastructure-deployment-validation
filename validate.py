#!/usr/bin/env python3
"""CLI entry point for layered deployment validation."""

from __future__ import annotations

import argparse
import sys

from validator.config import ConfigurationError, ValidationConfig
from validator.report import render_json, render_text
from validator.validator import run_validation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a cloud deployment layer by layer.")
    parser.add_argument("--host", required=True, help="Public IP or hostname to validate")
    parser.add_argument("--port", type=int, default=80, help="Application TCP port (default: 80)")
    parser.add_argument("--health-path", default="/health", help="HTTP health path")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-check timeout in seconds")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = ValidationConfig(
            host=args.host,
            port=args.port,
            health_path=args.health_path,
            timeout_seconds=args.timeout,
        )
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    results = run_validation(config)
    print(render_json(config.host, results) if args.json_output else render_text(config.host, results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
