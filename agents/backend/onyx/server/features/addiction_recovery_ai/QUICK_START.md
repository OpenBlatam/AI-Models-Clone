# Quick Start Guide - Addiction Recovery AI

## 🚀 Installation

```bash
cd addiction_recovery_ai
pip install -r requirements.txt
pip install torch transformers gradio
```

## 📖 Basic Usage

### 1. Enhanced Analyzer with Deep Learning

```python
from addiction_recovery_ai import create_enhanced_analyzer

# Create analyzer
analyzer = create_enhanced_analyzer(use_gpu=True)

# Sentiment analysis
sentiment = analyzer.analyze_sentiment("I'm feeling great today!")
print(f"Sentiment: {sentiment['label']}")

# Progress prediction
features = {
    "days_sober": 30,
    "cravings_level": 3,
    "stress_level": 4,
    "support_level": 8,
    "mood_score": 7
}
progress = analyzer.predict_progress(features)
print(f"Progress: {progress:.2%}")

# Relapse risk
sequence = [{"cravings_level": 3, "stress_level": 4, "mood_score": 7, "triggers_count": 1, "consumed": 0.0}]
risk = analyzer.predict_relapse_risk(sequence)
print(f"Relapse Risk: {risk:.2%}")

# AI Coaching
coaching = analyzer.generate_coaching(
    user_situation="Feeling stressed",
    days_sober=30,
    current_challenge="Evening cravings"
)
print(f"Coaching: {coaching}")
```

### 2. Fast Analyzer (Optimized)

```python
from addiction_recovery_ai import create_fast_analyzer

# Fast analyzer with optimizations
analyzer = create_fast_analyzer(use_gpu=True)

# Same API, faster inference
progress = analyzer.predict_progress(features)
```

### 3. Launch Gradio Interface

```python
from addiction_recovery_ai import create_recovery_gradio_app, create_enhanced_analyzer

# Create analyzer
analyzer = create_enhanced_analyzer()

# Launch Gradio
app = create_recovery_gradio_app(analyzer)
app.launch(server_port=7860)
```

### 4. Train Custom Models

```python
from addiction_recovery_ai import create_progress_predictor, create_trainer
import torch.optim as optim
import torch.nn as nn

# Create model
model = create_progress_predictor(input_features=10)

# Create trainer
trainer = create_trainer(model, train_loader, val_loader)

# Train
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.BCELoss()
trainer.train(optimizer, criterion, num_epochs=10)
```

## 🎯 API Endpoints

### Start Server

```bash
python main.py
```

Server available at `http://localhost:8018`

### Key Endpoints

- `POST /recovery/assess` - Assess addiction
- `POST /recovery/create-plan` - Create recovery plan
- `POST /recovery/log-entry` - Log daily entry
- `GET /recovery/progress/{user_id}` - Get progress
- `POST /recovery/check-relapse-risk` - Check relapse risk
- `POST /recovery/coaching-session` - Get AI coaching

## 🤖 Deep Learning Features

### Sentiment Analysis
- Real-time mood tracking
- Journal entry analysis
- Batch processing

### Progress Prediction
- Multi-feature prediction
- Deep neural networks
- Customizable models

### Relapse Risk
- LSTM sequence modeling
- Early warning system
- Temporal patterns

### AI Coaching
- GPT-2 and T5 generation
- Personalized messages
- Context-aware responses

## 📊 Performance

- **Sentiment Analysis**: < 100ms
- **Progress Prediction**: < 50ms
- **Relapse Risk**: < 200ms
- **AI Coaching**: < 2s

## 🔧 Configuration

```python
# GPU acceleration
analyzer = create_enhanced_analyzer(use_gpu=True)

# Fast models
analyzer = create_fast_analyzer(use_gpu=True)

# Custom models
sentiment = create_sentiment_analyzer(model_name="custom-model")
```

## 📝 Examples

See `examples/deep_learning_example.py` for basic examples.
See `examples/fast_example.py` for speed optimizations.
See `examples/advanced_example.py` for advanced features (LoRA, ONNX, pruning, etc.).

## 🚀 Advanced Features

### LoRA Fine-tuning
```python
from addiction_recovery_ai import LoRATrainer, apply_lora_to_model

# Apply LoRA
model = apply_lora_to_model(model, rank=8, alpha=16.0)
trainer = LoRATrainer(model, train_loader, rank=8)
```

### ONNX Export
```python
from addiction_recovery_ai import export_to_onnx, ONNXRuntimeInference

# Export
export_to_onnx(model, input_shape=(1, 10), output_path="model.onnx")

# Inference
onnx_inference = ONNXRuntimeInference("model.onnx")
output = onnx_inference.predict(input_tensor)
```

### Model Pruning
```python
from addiction_recovery_ai import ModelPruner

# Prune model
pruned = ModelPruner.prune_model(model, amount=0.3)
sparsity = ModelPruner.get_sparsity(pruned)
```

### Knowledge Distillation
```python
from addiction_recovery_ai import KnowledgeDistillation, create_lightweight_student

# Create student
student = create_lightweight_student(teacher, reduction_factor=0.5)
distillation = KnowledgeDistillation(teacher, student)
```

### Enhanced Gradio Interface
```python
from addiction_recovery_ai import create_enhanced_gradio_app

# Create enhanced interface
app = create_enhanced_gradio_app(engine, engine)
app.launch(server_port=7860)
```

See `ADVANCED_IMPROVEMENTS.md` for complete documentation.

## 🎯 Extra Features

### Precomputation and Caching
```python
from addiction_recovery_ai import EmbeddingCache, FeaturePreprocessor

# Create cache
cache = EmbeddingCache(cache_dir=".cache")
preprocessor = FeaturePreprocessor(cache=cache)

# Preprocess features
features_tensor = preprocessor.preprocess_features(features_dict)
```

### Async Inference
```python
from addiction_recovery_ai import AsyncInferenceEngine
import asyncio

# Async inference
async_engine = AsyncInferenceEngine(model)
result = await async_engine.predict_async(input_tensor)
```

### Performance Profiling
```python
from addiction_recovery_ai import PerformanceProfiler, ModelProfiler

# Profile operations
profiler = PerformanceProfiler()
with profiler.profile("operation"):
    result = model(input_tensor)

stats = profiler.get_stats("operation")
```

### Model Ensembling
```python
from addiction_recovery_ai import create_ensemble

# Create ensemble
ensemble = create_ensemble([model1, model2, model3], method="mean")
prediction = ensemble.predict(input_tensor)
```

### Data Augmentation
```python
from addiction_recovery_ai import create_feature_augmentation_pipeline

# Augmentation pipeline
pipeline = create_feature_augmentation_pipeline()
augmented = pipeline(features)
```

### Advanced Logging
```python
from addiction_recovery_ai import StructuredLogger, MetricsTracker

# Structured logging
logger = StructuredLogger()
logger.info("Operation", operation="inference", time_ms=5.2)

# Metrics tracking
tracker = MetricsTracker()
tracker.log_metric("accuracy", 0.95, step=10)
```

See `EXTRA_IMPROVEMENTS.md` for complete documentation.

## 🎯 Production Features

### Hyperparameter Optimization
```python
from addiction_recovery_ai import HyperparameterOptimizer

# Auto-tune hyperparameters
optimizer = HyperparameterOptimizer(
    model_factory=model_factory,
    train_loader=train_loader,
    val_loader=val_loader,
    n_trials=50
)
best_params = optimizer.optimize()
```

### Model Versioning
```python
from addiction_recovery_ai import ModelRegistry

# Version management
registry = ModelRegistry()
registry.register(model, version="1.0.0", metadata={...})
versions = registry.list_versions()
model = registry.load_model("1.0.0", model_class)
```

### A/B Testing
```python
from addiction_recovery_ai import ABTest

# Compare models
ab_test = ABTest(model_a=current, model_b=new, split_ratio=0.5)
prediction, model_id = ab_test.predict(user_id, inputs)
stats = ab_test.get_statistics()
is_sig, p_value = ab_test.is_significant()
```

See `FINAL_IMPROVEMENTS.md` for complete documentation.

## 🎯 Ultimate Features

### Model Interpretability
```python
from addiction_recovery_ai import ModelInterpreter

# Explain predictions
interpreter = ModelInterpreter(model, background_data, feature_names)
interpreter.create_shap_explainer()
explanations = interpreter.explain_shap(instances)
importance = interpreter.get_feature_importance(instances)
```

### Continuous Learning
```python
from addiction_recovery_ai import OnlineLearner, IncrementalLearner

# Online learning
online_learner = OnlineLearner(model, optimizer, criterion)
online_learner.add_sample(inputs, targets)

# Incremental learning
incremental = IncrementalLearner(model)
incremental.learn(new_data, epochs=1)
```

### AutoML
```python
from addiction_recovery_ai import AutoML

# Automatic model selection
automl = AutoML(train_loader, val_loader)
results = automl.auto_train(input_size=10, max_time=3600)
best_model = results["model"]
```

See `ULTIMATE_IMPROVEMENTS.md` for complete documentation.

## 🔒 Security & Advanced Compression

### Advanced Compression
```python
from addiction_recovery_ai import AdvancedQuantization, ModelCompressor

# Static quantization
quantized = AdvancedQuantization.quantize_static(
    model, calibration_data, backend="fbgemm"
)

# Quantization-Aware Training
qat_model = AdvancedQuantization.quantize_qat(model, train_loader)

# SVD compression
compressed = ModelCompressor.compress_with_svd(model, compression_ratio=0.5)
```

### Security Features
```python
from addiction_recovery_ai import APIKeyManager, InputSanitizer, SecurityRateLimiter

# API key management
key_manager = APIKeyManager()
api_key = key_manager.generate_key(user_id="user123")
is_valid, key_info = key_manager.validate_key(api_key)

# Input sanitization
sanitizer = InputSanitizer()
is_valid, sanitized = sanitizer.sanitize_tensor(tensor, max_size=10000)

# Rate limiting with security
rate_limiter = SecurityRateLimiter(max_requests=100, window=60.0)
is_allowed, reason = rate_limiter.is_allowed(identifier="user123")
```

See `COMPLETE_SUMMARY.md` for complete feature list.

## ⚙️ Configuration & Testing

### Configuration Management
```python
from addiction_recovery_ai import ConfigManager, load_config

# Load configuration
config = load_config("config.yaml")

# Get values
use_gpu = config.get("model.use_gpu", True)
batch_size = config.get("model.batch_size", 32)

# Set values
config.set("model.use_gpu", False)
config.save("config.yaml")
```

### Testing
```python
# Run tests
pytest tests/test_models.py -v

# Test specific model
pytest tests/test_models.py::TestProgressPredictor -v
```

### Deployment
```bash
# Deploy model
python scripts/deploy.py --model-type progress --version 1.0.0

# Deploy with options
python scripts/deploy.py --model-type relapse --version 1.0.0 --no-optimize
```

### Metrics Dashboard
```python
from addiction_recovery_ai import MetricsDashboard, PerformanceTracker

# Metrics dashboard
dashboard = MetricsDashboard()
dashboard.record_metric("latency", 5.2)
dashboard.record_metric("accuracy", 0.95)
stats = dashboard.get_metric_stats("latency", window=3600)

# Performance tracking
tracker = PerformanceTracker()
tracker.start_operation("inference")
result = model(input_tensor)
elapsed = tracker.end_operation("inference")
```

### Model Utilities
```python
from addiction_recovery_ai import (
    count_parameters, get_model_size, freeze_model,
    compare_models, save_model_checkpoint
)

# Count parameters
params = count_parameters(model)
print(f"Total: {params['total']:,}, Trainable: {params['trainable']:,}")

# Get model size
size = get_model_size(model, unit="MB")
print(f"Model size: {size:.2f} MB")

# Freeze model
freeze_model(model, freeze=True)

# Compare models
comparison = compare_models(model1, model2)

# Save checkpoint
save_model_checkpoint(model, "checkpoint.pth", optimizer, epoch=10)
```

### Experiment Tracking
```python
from addiction_recovery_ai import ExperimentTracker, ExperimentTrainingLogger

# Experiment tracking
tracker = ExperimentTracker("experiment_1", use_tensorboard=True, use_wandb=True)
tracker.log_metric("accuracy", 0.95, step=10)
tracker.log_metrics({"loss": 0.05, "f1": 0.92}, step=10)
tracker.log_hparams({"lr": 0.001, "batch_size": 32}, {"accuracy": 0.95})

# Training logger
train_logger = ExperimentTrainingLogger("training_run", use_tensorboard=True)
train_logger.log_epoch(epoch=1, train_loss=0.05, val_loss=0.06, accuracy=0.95)
```

### Visualization
```python
from addiction_recovery_ai import ModelVisualizer, ProgressVisualizer

# Model visualization
visualizer = ModelVisualizer()
visualizer.plot_training_curves(train_losses, val_losses, "training.png")
visualizer.plot_feature_importance(feature_names, importances, "importance.png")

# Progress visualization
progress_viz = ProgressVisualizer()
progress_viz.plot_progress_timeline(dates, progress_scores, "progress.png")
```

### Data Pipeline
```python
from addiction_recovery_ai import RecoveryDataset, DataPipeline, DataAugmentationPipeline

# Create dataset
dataset = RecoveryDataset(features_list, targets_list)

# Create optimized pipeline
pipeline = DataPipeline(batch_size=32, num_workers=4, pin_memory=True)
loader = pipeline.create_loader(dataset)

# With augmentation
augmentation = DataAugmentationPipeline(augmentation_prob=0.5)
augmented_dataset = RecoveryDataset(features_list, targets_list, transform=augmentation)
```

### Real-time Streaming
```python
from addiction_recovery_ai import RealTimePredictor
import asyncio

# Real-time prediction
predictor = RealTimePredictor(model)
await predictor.start()

# Async prediction
result = await predictor.predict(input_tensor)
```

### Distributed Inference
```python
from addiction_recovery_ai import DistributedInference

# Multi-GPU inference
distributed = DistributedInference(model, device_ids=[0, 1, 2, 3])
results = distributed.predict_batch(inputs, batch_size_per_gpu=8)
```

### REST API
```python
# Start REST API server
from addiction_recovery_ai.api.rest_api import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8018)

# API endpoints:
# POST /predict/progress - Predict progress
# POST /predict/relapse-risk - Predict relapse risk
# POST /analyze/sentiment - Analyze sentiment
# POST /predict/batch - Batch prediction
# GET /health - Health check
```

### WebSocket API
```python
# Start WebSocket server
from addiction_recovery_ai.api.websocket_api import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8019)

# WebSocket endpoint: ws://localhost:8019/ws
# Message types: predict_progress, analyze_sentiment, ping
```

### Advanced Caching
```python
from addiction_recovery_ai import LRUCache, PersistentCache, CacheDecorator

# LRU Cache with TTL
cache = LRUCache(maxsize=1000, ttl=3600.0)
cache.set("key", value)
value = cache.get("key")

# Persistent cache
persistent = PersistentCache(cache_dir=".cache", maxsize=10000)
persistent.set("key", value)

# Cache decorator
@CacheDecorator(cache)
def expensive_function(x, y):
    return x + y
```

### Multi-Tenant Support
```python
from addiction_recovery_ai import TenantManager, TenantIsolation

# Tenant management
tenant_manager = TenantManager()
tenant_manager.register_tenant("tenant1", config={"model_type": "custom"})

# Tenant isolation
isolation = TenantIsolation(tenant_manager)
result = isolation.predict_for_tenant("tenant1", features)

# Tenant statistics
stats = tenant_manager.get_tenant_stats("tenant1")
```

### Backup & Recovery
```python
from addiction_recovery_ai import ModelBackup, DataBackup

# Model backup
backup = ModelBackup(backup_dir="backups")
backup_path = backup.backup_model(model, "progress_model", metadata={...})

# List backups
backups = backup.list_backups("progress_model")

# Restore model
restored = backup.restore_model("progress_model_20240101_120000", model_class)

# Data backup
data_backup = DataBackup()
data_path = data_backup.backup_data(data, "training_data")
restored_data = data_backup.restore_data("training_data_20240101_120000")
```

### Advanced Monitoring
```python
from addiction_recovery_ai import SystemMonitor, PerformanceMonitor

# System monitoring
monitor = SystemMonitor()
monitor.record_metric("latency", 5.2)
monitor.record_metric("throughput", 100.5)
dashboard_data = monitor.get_dashboard_data(time_window=3600)

# Performance monitoring
perf_monitor = PerformanceMonitor()
perf_monitor.record_operation("inference", duration_ms=5.2, success=True)
report = perf_monitor.get_performance_report()
```

### Error Recovery
```python
from addiction_recovery_ai import CircuitBreaker, RetryHandler, GracefulDegradation

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
result = breaker.call(model.predict, inputs)

# Retry handler
retry = RetryHandler(max_retries=3, initial_delay=1.0)
result = retry.retry(model.predict, inputs)

# Graceful degradation
degradation = GracefulDegradation(fallback_model=simple_model)
result = degradation.predict_with_fallback(primary_model, inputs)
```

### Advanced Analytics
```python
from addiction_recovery_ai import RecoveryAnalytics, CohortAnalysis

# Recovery analytics
analytics = RecoveryAnalytics()
analytics.add_data_point(user_id, timestamp, features, prediction)
trends = analytics.calculate_trends(user_id, metric="progress", days=30)
patterns = analytics.detect_patterns(user_id)
insights = analytics.generate_insights(user_id)

# Cohort analysis
cohorts = CohortAnalysis()
cohorts.add_to_cohort("cohort1", user_id, {"progress": 0.8})
analysis = cohorts.analyze_cohort("cohort1")
comparison = cohorts.compare_cohorts("cohort1", "cohort2")
```

### Notifications
```python
from addiction_recovery_ai import NotificationManager, NotificationLevel, AlertSystem

# Notification system
notifier = NotificationManager()
notifier.send_notification(
    "High Risk Detected",
    "User shows high relapse risk",
    level=NotificationLevel.WARNING
)

# Alert system
alerts = AlertSystem(notifier)
alerts.add_alert_rule(
    condition=lambda ctx: ctx.get("risk", 0) > 0.7,
    title="High Risk Alert",
    message="Relapse risk exceeds threshold",
    level=NotificationLevel.CRITICAL
)
```

### External Integration
```python
from addiction_recovery_ai import ExternalAPIClient, WebhookHandler, DataExporter

# External API
client = ExternalAPIClient("https://api.example.com", api_key="key")
data = client.get("/endpoint")

# Webhooks
webhooks = WebhookHandler()
webhooks.register_webhook("high_risk", "https://webhook.url")
webhooks.trigger_webhook("high_risk", {"user_id": "123", "risk": 0.8})

# Data export
exporter = DataExporter()
exporter.export_to_json(data, "export.json")
exporter.export_to_csv(data, "export.csv")
```

### Load Balancing
```python
from addiction_recovery_ai import LoadBalancer, ModelPool

# Load balancer
models = [model1, model2, model3]
balancer = LoadBalancer(models, strategy="round_robin")
model = balancer.get_model()
stats = balancer.get_stats()

# Model pool
def create_model():
    return YourModel()

pool = ModelPool(create_model, pool_size=4)
output = pool.predict(inputs)
pool_stats = pool.get_stats()
```

### Feature Store
```python
from addiction_recovery_ai import FeatureStore, EmbeddingStore

# Feature store
store = FeatureStore("feature_store")
store.store_features("user_123", {"cravings": 0.5, "stress": 0.3})
features = store.get_features("user_123")
history = store.get_feature_history("user_123", days=30)

# Embedding store
embed_store = EmbeddingStore("embedding_store")
embed_store.store_embedding("user_123", embedding_tensor)
embedding = embed_store.get_embedding("user_123")
similar = embed_store.search_similar(query_embedding, top_k=10)
```

### Task Scheduling
```python
from addiction_recovery_ai import TaskScheduler, ModelUpdateScheduler

# Task scheduler
scheduler = TaskScheduler()
scheduler.schedule_task(
    "daily_check",
    check_function,
    schedule_type="daily",
    time="09:00"
)
scheduler.start()

# Model update scheduler
update_scheduler = ModelUpdateScheduler(scheduler)
update_scheduler.schedule_model_update(
    "model_1",
    update_function,
    interval_hours=24
)
```

### GraphQL API
```python
from addiction_recovery_ai import GraphQLAPI

# GraphQL API
graphql = GraphQLAPI(analyzer=analyzer)

query = """
{
    analyze(text: "I'm feeling better today") {
        risk
        progress
        recommendations
    }
}
"""

result = graphql.execute(query)
```

### Message Queue & Event Streaming
```python
from addiction_recovery_ai import MessageQueue, EventStream

# Message queue
mq = MessageQueue()
mq.subscribe("high_risk", lambda msg: handle_risk(msg))
mq.publish("high_risk", {"user_id": "123", "risk": 0.8})
mq.start()

# Event streaming
stream = EventStream()
stream.on(lambda event: print(f"Event: {event['type']}"))
stream.emit("user_progress", {"user_id": "123", "progress": 0.75})
```

### API Versioning
```python
from addiction_recovery_ai import APIVersion, VersionRouter, versioned

# API versioning
api_version = APIVersion()
api_version.register_endpoint("v1", "/analyze", v1_analyze_handler)
api_version.register_endpoint("v2", "/analyze", v2_analyze_handler)

# Version router
router = VersionRouter(api_version)
result = router.route("v2", "/analyze", text="sample")

# Versioned decorator
@versioned("v2")
def analyze_v2(text: str):
    return {"result": "v2 analysis"}
```

### Service Discovery
```python
from addiction_recovery_ai import ServiceRegistry, ServiceDiscovery

# Service registry
registry = ServiceRegistry()
registry.register_service("model_service", "http://localhost:8000")
registry.register_service("analytics_service", "http://localhost:8001")

# Service discovery
discovery = ServiceDiscovery(registry)
service = discovery.discover_service("model_service", healthy_only=True)
all_services = discovery.discover_all_services()
```

### Performance Benchmarking
```python
from addiction_recovery_ai import Benchmark, ModelBenchmark

# General benchmarking
benchmark = Benchmark()
result = benchmark.measure("analyze", analyzer.analyze, "sample text", iterations=100)
comparison = benchmark.compare(["analyze_v1", "analyze_v2"])

# Model benchmarking
model_bench = ModelBenchmark(device=torch.device("cuda"))
inference_stats = model_bench.benchmark_inference(model, (32, 10), iterations=100)
training_stats = model_bench.benchmark_training_step(model, (32, 10), iterations=50)
```

### Advanced Testing
```python
from addiction_recovery_ai import ModelTester, DataTester, MockFactory

# Model testing
tester = ModelTester()
forward_test = tester.test_forward_pass(model, (32, 10))
gradient_test = tester.test_gradient_flow(model, (32, 10))
batch_tests = tester.test_batch_sizes(model, (10,), [1, 8, 16, 32])

# Data testing
data_tester = DataTester()
consistency = data_tester.test_data_consistency(data, ["user_id", "text"])
type_check = data_tester.test_data_types(data, {"user_id": str, "risk": float})

# Mock factory
mock_model = MockFactory.create_model_mock()
mock_analyzer = MockFactory.create_analyzer_mock()
```

### Documentation Generation
```python
from addiction_recovery_ai import DocumentationGenerator

# Documentation generator
doc_gen = DocumentationGenerator()

# Generate class documentation
class_doc = doc_gen.generate_class_doc(AddictionAnalyzer)

# Generate function documentation
func_doc = doc_gen.generate_function_doc(analyzer.analyze)

# Generate module documentation
module_doc = doc_gen.generate_module_doc(module)

# Generate API documentation
api_doc = doc_gen.generate_api_doc([module1, module2])
```

### Resource Management
```python
from addiction_recovery_ai import ResourceMonitor, MemoryManager, ResourceLimiter

# Resource monitoring
monitor = ResourceMonitor()
monitor.start_monitoring(interval=1.0)
current_stats = monitor.get_current_stats()
avg_stats = monitor.get_average_stats()
monitor.stop_monitoring()

# Memory management
MemoryManager.clear_cache()
usage = MemoryManager.get_memory_usage()
MemoryManager.optimize_memory()

# Resource limiting
limiter = ResourceLimiter(
    max_cpu_percent=80.0,
    max_memory_percent=80.0,
    max_gpu_memory_gb=8.0
)
status = limiter.check_limits()
limiter.wait_if_needed()
```

### Advanced Configuration
```python
from addiction_recovery_ai import ConfigManager, ModelConfig, TrainingConfig

# Configuration manager
config_mgr = ConfigManager("config")
config = config_mgr.load_config("model_config")
config_mgr.save_config("model_config", config, format="yaml")
config_mgr.update_config("model_config", {"learning_rate": 0.0001})

# Load from environment
env_config = config_mgr.load_from_env(prefix="RECOVERY_AI_")

# Merge configurations
merged = config_mgr.merge_configs(base_config, override_config)

# Dataclass configs
model_cfg = ModelConfig(
    model_name="recovery_model",
    model_type="lstm",
    input_size=10,
    hidden_size=64,
    num_layers=2
)
training_cfg = TrainingConfig(
    optimizer="adam",
    learning_rate=0.001,
    batch_size=32
)
```

### Advanced Pipeline
```python
from addiction_recovery_ai import ProcessingPipeline, PipelineStage, BatchProcessor

# Processing pipeline
pipeline = ProcessingPipeline()
pipeline.add_stage("normalize", normalize_function)
pipeline.add_stage("encode", encode_function)
pipeline.add_stage("augment", augment_function)

# Process data
processed = pipeline.process(data)
batch_processed = pipeline.process_batch(batch)

# Enable/disable stages
pipeline.disable_stage("augment")
pipeline.enable_stage("augment")

# Batch processor
batch_processor = BatchProcessor(batch_size=32, max_workers=4)
results = batch_processor.process(data, processor_function)

# Streaming processing
stream_results = batch_processor.process_streaming(data_stream, processor_function)
```

### Session Management
```python
from addiction_recovery_ai import SessionManager, Session

# Session manager
session_mgr = SessionManager(default_timeout_minutes=30)
session_id = session_mgr.create_session("user_123", metadata={"ip": "127.0.0.1"})

# Get and update session
session = session_mgr.get_session(session_id)
session_mgr.update_session(session_id, data={"last_analysis": "2024-01-01"})

# Get user sessions
user_sessions = session_mgr.get_user_sessions("user_123")

# Cleanup expired sessions
session_mgr.cleanup_expired()

# Get statistics
stats = session_mgr.get_stats()
```

### Advanced Logging
```python
from addiction_recovery_ai import StructuredLogger, JSONFormatter, LogAggregator

# Structured logger
logger = StructuredLogger("recovery_ai", use_json=True, log_file="app.log")
logger.set_context(user_id="123", request_id="req_456")
logger.info("Analysis completed", risk=0.5, progress=0.75)
logger.clear_context()

# Log aggregator
aggregator = LogAggregator()
aggregator.add_log({"level": "INFO", "message": "Event occurred"})
logs = aggregator.get_logs(level="INFO", limit=100)
```

### Advanced Rate Limiting
```python
from addiction_recovery_ai import AdvancedRateLimiter, TokenBucket, SlidingWindowLimiter

# Token bucket limiter
limiter = AdvancedRateLimiter(
    strategy="token_bucket",
    capacity=100,
    refill_rate=10.0
)
allowed, wait_time = limiter.is_allowed("user_123")

# Sliding window limiter
window_limiter = AdvancedRateLimiter(
    strategy="sliding_window",
    max_requests=100,
    window_seconds=60.0
)
allowed, wait_time = window_limiter.is_allowed("user_123")

# Get statistics
stats = limiter.get_stats()
```

## ⚠️ Important

This system is a support tool and **does NOT replace** professional medical advice. Always consult healthcare professionals for severe addiction cases.

