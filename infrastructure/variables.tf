variable "aws_region" {
  description = "AWS region in which to create the demo infrastructure."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier used for names and tags."
  type        = string
  default     = "cloud-deployment-validator"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,32}$", var.project_name))
    error_message = "project_name must contain 3-32 lowercase letters, numbers, or hyphens."
  }
}

variable "environment" {
  description = "Environment tag applied to all resources."
  type        = string
  default     = "demo"
}

variable "instance_type" {
  description = "Small EC2 instance type for the demonstration."
  type        = string
  default     = "t3.micro"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR for the demo VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "IPv4 CIDR for the single public subnet."
  type        = string
  default     = "10.42.1.0/24"
}

variable "application_port" {
  description = "Public TCP port exposed by the sample application."
  type        = number
  default     = 80

  validation {
    condition     = var.application_port >= 1 && var.application_port <= 65535
    error_message = "application_port must be between 1 and 65535."
  }
}

variable "application_cidr" {
  description = "IPv4 CIDR allowed to access the sample application."
  type        = string
  default     = "0.0.0.0/0"
}

variable "administrative_cidr" {
  description = "Optional restricted IPv4 CIDR for SSH. Null disables SSH ingress. Never use 0.0.0.0/0."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition     = var.administrative_cidr == null || var.administrative_cidr != "0.0.0.0/0"
    error_message = "SSH cannot be exposed to 0.0.0.0/0; use a restricted CIDR or null."
  }
}

variable "key_name" {
  description = "Optional existing EC2 key pair name. No key is needed when SSH is disabled."
  type        = string
  default     = null
  nullable    = true
}

variable "root_volume_size_gib" {
  description = "Size of the encrypted gp3 root volume."
  type        = number
  default     = 8

  validation {
    condition     = var.root_volume_size_gib >= 8 && var.root_volume_size_gib <= 30
    error_message = "root_volume_size_gib must be between 8 and 30 GiB."
  }
}
