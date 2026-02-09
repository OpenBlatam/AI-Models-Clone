# TruthGPT Infrastructure as Code
# Terraform configuration for TruthGPT deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

# Variables
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "truthgpt"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "truthgpt-cluster"
}

variable "node_group_name" {
  description = "EKS node group name"
  type        = string
  default     = "truthgpt-nodes"
}

variable "instance_types" {
  description = "EC2 instance types for EKS nodes"
  type        = list(string)
  default     = ["g4dn.xlarge", "g4dn.2xlarge"]
}

variable "min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 10
}

variable "desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 3
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC Configuration
resource "aws_vpc" "truthgpt_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "truthgpt_igw" {
  vpc_id = aws_vpc.truthgpt_vpc.id

  tags = {
    Name        = "${var.project_name}-igw"
    Environment = var.environment
  }
}

resource "aws_subnet" "truthgpt_public_subnets" {
  count = 2

  vpc_id                  = aws_vpc.truthgpt_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-public-subnet-${count.index + 1}"
    Environment = var.environment
    "kubernetes.io/role/elb" = "1"
  }
}

resource "aws_subnet" "truthgpt_private_subnets" {
  count = 2

  vpc_id            = aws_vpc.truthgpt_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "${var.project_name}-private-subnet-${count.index + 1}"
    Environment = var.environment
    "kubernetes.io/role/internal-elb" = "1"
  }
}

resource "aws_route_table" "truthgpt_public_rt" {
  vpc_id = aws_vpc.truthgpt_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.truthgpt_igw.id
  }

  tags = {
    Name        = "${var.project_name}-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "truthgpt_public_rta" {
  count = 2

  subnet_id      = aws_subnet.truthgpt_public_subnets[count.index].id
  route_table_id = aws_route_table.truthgpt_public_rt.id
}

resource "aws_eip" "truthgpt_nat_eip" {
  count = 2

  domain = "vpc"

  tags = {
    Name        = "${var.project_name}-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "truthgpt_nat_gw" {
  count = 2

  allocation_id = aws_eip.truthgpt_nat_eip[count.index].id
  subnet_id     = aws_subnet.truthgpt_public_subnets[count.index].id

  tags = {
    Name        = "${var.project_name}-nat-gw-${count.index + 1}"
    Environment = var.environment
  }

  depends_on = [aws_internet_gateway.truthgpt_igw]
}

resource "aws_route_table" "truthgpt_private_rt" {
  count = 2

  vpc_id = aws_vpc.truthgpt_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.truthgpt_nat_gw[count.index].id
  }

  tags = {
    Name        = "${var.project_name}-private-rt-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "truthgpt_private_rta" {
  count = 2

  subnet_id      = aws_subnet.truthgpt_private_subnets[count.index].id
  route_table_id = aws_route_table.truthgpt_private_rt[count.index].id
}

# Security Groups
resource "aws_security_group" "truthgpt_cluster_sg" {
  name_prefix = "${var.project_name}-cluster-sg"
  vpc_id      = aws_vpc.truthgpt_vpc.id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-cluster-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "truthgpt_node_sg" {
  name_prefix = "${var.project_name}-node-sg"
  vpc_id      = aws_vpc.truthgpt_vpc.id

  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.truthgpt_cluster_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-node-sg"
    Environment = var.environment
  }
}

# IAM Roles
resource "aws_iam_role" "truthgpt_cluster_role" {
  name = "${var.project_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-cluster-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "truthgpt_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.truthgpt_cluster_role.name
}

resource "aws_iam_role" "truthgpt_node_role" {
  name = "${var.project_name}-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-node-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "truthgpt_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.truthgpt_node_role.name
}

resource "aws_iam_role_policy_attachment" "truthgpt_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.truthgpt_node_role.name
}

resource "aws_iam_role_policy_attachment" "truthgpt_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.truthgpt_node_role.name
}

# EKS Cluster
resource "aws_eks_cluster" "truthgpt_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.truthgpt_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.truthgpt_public_subnets[*].id, aws_subnet.truthgpt_private_subnets[*].id)
    security_group_ids      = [aws_security_group.truthgpt_cluster_sg.id]
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.truthgpt_cluster_policy,
    aws_cloudwatch_log_group.truthgpt_cluster_logs
  ]

  tags = {
    Name        = var.cluster_name
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "truthgpt_cluster_logs" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-cluster-logs"
    Environment = var.environment
  }
}

# EKS Node Group
resource "aws_eks_node_group" "truthgpt_nodes" {
  cluster_name    = aws_eks_cluster.truthgpt_cluster.name
  node_group_name = var.node_group_name
  node_role_arn   = aws_iam_role.truthgpt_node_role.arn
  subnet_ids      = aws_subnet.truthgpt_private_subnets[*].id

  instance_types = var.instance_types

  scaling_config {
    desired_size = var.desired_size
    max_size     = var.max_size
    min_size     = var.min_size
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.truthgpt_node_policy,
    aws_iam_role_policy_attachment.truthgpt_cni_policy,
    aws_iam_role_policy_attachment.truthgpt_registry_policy
  ]

  tags = {
    Name        = "${var.project_name}-node-group"
    Environment = var.environment
  }
}

# RDS Database
resource "aws_db_subnet_group" "truthgpt_db_subnet_group" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.truthgpt_private_subnets[*].id

  tags = {
    Name        = "${var.project_name}-db-subnet-group"
    Environment = var.environment
  }
}

resource "aws_security_group" "truthgpt_db_sg" {
  name_prefix = "${var.project_name}-db-sg"
  vpc_id      = aws_vpc.truthgpt_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.truthgpt_node_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-db-sg"
    Environment = var.environment
  }
}

resource "aws_db_instance" "truthgpt_db" {
  identifier = "${var.project_name}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "truthgpt"
  username = "truthgpt"
  password = "changeme123" # Use AWS Secrets Manager in production

  vpc_security_group_ids = [aws_security_group.truthgpt_db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.truthgpt_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.project_name}-db"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "truthgpt_cache_subnet_group" {
  name       = "${var.project_name}-cache-subnet-group"
  subnet_ids = aws_subnet.truthgpt_private_subnets[*].id
}

resource "aws_security_group" "truthgpt_cache_sg" {
  name_prefix = "${var.project_name}-cache-sg"
  vpc_id      = aws_vpc.truthgpt_vpc.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.truthgpt_node_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-cache-sg"
    Environment = var.environment
  }
}

resource "aws_elasticache_replication_group" "truthgpt_cache" {
  replication_group_id       = "${var.project_name}-cache"
  description                = "TruthGPT Redis cache"

  node_type                  = "cache.t3.medium"
  port                       = 6379
  parameter_group_name        = "default.redis7"
  num_cache_clusters         = 2

  subnet_group_name          = aws_elasticache_subnet_group.truthgpt_cache_subnet_group.name
  security_group_ids         = [aws_security_group.truthgpt_cache_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled  = true

  tags = {
    Name        = "${var.project_name}-cache"
    Environment = var.environment
  }
}

# S3 Bucket for model storage
resource "aws_s3_bucket" "truthgpt_models" {
  bucket = "${var.project_name}-models-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-models"
    Environment = var.environment
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "truthgpt_models_versioning" {
  bucket = aws_s3_bucket.truthgpt_models.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "truthgpt_models_encryption" {
  bucket = aws_s3_bucket.truthgpt_models.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.truthgpt_cluster.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = aws_eks_cluster.truthgpt_cluster.vpc_config[0].cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = aws_iam_role.truthgpt_cluster_role.name
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.truthgpt_cluster.certificate_authority[0].data
}

output "cluster_name" {
  description = "The name/id of the EKS cluster"
  value       = aws_eks_cluster.truthgpt_cluster.name
}

output "cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster"
  value       = aws_eks_cluster.truthgpt_cluster.arn
}

output "db_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.truthgpt_db.endpoint
}

output "cache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.truthgpt_cache.primary_endpoint_address
}

output "s3_bucket_name" {
  description = "S3 bucket name for model storage"
  value       = aws_s3_bucket.truthgpt_models.bucket
}