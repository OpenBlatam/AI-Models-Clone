output "feature_public_ips" {
  value = module.docker_microservices[*].public_ip
} 