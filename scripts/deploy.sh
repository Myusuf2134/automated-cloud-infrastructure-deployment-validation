#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
terraform_dir="$repository_root/infrastructure"

echo "Preparing a Terraform plan only. This script does not apply infrastructure."
terraform -chdir="$terraform_dir" init
terraform -chdir="$terraform_dir" fmt -check
terraform -chdir="$terraform_dir" validate
terraform -chdir="$terraform_dir" plan -out=tfplan

echo
echo "STOP: review the complete plan and AWS cost implications before deployment."
echo "If explicitly approved, apply exactly this saved plan:"
echo "terraform -chdir=$terraform_dir apply tfplan"
