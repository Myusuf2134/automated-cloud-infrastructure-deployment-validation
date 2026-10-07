#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_command="python3"
if [[ -x "$repository_root/.venv/bin/python" ]]; then
  python_command="$repository_root/.venv/bin/python"
fi

if [[ $# -gt 0 ]]; then
  exec "$python_command" "$repository_root/validate.py" "$@"
fi

exec "$python_command" "$repository_root/validate.py" \
  --terraform-dir "$repository_root/infrastructure"
