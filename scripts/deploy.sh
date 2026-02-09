#!/bin/bash
# TruthGPT Deployment Scripts
# Comprehensive deployment automation for TruthGPT optimization core

set -e

# Configuration
TRUTHGPT_VERSION="1.0.0"
DOCKER_REGISTRY="your-registry.com"
KUBERNETES_NAMESPACE="truthgpt"
MODEL_NAME="TruthGPT-PiMoE-v1"
NUM_EXPERTS="8"
GPU_COUNT="1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed"
        exit 1
    fi
    
    # Check GPU availability
    if ! nvidia-smi &> /dev/null; then
        log_warning "NVIDIA GPU not detected, using CPU mode"
    fi
    
    log_success "Prerequisites check completed"
}

# Build Docker image
build_docker_image() {
    log_info "Building Docker image..."
    
    docker build -t ${DOCKER_REGISTRY}/truthgpt:${TRUTHGPT_VERSION} \
        -t ${DOCKER_REGISTRY}/truthgpt:latest \
        -f Dockerfile.prod .
    
    log_success "Docker image built successfully"
}

# Push Docker image
push_docker_image() {
    log_info "Pushing Docker image to registry..."
    
    docker push ${DOCKER_REGISTRY}/truthgpt:${TRUTHGPT_VERSION}
    docker push ${DOCKER_REGISTRY}/truthgpt:latest
    
    log_success "Docker image pushed successfully"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl create namespace ${KUBERNETES_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    kubectl apply -f kubernetes/configmap.yaml -n ${KUBERNETES_NAMESPACE}
    kubectl apply -f kubernetes/secret.yaml -n ${KUBERNETES_NAMESPACE}
    kubectl apply -f kubernetes/deployment.yaml -n ${KUBERNETES_NAMESPACE}
    kubectl apply -f kubernetes/service.yaml -n ${KUBERGPT_NAMESPACE}
    kubectl apply -f kubernetes/ingress.yaml -n ${KUBERNETES_NAMESPACE}
    kubectl apply -f kubernetes/hpa.yaml -n ${KUBERNETES_NAMESPACE}
    
    # Wait for deployment
    kubectl wait --for=condition=available --timeout=300s deployment/truthgpt-deployment -n ${KUBERNETES_NAMESPACE}
    
    log_success "Kubernetes deployment completed"
}

# Deploy with Helm
deploy_helm() {
    log_info "Deploying with Helm..."
    
    # Add Helm repository
    helm repo add truthgpt https://charts.truthgpt.com
    helm repo update
    
    # Install/upgrade with Helm
    helm upgrade --install truthgpt truthgpt/truthgpt \
        --namespace ${KUBERNETES_NAMESPACE} \
        --create-namespace \
        --set image.repository=${DOCKER_REGISTRY}/truthgpt \
        --set image.tag=${TRUTHGPT_VERSION} \
        --set model.name=${MODEL_NAME} \
        --set model.numExperts=${NUM_EXPERTS} \
        --set resources.gpuCount=${GPU_COUNT} \
        --values helm/values.yaml
    
    log_success "Helm deployment completed"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Install Prometheus
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --values monitoring/prometheus-values.yaml
    
    # Install Grafana
    helm upgrade --install grafana grafana/grafana \
        --namespace monitoring \
        --create-namespace \
        --values monitoring/grafana-values.yaml
    
    # Apply TruthGPT dashboards
    kubectl apply -f monitoring/dashboards/ -n monitoring
    
    log_success "Monitoring setup completed"
}

# Setup logging
setup_logging() {
    log_info "Setting up logging..."
    
    # Install ELK stack
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace logging \
        --create-namespace \
        --values logging/elasticsearch-values.yaml
    
    helm upgrade --install kibana elastic/kibana \
        --namespace logging \
        --create-namespace \
        --values logging/kibana-values.yaml
    
    helm upgrade --install logstash elastic/logstash \
        --namespace logging \
        --create-namespace \
        --values logging/logstash-values.yaml
    
    # Install Fluentd
    kubectl apply -f logging/fluentd-config.yaml -n logging
    
    log_success "Logging setup completed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    # Unit tests
    python -m pytest tests/unit/ -v --cov=truthgpt --cov-report=html
    
    # Integration tests
    python -m pytest tests/integration/ -v
    
    # Performance tests
    python -m pytest tests/performance/ -v
    
    # Security tests
    python -m pytest tests/security/ -v
    
    log_success "All tests passed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check pods
    kubectl get pods -n ${KUBERNETES_NAMESPACE}
    
    # Check services
    kubectl get services -n ${KUBERNETES_NAMESPACE}
    
    # Check ingress
    kubectl get ingress -n ${KUBERNETES_NAMESPACE}
    
    # Test API endpoint
    SERVICE_URL=$(kubectl get service truthgpt-service -n ${KUBERNETES_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ ! -z "$SERVICE_URL" ]; then
        curl -f http://${SERVICE_URL}:8000/health || log_error "Health check failed"
    fi
    
    log_success "Health check completed"
}

# Cleanup
cleanup() {
    log_info "Cleaning up resources..."
    
    # Delete Kubernetes resources
    kubectl delete namespace ${KUBERNETES_NAMESPACE}
    
    # Delete monitoring
    kubectl delete namespace monitoring
    
    # Delete logging
    kubectl delete namespace logging
    
    log_success "Cleanup completed"
}

# Main deployment function
deploy() {
    log_info "Starting TruthGPT deployment..."
    
    check_prerequisites
    build_docker_image
    push_docker_image
    deploy_kubernetes
    setup_monitoring
    setup_logging
    run_tests
    health_check
    
    log_success "TruthGPT deployment completed successfully!"
    log_info "Access TruthGPT at: http://your-domain.com"
    log_info "Access Grafana at: http://grafana.your-domain.com"
    log_info "Access Kibana at: http://kibana.your-domain.com"
}

# Main script
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "build")
        check_prerequisites
        build_docker_image
        ;;
    "push")
        push_docker_image
        ;;
    "k8s")
        deploy_kubernetes
        ;;
    "helm")
        deploy_helm
        ;;
    "monitoring")
        setup_monitoring
        ;;
    "logging")
        setup_logging
        ;;
    "test")
        run_tests
        ;;
    "health")
        health_check
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|build|push|k8s|helm|monitoring|logging|test|health|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy     - Full deployment (default)"
        echo "  build      - Build Docker image only"
        echo "  push       - Push Docker image only"
        echo "  k8s        - Deploy to Kubernetes only"
        echo "  helm       - Deploy with Helm only"
        echo "  monitoring - Setup monitoring only"
        echo "  logging    - Setup logging only"
        echo "  test       - Run tests only"
        echo "  health     - Perform health check only"
        echo "  cleanup    - Cleanup all resources"
        exit 1
        ;;
esac


