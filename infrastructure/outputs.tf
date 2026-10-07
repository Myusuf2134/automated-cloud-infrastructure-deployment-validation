output "instance_id" {
  description = "EC2 instance identifier used by optional AWS validation."
  value       = aws_instance.application.id
}

output "public_ip" {
  description = "Public IPv4 address assigned to the demonstration instance."
  value       = aws_instance.application.public_ip
}

output "application_port" {
  description = "Public TCP port for the sample application."
  value       = var.application_port
}

output "application_url" {
  description = "Base URL of the sample application."
  value       = "http://${aws_instance.application.public_ip}:${var.application_port}"
}

output "health_url" {
  description = "Health endpoint consumed by the Python validator."
  value       = "http://${aws_instance.application.public_ip}:${var.application_port}/health"
}

output "aws_region" {
  description = "Region containing the demonstration infrastructure."
  value       = var.aws_region
}

output "project_name" {
  description = "Expected Project tag value."
  value       = var.project_name
}
