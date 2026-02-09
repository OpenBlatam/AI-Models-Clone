"""
Setup AWS - Configuración Automática
=====================================

Configura automáticamente recursos de AWS necesarios para el deployment.
"""

import json
import subprocess
import sys
from typing import Dict, Optional


def run_aws_command(cmd: list, capture_output: bool = True) -> Optional[Dict]:
    """Ejecuta comando de AWS CLI"""
    try:
        result = subprocess.run(
            ['aws'] + cmd,
            capture_output=capture_output,
            check=True,
            text=True
        )
        if capture_output and result.stdout:
            return json.loads(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {' '.join(cmd)}")
        print(f"   {e.stderr}")
        return None
    except json.JSONDecodeError:
        return result.stdout if hasattr(result, 'stdout') else True


def setup_dynamodb_table(table_name: str, region: str = "us-east-1") -> bool:
    """Crea tabla de DynamoDB"""
    print(f"📦 Creando tabla DynamoDB: {table_name}...")
    
    # Verificar si existe
    try:
        run_aws_command([
            'dynamodb', 'describe-table',
            '--table-name', table_name,
            '--region', region
        ])
        print(f"✅ Tabla {table_name} ya existe")
        return True
    except:
        pass
    
    # Crear tabla
    table_def = {
        "TableName": table_name,
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"}
        ],
        "BillingMode": "PAY_PER_REQUEST"
    }
    
    result = run_aws_command([
        'dynamodb', 'create-table',
        '--region', region,
        '--cli-input-json', json.dumps(table_def)
    ], capture_output=False)
    
    if result:
        print(f"✅ Tabla {table_name} creada")
        return True
    return False


def setup_s3_bucket(bucket_name: str, region: str = "us-east-1") -> bool:
    """Crea bucket de S3"""
    print(f"📦 Creando bucket S3: {bucket_name}...")
    
    # Verificar si existe
    try:
        run_aws_command([
            's3api', 'head-bucket',
            '--bucket', bucket_name
        ])
        print(f"✅ Bucket {bucket_name} ya existe")
        return True
    except:
        pass
    
    # Crear bucket
    cmd = ['s3', 'mb', f's3://{bucket_name}']
    if region != "us-east-1":
        cmd.extend(['--region', region])
    
    result = run_aws_command(cmd, capture_output=False)
    
    if result:
        print(f"✅ Bucket {bucket_name} creado")
        return True
    return False


def setup_cloudwatch_log_group(log_group: str, region: str = "us-east-1") -> bool:
    """Crea log group de CloudWatch"""
    print(f"📦 Creando CloudWatch log group: {log_group}...")
    
    # Verificar si existe
    try:
        run_aws_command([
            'logs', 'describe-log-groups',
            '--log-group-name-prefix', log_group,
            '--region', region
        ])
        print(f"✅ Log group {log_group} ya existe")
        return True
    except:
        pass
    
    # Crear log group
    result = run_aws_command([
        'logs', 'create-log-group',
        '--log-group-name', log_group,
        '--region', region
    ], capture_output=False)
    
    if result:
        print(f"✅ Log group {log_group} creado")
        return True
    return False


def setup_ecr_repository(repo_name: str, region: str = "us-east-1") -> bool:
    """Crea ECR repository"""
    print(f"📦 Creando ECR repository: {repo_name}...")
    
    # Verificar si existe
    try:
        run_aws_command([
            'ecr', 'describe-repositories',
            '--repository-names', repo_name,
            '--region', region
        ])
        print(f"✅ ECR repository {repo_name} ya existe")
        return True
    except:
        pass
    
    # Crear repository
    result = run_aws_command([
        'ecr', 'create-repository',
        '--repository-name', repo_name,
        '--region', region
    ])
    
    if result:
        print(f"✅ ECR repository {repo_name} creado")
        return True
    return False


def setup_all(service_name: str, region: str = "us-east-1"):
    """Configura todos los recursos necesarios"""
    print(f"🚀 Configurando recursos AWS para {service_name}...")
    print(f"   Region: {region}\n")
    
    # Verificar credenciales
    try:
        identity = run_aws_command(['sts', 'get-caller-identity'])
        if identity:
            print(f"✅ AWS Account: {identity.get('Account')}")
            print(f"✅ User/Role: {identity.get('Arn')}\n")
    except:
        print("❌ Error verificando credenciales AWS")
        sys.exit(1)
    
    # Setup recursos
    setup_dynamodb_table(f"{service_name}-table", region)
    setup_s3_bucket(f"{service_name}-bucket-{region}", region)
    setup_cloudwatch_log_group(f"/aws/lambda/{service_name}", region)
    setup_cloudwatch_log_group(f"/ecs/{service_name}", region)
    setup_ecr_repository(service_name, region)
    
    print("\n✅ Configuración completada")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python setup_aws.py <service_name> [region]")
        print("\nEjemplo:")
        print("  python setup_aws.py my-service us-east-1")
        sys.exit(1)
    
    service_name = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "us-east-1"
    
    setup_all(service_name, region)


if __name__ == "__main__":
    main()




