#!/usr/bin/env python3
"""
🚀 Deploy to Production - Sistema SEO Ultra-Calidad
Script automatizado para deployment en producción
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class ProductionDeployer:
    """Deployer automatizado para producción."""
    
    def __init__(self):
        self.deployment_steps = []
        self.current_step = 0
        
    def run_command(self, command: str, description: str) -> bool:
        """Ejecuta un comando y muestra el progreso."""
        self.current_step += 1
        print(f"🔄 [{self.current_step}] {description}...")
        print(f"   Comando: {command}")
        
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ [{self.current_step}] {description} completado")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ [{self.current_step}] Error en {description}")
            print(f"   Error: {e.stderr}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Verifica prerequisitos del sistema."""
        print("🔍 Verificando prerequisitos del sistema...")
        
        # Verificar Docker
        if not self.run_command("docker --version", "Verificar Docker"):
            print("❌ Docker no está instalado o no es accesible")
            return False
        
        # Verificar kubectl
        if not self.run_command("kubectl version --client", "Verificar kubectl"):
            print("❌ kubectl no está instalado o no es accesible")
            return False
        
        # Verificar cluster Kubernetes
        if not self.run_command("kubectl cluster-info", "Verificar cluster Kubernetes"):
            print("❌ No se puede conectar al cluster Kubernetes")
            return False
        
        print("✅ Prerequisitos verificados correctamente")
        return True
    
    def build_docker_image(self) -> bool:
        """Construye la imagen Docker."""
        print("🐳 Construyendo imagen Docker...")
        
        # Construir imagen
        if not self.run_command("docker build -t seo-ultra-quality:latest .", "Construir imagen Docker"):
            return False
        
        # Verificar imagen
        if not self.run_command("docker images seo-ultra-quality:latest", "Verificar imagen construida"):
            return False
        
        print("✅ Imagen Docker construida correctamente")
        return True
    
    def deploy_kubernetes(self) -> bool:
        """Despliega en Kubernetes."""
        print("☸️ Desplegando en Kubernetes...")
        
        # Aplicar namespace
        if not self.run_command("kubectl apply -f k8s/namespace.yaml", "Aplicar namespace"):
            return False
        
        # Aplicar configmap
        if not self.run_command("kubectl apply -f k8s/configmap.yaml", "Aplicar configmap"):
            return False
        
        # Aplicar deployment
        if not self.run_command("kubectl apply -f k8s/deployment.yaml", "Aplicar deployment"):
            return False
        
        # Aplicar servicios
        if not self.run_command("kubectl apply -f k8s/service.yaml", "Aplicar servicios"):
            return False
        
        # Aplicar HPA
        if not self.run_command("kubectl apply -f k8s/hpa.yaml", "Aplicar HPA"):
            return False
        
        print("✅ Kubernetes desplegado correctamente")
        return True
    
    def verify_deployment(self) -> bool:
        """Verifica el deployment."""
        print("🔍 Verificando deployment...")
        
        # Esperar a que los pods estén listos
        print("⏳ Esperando a que los pods estén listos...")
        time.sleep(30)
        
        # Verificar estado de los pods
        if not self.run_command("kubectl get pods -n seo-system", "Verificar estado de pods"):
            return False
        
        # Verificar servicios
        if not self.run_command("kubectl get services -n seo-system", "Verificar servicios"):
            return False
        
        # Verificar HPA
        if not self.run_command("kubectl get hpa -n seo-system", "Verificar HPA"):
            return False
        
        print("✅ Deployment verificado correctamente")
        return True
    
    def setup_monitoring(self) -> bool:
        """Configura monitoreo básico."""
        print("📊 Configurando monitoreo...")
        
        # Crear directorio de monitoring
        monitoring_dir = Path("monitoring")
        monitoring_dir.mkdir(exist_ok=True)
        
        # Crear configuración básica de Prometheus
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'seo-engine'
    static_configs:
      - targets: ['seo-service:80']
    metrics_path: '/metrics'
    scrape_interval: 5s
"""
        
        with open("monitoring/prometheus.yml", "w") as f:
            f.write(prometheus_config)
        
        print("✅ Monitoreo configurado correctamente")
        return True
    
    def run_deployment(self) -> bool:
        """Ejecuta el deployment completo."""
        print("🚀 INICIANDO DEPLOYMENT A PRODUCCIÓN 🚀")
        print("=" * 60)
        
        steps = [
            ("Verificación de prerequisitos", self.check_prerequisites),
            ("Construcción de imagen Docker", self.build_docker_image),
            ("Deployment en Kubernetes", self.deploy_kubernetes),
            ("Verificación del deployment", self.verify_deployment),
            ("Configuración de monitoreo", self.setup_monitoring)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 Paso: {step_name}")
            print("-" * 40)
            
            if not step_func():
                print(f"\n❌ Deployment falló en: {step_name}")
                return False
            
            print(f"✅ {step_name} completado exitosamente")
        
        print("\n🎉 ¡DEPLOYMENT A PRODUCCIÓN COMPLETADO EXITOSAMENTE! 🎉")
        return True
    
    def show_status(self):
        """Muestra el estado del sistema."""
        print("\n📊 ESTADO DEL SISTEMA EN PRODUCCIÓN")
        print("=" * 60)
        
        # Mostrar pods
        print("\n🐳 Pods:")
        subprocess.run("kubectl get pods -n seo-system", shell=True)
        
        # Mostrar servicios
        print("\n🔌 Servicios:")
        subprocess.run("kubectl get services -n seo-system", shell=True)
        
        # Mostrar HPA
        print("\n📈 HPA:")
        subprocess.run("kubectl get hpa -n seo-system", shell=True)
        
        # Mostrar logs del primer pod
        print("\n📝 Logs del primer pod:")
        try:
            result = subprocess.run("kubectl get pods -n seo-system -o name | head -1", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pod_name = result.stdout.strip()
                subprocess.run(f"kubectl logs {pod_name} -n seo-system --tail=10", shell=True)
        except:
            print("No se pudieron obtener logs")

def main():
    """Función principal."""
    deployer = ProductionDeployer()
    
    if deployer.run_deployment():
        deployer.show_status()
        
        print("\n🌟 ¡SISTEMA SEO ULTRA-CALIDAD DESPLEGADO EN PRODUCCIÓN!")
        print("\n📚 Próximos pasos recomendados:")
        print("1. Configurar dominio y SSL")
        print("2. Configurar backup automático")
        print("3. Configurar alerting")
        print("4. Configurar CI/CD pipeline")
        print("5. Ejecutar tests de carga")
        print("6. Configurar logging centralizado")
        
        print("\n🔗 URLs de acceso:")
        print("- Aplicación: http://localhost:8000 (port-forward)")
        print("- Kubernetes Dashboard: kubectl proxy")
        print("- Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n monitoring")
        print("- Grafana: kubectl port-forward svc/grafana 3000:3000 -n monitoring")
        
        return True
    else:
        print("\n❌ Deployment falló. Revisar logs y reintentar.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
