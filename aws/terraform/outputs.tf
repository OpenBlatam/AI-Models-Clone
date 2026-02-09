output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "load_balancer_dns" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = aws_lb.main.zone_id
}

output "ec2_instance_ids" {
  description = "EC2 instance IDs"
  value       = aws_instance.app[*].id
}

output "ec2_instance_public_ips" {
  description = "EC2 instance public IPs"
  value       = aws_instance.app[*].public_ip
}

output "ec2_instance_private_ips" {
  description = "EC2 instance private IPs"
  value       = aws_instance.app[*].private_ip
}

output "security_group_id" {
  description = "Security group ID for EC2 instances"
  value       = aws_security_group.app.id
}

output "ssh_command" {
  description = "SSH command to connect to instances"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.app[0].public_ip}"
}

