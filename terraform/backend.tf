# =====================================================================
# Terraform Remote State Backend Configuration (Advanced Best Practices)
# =====================================================================
# - S3 for remote, encrypted, versioned state
# - DynamoDB for state locking
# - KMS for encryption at rest
# - Workspaces for environment separation (dev, prod, etc.)
# - State file key includes workspace for isolation
# =====================================================================

terraform {
  backend "s3" {
    bucket         = "blatam-terraform-state"                # Change to your bucket name
    key            = "envs/${terraform.workspace}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"                  # Change to your DynamoDB table name
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/your-kms-key-id" # Optional: Use your KMS key ARN
  }
}

# =====================================================================
# Usage:
#   terraform workspace new dev
#   terraform workspace new prod
#   terraform workspace select dev
#   terraform apply
#   terraform workspace select prod
#   terraform apply
# ===================================================================== 