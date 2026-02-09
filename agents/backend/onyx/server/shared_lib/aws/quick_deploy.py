"""
Quick Deploy para AWS
=====================

Script Python para deployment rápido y fácil en AWS.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_requirements():
    """Verifica que las herramientas necesarias estén instaladas"""
    required = {
        'aws': 'AWS CLI',
        'docker': 'Docker (para ECS)',
        'serverless': 'Serverless Framework (para Lambda)'
    }
    
    missing = []
    for cmd, name in required.items():
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(name)
    
    if missing:
        print(f"❌ Faltan herramientas: {', '.join(missing)}")
        return False
    
    return True


def check_aws_credentials():
    """Verifica credenciales de AWS"""
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            check=True
        )
        identity = json.loads(result.stdout)
        print(f"✅ AWS credentials OK - Account: {identity.get('Account')}")
        return True
    except subprocess.CalledProcessError:
        print("❌ AWS credentials no configuradas")
        print("   Configura con: aws configure")
        return False


def deploy_lambda(service_name: str, stage: str = "dev", region: str = "us-east-1"):
    """Deploy a AWS Lambda"""
    print(f"🚀 Deploying {service_name} to Lambda ({stage})...")
    
    # Generar configuración
    from shared_lib.aws import create_serverless_config
    
    print("📝 Generando configuración...")
    create_serverless_config(service_name, ".", "serverless")
    
    # Deploy
    print("📦 Deploying...")
    subprocess.run([
        'serverless', 'deploy',
        '--stage', stage,
        '--region', region
    ], check=True)
    
    # Info
    print("📊 Información del deployment:")
    subprocess.run(['serverless', 'info', '--stage', stage])


def deploy_ecs(service_name: str, region: str = "us-east-1"):
    """Deploy a AWS ECS"""
    print(f"🚀 Deploying {service_name} to ECS...")
    
    # Build Docker image
    print("🔨 Building Docker image...")
    subprocess.run([
        'docker', 'build',
        '-f', '../docker/Dockerfile',
        '-t', f'{service_name}:latest',
        '..'
    ], check=True)
    
    # Get account ID
    result = subprocess.run(
        ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
        capture_output=True,
        check=True,
        text=True
    )
    account_id = result.stdout.strip()
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{service_name}"
    
    # Create ECR repo
    print("📦 Creando ECR repository...")
    try:
        subprocess.run([
            'aws', 'ecr', 'describe-repositories',
            '--repository-names', service_name,
            '--region', region
        ], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        subprocess.run([
            'aws', 'ecr', 'create-repository',
            '--repository-name', service_name,
            '--region', region
        ], check=True)
    
    # Login to ECR
    print("🔐 Login a ECR...")
    login_cmd = subprocess.run(
        ['aws', 'ecr', 'get-login-password', '--region', region],
        capture_output=True,
        check=True,
        text=True
    )
    subprocess.run([
        'docker', 'login',
        '--username', 'AWS',
        '--password-stdin',
        ecr_repo
    ], input=login_cmd.stdout, text=True, check=True)
    
    # Tag and push
    print("📤 Pushing image...")
    subprocess.run(['docker', 'tag', f'{service_name}:latest', f'{ecr_repo}:latest'], check=True)
    subprocess.run(['docker', 'push', f'{ecr_repo}:latest'], check=True)
    
    print(f"✅ Image pushed: {ecr_repo}:latest")
    print(f"📝 Usa esta imagen en tu task definition: {ecr_repo}:latest")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python quick_deploy.py <tipo> [opciones]")
        print("\nTipos:")
        print("  lambda <service_name> [stage] [region]")
        print("  ecs <service_name> [region]")
        print("\nEjemplos:")
        print("  python quick_deploy.py lambda my-service dev us-east-1")
        print("  python quick_deploy.py ecs my-service us-east-1")
        sys.exit(1)
    
    deploy_type = sys.argv[1]
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_aws_credentials():
        sys.exit(1)
    
    if deploy_type == "lambda":
        service_name = sys.argv[2] if len(sys.argv) > 2 else "shared-lib-service"
        stage = sys.argv[3] if len(sys.argv) > 3 else "dev"
        region = sys.argv[4] if len(sys.argv) > 4 else "us-east-1"
        deploy_lambda(service_name, stage, region)
    
    elif deploy_type == "ecs":
        service_name = sys.argv[2] if len(sys.argv) > 2 else "shared-lib-service"
        region = sys.argv[3] if len(sys.argv) > 3 else "us-east-1"
        deploy_ecs(service_name, region)
    
    else:
        print(f"❌ Tipo no válido: {deploy_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()




