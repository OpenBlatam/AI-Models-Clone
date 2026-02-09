#!/usr/bin/env python3
"""
Comando Único de Deployment
===========================

Script Python que automatiza todo el proceso de deployment.

Uso:
    python run.py deploy [tipo] [servicio] [stage] [region]
    python run.py setup [servicio] [region]
    python run.py local
"""

import sys
import subprocess
import os
from pathlib import Path


def check_command(cmd, name, install_cmd=None):
    """Verifica que un comando esté disponible"""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {name} no está instalado")
        if install_cmd:
            print(f"   Instala con: {install_cmd}")
        return False


def check_aws_credentials():
    """Verifica credenciales de AWS"""
    try:
        subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                      capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ AWS credentials no configuradas")
        print("   Configura con: aws configure")
        return False


def deploy_lambda(service_name, stage="dev", region="us-east-1"):
    """Deploy a AWS Lambda"""
    print(f"🚀 Deploying {service_name} to Lambda ({stage})...")
    
    # Verificar Serverless Framework
    if not check_command('serverless', 'Serverless Framework', 
                        'npm install -g serverless'):
        print("⚠️  Instalando Serverless Framework...")
        subprocess.run(['npm', 'install', '-g', 'serverless', 
                       'serverless-python-requirements'], check=True)
    
    # Setup recursos
    print("📦 Configurando recursos AWS...")
    subprocess.run(['python3', 'aws/setup_aws.py', service_name, region])
    
    # Deploy
    print("🚀 Deploying...")
    subprocess.run(['python3', 'aws/quick_deploy.py', 'lambda', 
                   service_name, stage, region], check=True)
    
    print("✅ Deployment completado")
    print("\n📊 Información:")
    subprocess.run(['serverless', 'info', '--stage', stage])


def deploy_ecs(service_name, region="us-east-1"):
    """Deploy a AWS ECS"""
    print(f"🚀 Deploying {service_name} to ECS...")
    
    # Verificar Docker
    if not check_command('docker', 'Docker', 'Instala Docker Desktop'):
        sys.exit(1)
    
    # Setup recursos
    print("📦 Configurando recursos AWS...")
    subprocess.run(['python3', 'aws/setup_aws.py', service_name, region])
    
    # Deploy
    print("🚀 Deploying...")
    subprocess.run(['python3', 'aws/quick_deploy.py', 'ecs', 
                   service_name, region], check=True)
    
    print("✅ Deployment completado")


def deploy_local():
    """Iniciar servicios locales"""
    print("🚀 Iniciando servicios locales...")
    
    docker_compose_path = Path(__file__).parent / "docker" / "docker-compose.yml"
    if not docker_compose_path.exists():
        print("❌ docker-compose.yml no encontrado")
        sys.exit(1)
    
    os.chdir(docker_compose_path.parent)
    subprocess.run(['docker-compose', 'up', '-d'], check=True)
    
    print("✅ Servicios iniciados")
    print("   API: http://localhost:8030")
    print("   Docs: http://localhost:8030/docs")
    print("   RabbitMQ: http://localhost:15672")
    print("   Grafana: http://localhost:3000")


def setup(service_name, region="us-east-1"):
    """Configurar recursos AWS"""
    print(f"📦 Configurando recursos AWS para {service_name}...")
    subprocess.run(['python3', 'aws/setup_aws.py', service_name, region], check=True)
    print("✅ Configuración completada")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python run.py <comando> [opciones]")
        print("\nComandos:")
        print("  deploy <tipo> [servicio] [stage] [region]")
        print("    - tipo: lambda, ecs, local")
        print("    - Ejemplo: python run.py deploy lambda mi-servicio dev us-east-1")
        print("\n  setup [servicio] [region]")
        print("    - Ejemplo: python run.py setup mi-servicio us-east-1")
        print("\n  local")
        print("    - Inicia servicios locales con Docker Compose")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Verificar prerequisitos básicos
    if command != "local":
        if not check_command('aws', 'AWS CLI', 'pip install awscli'):
            sys.exit(1)
        if not check_aws_credentials():
            sys.exit(1)
        if not check_command('python3', 'Python3'):
            sys.exit(1)
    
    if command == "deploy":
        if len(sys.argv) < 3:
            print("❌ Especifica el tipo de deployment: lambda, ecs, o local")
            sys.exit(1)
        
        deploy_type = sys.argv[2]
        service_name = sys.argv[3] if len(sys.argv) > 3 else "shared-lib-service"
        stage = sys.argv[4] if len(sys.argv) > 4 else "dev"
        region = sys.argv[5] if len(sys.argv) > 5 else "us-east-1"
        
        if deploy_type == "lambda":
            deploy_lambda(service_name, stage, region)
        elif deploy_type == "ecs":
            deploy_ecs(service_name, region)
        elif deploy_type == "local":
            deploy_local()
        else:
            print(f"❌ Tipo no válido: {deploy_type}")
            print("   Opciones: lambda, ecs, local")
            sys.exit(1)
    
    elif command == "setup":
        service_name = sys.argv[2] if len(sys.argv) > 2 else "shared-lib-service"
        region = sys.argv[3] if len(sys.argv) > 3 else "us-east-1"
        setup(service_name, region)
    
    elif command == "local":
        deploy_local()
    
    else:
        print(f"❌ Comando no reconocido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()




