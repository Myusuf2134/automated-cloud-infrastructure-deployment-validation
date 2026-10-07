#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
terraform_dir="$repository_root/infrastructure"

echo "Terraform will propose destroying resources tracked by state in: $terraform_dir"
terraform -chdir="$terraform_dir" plan -destroy
echo
read -r -p "Type DESTROY to run terraform destroy: " confirmation
if [[ "$confirmation" != "DESTROY" ]]; then
  echo "Destroy cancelled."
  exit 1
fi

terraform -chdir="$terraform_dir" destroy
echo "Destroy finished. Verify the selected AWS account and region for unexpected remaining resources."
