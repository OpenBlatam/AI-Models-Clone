# TruthGPT Troubleshooting Guide

## Common Issues and Solutions

### Performance Issues

#### Issue: High Memory Usage

**Symptoms:**
- Out of memory errors
- System slowdowns
- Frequent garbage collection

**Solutions:**

```python
# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use mixed precision training
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input)
    loss = criterion(output, target)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# Reduce batch size
train_loader = DataLoader(dataset, batch_size=16)  # Reduced from 32

# Clear cache
torch.cuda.empty_cache()
```

#### Issue: Slow Inference Speed

**Symptoms:**
- High latency
- Low throughput
- GPU underutilization

**Solutions:**

```python
# Compile model for optimal performance
compiled_model = torch.jit.script(model)
# Or use torch.compile
compiled_model = torch.compile(model)

# Use TensorRT for NVIDIA GPUs
import tensorrt as trt
model_trt = convert_to_tensorrt(model)

# Enable dynamic batching
class DynamicBatcher:
    def batch_requests(self, requests, max_batch_size=32):
        """Dynamically batch requests for optimal throughput."""
        # Implementation for dynamic batching
        pass

# Optimize K/V cache
cache_manager.enable_hierarchical_caching()
cache_manager.set_eviction_policy('LRU')
```

#### Issue: Training Instability

**Symptoms:**
- Loss not decreasing
- Gradient explosion
- NaN values in loss

**Solutions:**

```python
# Gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Learning rate scheduling
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=5
)

# Exponential moving average
from torch.optim.swa_utils import AveragedModel
swa_model = AveragedModel(model)

# Check for NaN values
for name, param in model.named_parameters():
    if torch.isnan(param).any():
        print(f"NaN found in {name}")
```

### Deployment Issues

#### Issue: Container Startup Failures

**Symptoms:**
- Container crashes on startup
- Health check failures
- Resource allocation errors

**Solutions:**

```bash
# Check container logs
docker logs truthgpt-container

# Check resource limits
kubectl describe pod truthgpt-pod

# Verify environment variables
kubectl exec truthgpt-pod -- env

# Check GPU availability
nvidia-smi
```

#### Issue: Service Unavailability

**Symptoms:**
- 503 Service Unavailable errors
- High error rates
- Pod restarts

**Solutions:**

```yaml
# Increase resource limits
resources:
  requests:
    cpu: "4"
    memory: "8Gi"
    nvidia.com/gpu: 2
  limits:
    cpu: "8"
    memory: "16Gi"
    nvidia.com/gpu: 2

# Add horizontal pod autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: truthgpt-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: truthgpt
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Security Issues

#### Issue: Unauthorized Access

**Symptoms:**
- Access denied errors
- Authentication failures
- Token expiration

**Solutions:**

```python
# Validate JWT tokens
import jwt

def validate_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256'],
            options={'verify_exp': True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# Implement rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/inference")
@limiter.limit("100/minute")
def inference(request):
    # Implementation
    pass
```

#### Issue: Data Privacy Violations

**Symptoms:**
- PII in logs
- Unencrypted data transmission
- Compliance violations

**Solutions:**

```python
# Sanitize logs
import re

def sanitize_log(log_entry):
    """Remove PII from log entries."""
    # Remove email addresses
    log_entry = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', log_entry)
    
    # Remove phone numbers
    log_entry = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', log_entry)
    
    # Remove SSN
    log_entry = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', log_entry)
    
    return log_entry

# Encrypt sensitive data
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)
    
    def decrypt(self, data: bytes) -> bytes:
        return self.cipher.decrypt(data)
```

### Model Issues

#### Issue: Poor Model Performance

**Symptoms:**
- Low accuracy
- High error rates
- Inconsistent outputs

**Solutions:**

```python
# Hyperparameter tuning
from ray import tune

def train_model(config):
    """Train model with hyperparameter tuning."""
    model = create_model(config)
    optimizer = create_optimizer(model, config)
    
    for epoch in range(config['epochs']):
        for batch in data_loader:
            loss = model(batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    return evaluate_model(model)

# Run hyperparameter search
analysis = tune.run(
    train_model,
    config={
        'learning_rate': tune.loguniform(1e-5, 1e-2),
        'batch_size': tune.choice([16, 32, 64]),
        'epochs': tune.choice([50, 100, 200])
    },
    num_samples=50
)

# Data augmentation
from torchvision import transforms

augmentation = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2)
])
```

#### Issue: Model Overfitting

**Symptoms:**
- High training accuracy, low validation accuracy
- Large gap between training and validation loss
- Poor generalization

**Solutions:**

```python
# Add regularization
model = nn.Sequential(
    nn.Linear(input_size, hidden_size),
    nn.Dropout(0.5),  # Dropout for regularization
    nn.ReLU(),
    nn.Linear(hidden_size, output_size)
)

# Weight decay
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-5  # L2 regularization
)

# Early stopping
class EarlyStopping:
    def __init__(self, patience=10, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
    
    def __call__(self, val_loss):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            return False
        else:
            self.counter += 1
            return self.counter >= self.patience

early_stopping = EarlyStopping(patience=10)
```

### API Issues

#### Issue: High API Latency

**Symptoms:**
- Slow response times
- Timeout errors
- Poor user experience

**Solutions:**

```python
# Implement caching
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class CacheManager:
    def __init__(self):
        self.redis = redis_client
    
    def get_or_compute(self, key, func, *args, **kwargs):
        """Get from cache or compute."""
        cached = self.redis.get(key)
        if cached:
            return pickle.loads(cached)
        
        result = func(*args, **kwargs)
        self.redis.setex(key, 3600, pickle.dumps(result))
        return result

# Async processing for long tasks
import asyncio
from celery import Celery

celery_app = Celery('truthgpt')

@celery_app.task
def process_long_request(data):
    """Process long-running request."""
    result = model.generate_long(data)
    return result

# Response compression
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### Issue: Rate Limiting Errors

**Symptoms:**
- 429 Too Many Requests
- API key exhausted
- Throttling errors

**Solutions:**

```python
# Implement exponential backoff
import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
        return wrapper
    return decorator

# Implement request queuing
from queue import Queue
import threading

request_queue = Queue(maxsize=100)

def process_queue():
    while True:
        request = request_queue.get()
        # Process request
        request_queue.task_done()

worker = threading.Thread(target=process_queue)
worker.start()
```

## Diagnostic Tools

### Performance Profiling

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[
        profiler.ProfilerActivity.CPU,
        profiler.ProfilerActivity.CUDA
    ],
    record_shapes=True,
    with_stack=True
) as prof:
    output = model(input)

# Print profiling results
print(prof.key_averages().table(sort_by="cuda_time_total"))
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def train_batch(model, batch):
    output = model(batch)
    loss = criterion(output, target)
    loss.backward()
    return loss
```

### System Monitoring

```python
import psutil
import GPUtil

def monitor_system():
    """Monitor system resources."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    gpu = GPUtil.getGPUs()[0]
    
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory: {memory.percent}% used ({memory.used/1e9:.2f}GB / {memory.total/1e9:.2f}GB)")
    print(f"GPU Usage: {gpu.load*100}%")
    print(f"GPU Memory: {gpu.memoryUtil*100}% used ({gpu.memoryUsed}MB / {gpu.memoryTotal}MB)")
```

## Emergency Procedures

### System Recovery

```bash
# Restart failing pods
kubectl rollout restart deployment/truthgpt

# Scale down and up
kubectl scale deployment truthgpt --replicas=0
kubectl scale deployment truthgpt --replicas=3

# Rollback to previous version
kubectl rollout undo deployment/truthgpt
```

### Data Recovery

```python
# Implement checkpointing
def save_checkpoint(model, optimizer, epoch, loss):
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss
    }
    torch.save(checkpoint, f'checkpoint_epoch_{epoch}.pt')

# Load from checkpoint
def load_checkpoint(model, optimizer, checkpoint_path):
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'], checkpoint['loss']
```

---

*This troubleshooting guide provides comprehensive solutions for common issues encountered when working with TruthGPT systems.*


