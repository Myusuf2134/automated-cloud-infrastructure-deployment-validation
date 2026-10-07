# Terraform Infrastructure

This module defines one intentionally small AWS deployment: a VPC, public subnet, Internet Gateway, public route table, security group, and EC2 instance. SSH is disabled by default. The application port is the only public inbound rule unless a restricted administrative CIDR is explicitly supplied.

No credentials belong in this directory. Terraform uses the standard AWS provider credential chain.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
```

Do not run `terraform apply` until the plan, selected AWS account, region, and potential charges have been reviewed.
