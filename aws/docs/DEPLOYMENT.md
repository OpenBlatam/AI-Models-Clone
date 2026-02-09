# Detailed Deployment Guide

This guide provides step-by-step instructions for deploying the Blatam Academy project to AWS EC2.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Verification](#verification)
6. [Updates and Maintenance](#updates-and-maintenance)

## Prerequisites

### Required Software

1. **AWS CLI** (v2.x)
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Configure AWS credentials
   aws configure
   ```

2. **Terraform** (>= 1.0)
   ```bash
   # Install Terraform
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

3. **Ansible** (>= 2.9)
   ```bash
   # Install Ansible
   pip3 install ansible boto3
   
   # Install required Ansible collections
   ansible-galaxy collection install amazon.aws community.general
   ```

4. **SSH Key Pair**
   ```bash
   # Create key pair in AWS
   aws ec2 create-key-pair \
     --key-name blatam-academy-key \
     --query 'KeyMaterial' \
     --output text > ~/.ssh/blatam-academy-key.pem
   
   chmod 400 ~/.ssh/blatam-academy-key.pem
   ```

### AWS Account Setup

1. Create an AWS account if you don't have one
2. Configure IAM user with appropriate permissions:
   - EC2 full access
   - VPC full access
   - IAM read access (for instance profiles)
   - CloudWatch full access
   - S3 access (for Terraform state, if using S3 backend)

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd blatam-academy
```

### 2. Configure Terraform Variables

```bash
cd aws/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
aws_region = "us-east-1"
project_name = "blatam-academy"
environment = "production"
instance_type = "t3.medium"
key_name = "blatam-academy-key"
min_size = 1
max_size = 3
desired_capacity = 2
```

### 3. Configure Ansible Variables

```bash
cd ../ansible
```

Edit `group_vars/all.yml` with your configuration:

```yaml
project_name: "blatam-academy"
environment: "production"
app_dir: "/opt/blatam-academy"
# Add database_url, redis_url, etc. as needed
```

### 4. Set Up Environment

```bash
cd ../scripts
./setup_environment.sh
```

## Infrastructure Deployment

### Option 1: Automated Deployment

```bash
cd aws/scripts
export DEPLOY_INFRASTRUCTURE=true
export DEPLOY_APPLICATION=false
export ENVIRONMENT=production
./deploy.sh
```

### Option 2: Manual Terraform Deployment

```bash
cd aws/terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### What Gets Created

- VPC with public and private subnets across 2 availability zones
- Internet Gateway and NAT Gateways
- Security Groups for ALB, EC2, and Database
- Application Load Balancer
- Auto Scaling Group with EC2 instances
- Route tables and associations

### Verify Infrastructure

```bash
# Check Terraform outputs
terraform output

# Verify instances are running
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=blatam-academy" \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' \
  --output table
```

## Application Deployment

### Option 1: Automated Deployment

```bash
cd aws/scripts
export DEPLOY_INFRASTRUCTURE=false
export DEPLOY_APPLICATION=true
export ENVIRONMENT=production
./deploy.sh
```

### Option 2: Manual Ansible Deployment

```bash
cd aws/ansible

# Update EC2 inventory
ansible-inventory -i inventory/ec2.ini --list

# Run deployment playbook
ansible-playbook \
  -i inventory/ec2.ini \
  playbooks/deploy.yml \
  -e "environment=production" \
  --ask-become-pass
```

### Deployment Process

The Ansible playbook will:

1. **Common Setup**: Update packages, configure firewall, set timezone
2. **Docker Installation**: Install Docker and Docker Compose
3. **Python Setup**: Install Python and create virtual environment
4. **Nginx Configuration**: Set up reverse proxy
5. **Application Deployment**: 
   - Clone/copy application code
   - Create environment file
   - Install dependencies
   - Build Docker images (if using Docker)
   - Start application services

## Verification

### 1. Check Application Health

```bash
# Get load balancer DNS
cd aws/terraform
terraform output load_balancer_dns

# Test health endpoint
curl http://$(terraform output -raw load_balancer_dns)/health
```

### 2. Check Application Logs

```bash
# SSH into instance
ssh -i ~/.ssh/blatam-academy-key.pem ubuntu@<instance-ip>

# Check application logs
sudo journalctl -u blatam-academy -f
# Or if using Docker
docker-compose -f /opt/blatam-academy/docker-compose.yml logs -f
```

### 3. Verify Services

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Docker containers
docker ps

# Check application process
ps aux | grep python
```

## Updates and Maintenance

### Update Application

```bash
cd aws/ansible
ansible-playbook \
  -i inventory/ec2.ini \
  playbooks/update.yml \
  -e "git_branch=main" \
  --ask-become-pass
```

### Scale Instances

```bash
cd aws/terraform
terraform apply -var="desired_capacity=4"
```

### View Logs

```bash
# Application logs
ansible all -i inventory/ec2.ini -m shell -a "docker-compose -f /opt/blatam-academy/docker-compose.yml logs --tail=100"

# System logs
ansible all -i inventory/ec2.ini -m shell -a "sudo journalctl -u nginx -n 50"
```

### Backup

```bash
# Backup application data
ansible all -i inventory/ec2.ini -m shell -a "tar -czf /tmp/backup-$(date +%Y%m%d).tar.gz /opt/blatam-academy"

# Copy backup to S3
aws s3 cp /tmp/backup-*.tar.gz s3://your-backup-bucket/
```

## Troubleshooting

### Instance Not Accessible

1. Check security group rules
2. Verify key pair permissions
3. Check instance status in AWS console

### Application Not Starting

1. Check application logs
2. Verify environment variables
3. Check Docker container status
4. Review system resources

### Load Balancer Health Checks Failing

1. Verify health endpoint is accessible
2. Check security group allows traffic from ALB
3. Review target group health check configuration

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more details.

## Cleanup

To destroy all resources:

```bash
cd aws/terraform
terraform destroy
```

**Warning**: This will delete all infrastructure. Make sure to backup any important data first.

