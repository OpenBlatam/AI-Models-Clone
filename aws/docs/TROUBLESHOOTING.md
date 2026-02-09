# Troubleshooting Guide

Common issues and solutions when deploying to AWS EC2.

## Table of Contents

1. [Infrastructure Issues](#infrastructure-issues)
2. [Application Deployment Issues](#application-deployment-issues)
3. [Connectivity Issues](#connectivity-issues)
4. [Performance Issues](#performance-issues)
5. [Security Issues](#security-issues)

## Infrastructure Issues

### Terraform State Lock

**Problem**: Terraform state is locked.

**Solution**:
```bash
# Check for lock
aws dynamodb list-tables | grep terraform

# If using S3 backend, check for lock file
aws s3 ls s3://your-terraform-bucket/terraform.tfstate.d/

# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### EC2 Instances Not Launching

**Problem**: Instances fail to launch in Auto Scaling Group.

**Solution**:
1. Check CloudWatch logs for user data script:
   ```bash
   aws logs tail /aws/ec2/user-data --follow
   ```

2. Check launch template:
   ```bash
   aws ec2 describe-launch-template-versions \
     --launch-template-name <template-name>
   ```

3. Verify AMI availability:
   ```bash
   aws ec2 describe-images --image-ids <ami-id>
   ```

### VPC/Networking Issues

**Problem**: Instances can't reach internet or each other.

**Solution**:
1. Verify route tables:
   ```bash
   aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"
   ```

2. Check NAT Gateway status:
   ```bash
   aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=<vpc-id>"
   ```

3. Verify security group rules:
   ```bash
   aws ec2 describe-security-groups --group-ids <sg-id>
   ```

## Application Deployment Issues

### Ansible Connection Failures

**Problem**: Can't connect to EC2 instances via Ansible.

**Solution**:
1. Verify SSH key permissions:
   ```bash
   chmod 400 ~/.ssh/blatam-academy-key.pem
   ```

2. Test SSH connection manually:
   ```bash
   ssh -i ~/.ssh/blatam-academy-key.pem ubuntu@<instance-ip>
   ```

3. Check security group allows SSH (port 22)

4. Verify EC2 inventory:
   ```bash
   ansible-inventory -i inventory/ec2.ini --list
   ```

### Docker Installation Failures

**Problem**: Docker fails to install on instances.

**Solution**:
1. Check user data script logs:
   ```bash
   ssh ubuntu@<instance-ip> "sudo cat /var/log/user-data.log"
   ```

2. Manually install Docker:
   ```bash
   ansible all -i inventory/ec2.ini -m shell \
     -a "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh" \
     --become
   ```

### Application Not Starting

**Problem**: Application containers fail to start.

**Solution**:
1. Check Docker logs:
   ```bash
   ssh ubuntu@<instance-ip>
   docker-compose -f /opt/blatam-academy/docker-compose.yml logs
   ```

2. Verify environment variables:
   ```bash
   cat /opt/blatam-academy/.env
   ```

3. Check disk space:
   ```bash
   df -h
   ```

4. Verify application code:
   ```bash
   ls -la /opt/blatam-academy/
   ```

### Nginx Configuration Errors

**Problem**: Nginx fails to start or serve content.

**Solution**:
1. Test Nginx configuration:
   ```bash
   sudo nginx -t
   ```

2. Check Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Verify upstream connectivity:
   ```bash
   curl http://localhost:8000/health
   ```

## Connectivity Issues

### Can't Access Application via Load Balancer

**Problem**: Load balancer returns 502 or connection timeout.

**Solution**:
1. Check target group health:
   ```bash
   aws elbv2 describe-target-health \
     --target-group-arn <target-group-arn>
   ```

2. Verify security group allows traffic from ALB to instances

3. Check application is listening on correct port:
   ```bash
   ssh ubuntu@<instance-ip> "sudo netstat -tlnp | grep 8000"
   ```

4. Test health endpoint directly on instance:
   ```bash
   curl http://localhost:8000/health
   ```

### SSH Connection Timeout

**Problem**: Can't SSH into instances.

**Solution**:
1. Verify security group allows port 22 from your IP

2. Check instance is running:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id>
   ```

3. Verify key pair name matches:
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id> \
     --query 'Reservations[0].Instances[0].KeyName'
   ```

4. Check route table for public subnet

## Performance Issues

### High CPU Usage

**Problem**: Instances show high CPU utilization.

**Solution**:
1. Check CloudWatch metrics:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/EC2 \
     --metric-name CPUUtilization \
     --dimensions Name=InstanceId,Value=<instance-id> \
     --start-time <start-time> \
     --end-time <end-time> \
     --period 300 \
     --statistics Average
   ```

2. Identify resource-intensive processes:
   ```bash
   ssh ubuntu@<instance-ip> "top -b -n 1 | head -20"
   ```

3. Consider upgrading instance type

### High Memory Usage

**Problem**: Instances running out of memory.

**Solution**:
1. Check memory usage:
   ```bash
   ssh ubuntu@<instance-ip> "free -h"
   ```

2. Review Docker container memory limits

3. Consider adding swap space or upgrading instance

### Slow Application Response

**Problem**: Application responds slowly.

**Solution**:
1. Check application logs for errors

2. Verify database connection (if using RDS)

3. Check Redis connection (if using ElastiCache)

4. Review Nginx access logs for patterns:
   ```bash
   sudo tail -f /var/log/nginx/blatam-academy_access.log
   ```

5. Enable application profiling

## Security Issues

### Unauthorized Access Attempts

**Problem**: Seeing unauthorized access in logs.

**Solution**:
1. Review security group rules - restrict SSH access:
   ```bash
   # Update security group to only allow your IP
   aws ec2 authorize-security-group-ingress \
     --group-id <sg-id> \
     --protocol tcp \
     --port 22 \
     --cidr <your-ip>/32
   ```

2. Enable fail2ban:
   ```bash
   sudo apt-get install fail2ban
   ```

3. Review CloudWatch logs for suspicious activity

### SSL/TLS Certificate Issues

**Problem**: HTTPS not working or certificate errors.

**Solution**:
1. Verify ACM certificate is valid:
   ```bash
   aws acm list-certificates
   ```

2. Check certificate is attached to load balancer listener

3. Verify domain DNS points to load balancer

### Secrets Management

**Problem**: Need to update secrets or environment variables.

**Solution**:
1. Use AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name blatam-academy/production/database \
     --secret-string '{"username":"admin","password":"secret"}'
   ```

2. Update Ansible to fetch from Secrets Manager

3. Rotate secrets regularly

## Getting Help

### Useful Commands

```bash
# View all instances
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=blatam-academy" \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,PrivateIpAddress]' \
  --output table

# View security groups
aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=blatam-academy"

# View load balancer
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?contains(LoadBalancerName, `blatam-academy`)]'

# View CloudWatch logs
aws logs tail /aws/ec2/user-data --follow
```

### Log Locations

- User data script: `/var/log/user-data.log`
- Application logs: `/opt/blatam-academy/logs/` or Docker logs
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u <service-name>`

### Support Resources

- AWS Documentation: https://docs.aws.amazon.com/
- Terraform Documentation: https://www.terraform.io/docs
- Ansible Documentation: https://docs.ansible.com/

