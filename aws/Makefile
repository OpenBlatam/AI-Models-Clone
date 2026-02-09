.PHONY: help init plan apply destroy deploy setup check-health update clean

# Default target
help:
	@echo "Blatam Academy AWS Deployment"
	@echo ""
	@echo "Available targets:"
	@echo "  make init          - Initialize Terraform"
	@echo "  make plan          - Plan Terraform deployment"
	@echo "  make apply         - Apply Terraform configuration"
	@echo "  make destroy       - Destroy all infrastructure"
	@echo "  make deploy        - Deploy application with Ansible"
	@echo "  make setup         - Set up local environment"
	@echo "  make check-health  - Check application health"
	@echo "  make update        - Update application"
	@echo "  make clean         - Clean temporary files"
	@echo ""
	@echo "Variables:"
	@echo "  ENVIRONMENT        - Environment name (default: production)"
	@echo "  DEPLOY_INFRA       - Deploy infrastructure (default: false)"
	@echo "  DEPLOY_APP         - Deploy application (default: true)"

ENVIRONMENT ?= production
DEPLOY_INFRA ?= false
DEPLOY_APP ?= true

# Terraform targets
init:
	cd terraform && terraform init

plan:
	cd terraform && terraform plan

apply:
	cd terraform && terraform apply

destroy:
	cd terraform && terraform destroy

# Ansible targets
deploy:
	cd ansible && \
	ansible-playbook \
		-i inventory/ec2.ini \
		playbooks/deploy.yml \
		-e "environment=$(ENVIRONMENT)"

update:
	cd ansible && \
	ansible-playbook \
		-i inventory/ec2.ini \
		playbooks/update.yml \
		-e "environment=$(ENVIRONMENT)"

setup:
	cd ansible && \
	ansible-playbook \
		-i inventory/ec2.ini \
		playbooks/setup.yml

# Utility targets
check-health:
	cd scripts && ./health_check.sh all

setup-env:
	cd scripts && ./setup_environment.sh

# Combined deployment
full-deploy: init apply deploy

# Cleanup
clean:
	find . -type f -name "*.retry" -delete
	find . -type f -name "*.log" -delete
	cd terraform && rm -f *.tfplan

# Validation
validate:
	cd terraform && terraform validate
	cd terraform && terraform fmt -check
	cd ansible && ansible-playbook --syntax-check playbooks/*.yml

