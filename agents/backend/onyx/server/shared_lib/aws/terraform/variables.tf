# Variables for Terraform Configuration
# =====================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "Docker image URI"
  type        = string
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 2
}

variable "cpu" {
  description = "CPU units (256 = 0.25 vCPU)"
  type        = string
  default     = "256"
}

variable "memory" {
  description = "Memory in MB"
  type        = string
  default     = "512"
}




