"""
TruthGPT API Server
===================

REST API server for TruthGPT API using FastAPI.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import numpy as np
import torch
import json
import uuid
import traceback

# Import TruthGPT API
import truthgpt as tg

# Create FastAPI app
app = FastAPI(
    title="TruthGPT API",
    description="REST API for TruthGPT - TensorFlow-like interface for neural networks",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store models in memory (in production, use a database)
models_store: Dict[str, Any] = {}

# Pydantic models for request/response
class LayerConfig(BaseModel):
    type: str
    params: Dict[str, Any]

class CreateModelRequest(BaseModel):
    layers: List[LayerConfig]
    name: Optional[str] = None

class CompileModelRequest(BaseModel):
    optimizer: str
    optimizer_params: Optional[Dict[str, Any]] = {}
    loss: str
    loss_params: Optional[Dict[str, Any]] = {}
    metrics: Optional[List[str]] = []

class TrainRequest(BaseModel):
    x_train: List[List[float]]
    y_train: List[Union[int, float]]
    epochs: int = 1
    batch_size: int = 32
    validation_data: Optional[Dict[str, List[List[float]]]] = None
    verbose: int = 1

class EvaluateRequest(BaseModel):
    x_test: List[List[float]]
    y_test: List[Union[int, float]]
    verbose: int = 0

class PredictRequest(BaseModel):
    x: List[List[float]]
    verbose: int = 0

# Helper functions
def create_layer_from_config(config: LayerConfig):
    """Create a layer from configuration."""
    layer_type = config.type.lower()
    params = config.params
    
    if layer_type == "dense":
        return tg.layers.Dense(**params)
    elif layer_type == "conv2d":
        return tg.layers.Conv2D(**params)
    elif layer_type == "lstm":
        return tg.layers.LSTM(**params)
    elif layer_type == "gru":
        return tg.layers.GRU(**params)
    elif layer_type == "dropout":
        return tg.layers.Dropout(**params)
    elif layer_type == "batchnormalization":
        return tg.layers.BatchNormalization(**params)
    elif layer_type == "maxpooling2d":
        return tg.layers.MaxPooling2D(**params)
    elif layer_type == "averagepooling2d":
        return tg.layers.AveragePooling2D(**params)
    elif layer_type == "flatten":
        return tg.layers.Flatten(**params)
    elif layer_type == "reshape":
        return tg.layers.Reshape(**params)
    elif layer_type == "embedding":
        return tg.layers.Embedding(**params)
    else:
        raise ValueError(f"Unknown layer type: {layer_type}")

def create_optimizer_from_config(optimizer: str, params: Dict[str, Any]):
    """Create an optimizer from configuration."""
    opt_type = optimizer.lower()
    
    if opt_type == "adam":
        return tg.optimizers.Adam(**params)
    elif opt_type == "sgd":
        return tg.optimizers.SGD(**params)
    elif opt_type == "rmsprop":
        return tg.optimizers.RMSprop(**params)
    elif opt_type == "adagrad":
        return tg.optimizers.Adagrad(**params)
    elif opt_type == "adamw":
        return tg.optimizers.AdamW(**params)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer}")

def create_loss_from_config(loss: str, params: Dict[str, Any]):
    """Create a loss function from configuration."""
    loss_type = loss.lower()
    
    if loss_type == "sparsecategoricalcrossentropy":
        return tg.losses.SparseCategoricalCrossentropy(**params)
    elif loss_type == "categoricalcrossentropy":
        return tg.losses.CategoricalCrossentropy(**params)
    elif loss_type == "binarycrossentropy":
        return tg.losses.BinaryCrossentropy(**params)
    elif loss_type == "meansquarederror" or loss_type == "mse":
        return tg.losses.MeanSquaredError(**params)
    elif loss_type == "meanabsoluteerror" or loss_type == "mae":
        return tg.losses.MeanAbsoluteError(**params)
    else:
        raise ValueError(f"Unknown loss function: {loss}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TruthGPT API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "device": str(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
    }

@app.post("/models/create")
async def create_model(request: CreateModelRequest):
    """Create a new model."""
    try:
        # Create layers
        layers = []
        for layer_config in request.layers:
            layer = create_layer_from_config(layer_config)
            layers.append(layer)
        
        # Create model
        model = tg.Sequential(layers, name=request.name)
        
        # Generate model ID
        model_id = str(uuid.uuid4())
        models_store[model_id] = {
            "model": model,
            "compiled": False,
            "name": request.name or f"Model_{model_id[:8]}"
        }
        
        return {
            "model_id": model_id,
            "name": models_store[model_id]["name"],
            "status": "created",
            "message": "Model created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating model: {str(e)}")

@app.post("/models/{model_id}/compile")
async def compile_model(model_id: str, request: CompileModelRequest):
    """Compile a model."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        model = models_store[model_id]["model"]
        
        # Create optimizer
        optimizer = create_optimizer_from_config(
            request.optimizer,
            request.optimizer_params or {}
        )
        
        # Create loss
        loss = create_loss_from_config(
            request.loss,
            request.loss_params or {}
        )
        
        # Compile model
        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=request.metrics or []
        )
        
        models_store[model_id]["compiled"] = True
        
        return {
            "model_id": model_id,
            "status": "compiled",
            "message": "Model compiled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error compiling model: {str(e)}")

@app.post("/models/{model_id}/train")
async def train_model(model_id: str, request: TrainRequest):
    """Train a model."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not models_store[model_id]["compiled"]:
        raise HTTPException(status_code=400, detail="Model must be compiled before training")
    
    try:
        model = models_store[model_id]["model"]
        
        # Convert to numpy arrays
        x_train = np.array(request.x_train, dtype=np.float32)
        y_train = np.array(request.y_train, dtype=np.int64 if isinstance(request.y_train[0], int) else np.float32)
        
        # Prepare validation data if provided
        validation_data = None
        if request.validation_data:
            x_val = np.array(request.validation_data.get("x", []), dtype=np.float32)
            y_val = np.array(request.validation_data.get("y", []), dtype=np.int64 if isinstance(request.validation_data["y"][0], int) else np.float32)
            validation_data = (x_val, y_val)
        
        # Train model
        history = model.fit(
            x_train, y_train,
            epochs=request.epochs,
            batch_size=request.batch_size,
            validation_data=validation_data,
            verbose=request.verbose
        )
        
        # Convert history to serializable format
        history_serializable = {}
        for key, value in history.items():
            if isinstance(value, list):
                history_serializable[key] = [float(v) if isinstance(v, (int, float, torch.Tensor)) else v for v in value]
            else:
                history_serializable[key] = float(value) if isinstance(value, (int, float, torch.Tensor)) else value
        
        return {
            "model_id": model_id,
            "status": "trained",
            "history": history_serializable,
            "message": "Model trained successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error training model: {str(e)}\n{traceback.format_exc()}")

@app.post("/models/{model_id}/evaluate")
async def evaluate_model(model_id: str, request: EvaluateRequest):
    """Evaluate a model."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not models_store[model_id]["compiled"]:
        raise HTTPException(status_code=400, detail="Model must be compiled before evaluation")
    
    try:
        model = models_store[model_id]["model"]
        
        # Convert to numpy arrays
        x_test = np.array(request.x_test, dtype=np.float32)
        y_test = np.array(request.y_test, dtype=np.int64 if isinstance(request.y_test[0], int) else np.float32)
        
        # Evaluate model
        results = model.evaluate(x_test, y_test, verbose=request.verbose)
        
        # Convert results to serializable format
        if isinstance(results, tuple):
            results_dict = {
                "loss": float(results[0]),
                "metrics": [float(r) for r in results[1:]]
            }
        else:
            results_dict = {"results": float(results)}
        
        return {
            "model_id": model_id,
            "status": "evaluated",
            "results": results_dict,
            "message": "Model evaluated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error evaluating model: {str(e)}\n{traceback.format_exc()}")

@app.post("/models/{model_id}/predict")
async def predict(model_id: str, request: PredictRequest):
    """Make predictions with a model."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        model = models_store[model_id]["model"]
        
        # Convert to numpy array
        x = np.array(request.x, dtype=np.float32)
        
        # Make predictions
        predictions = model.predict(x, verbose=request.verbose)
        
        # Convert predictions to list
        if isinstance(predictions, torch.Tensor):
            predictions = predictions.cpu().numpy().tolist()
        elif isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()
        
        return {
            "model_id": model_id,
            "status": "predicted",
            "predictions": predictions,
            "message": "Predictions generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error making predictions: {str(e)}\n{traceback.format_exc()}")

@app.get("/models")
async def list_models():
    """List all models."""
    models_list = []
    for model_id, model_data in models_store.items():
        models_list.append({
            "model_id": model_id,
            "name": model_data["name"],
            "compiled": model_data["compiled"]
        })
    
    return {
        "models": models_list,
        "count": len(models_list)
    }

@app.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """Get model information."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_data = models_store[model_id]
    return {
        "model_id": model_id,
        "name": model_data["name"],
        "compiled": model_data["compiled"]
    }

@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    del models_store[model_id]
    
    return {
        "model_id": model_id,
        "status": "deleted",
        "message": "Model deleted successfully"
    }

@app.post("/models/{model_id}/save")
async def save_model(model_id: str, filepath: Optional[str] = None):
    """Save a model to disk."""
    if model_id not in models_store:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        model = models_store[model_id]["model"]
        
        if not filepath:
            filepath = f"models/{model_id}.pth"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        
        # Save model
        model.save(filepath)
        
        return {
            "model_id": model_id,
            "filepath": filepath,
            "status": "saved",
            "message": "Model saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving model: {str(e)}")

@app.post("/models/load")
async def load_model(filepath: str, model_id: Optional[str] = None):
    """Load a model from disk."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Model file not found")
    
    try:
        # Load model
        model = tg.load_model(filepath, model_class=tg.Sequential)
        
        # Generate model ID if not provided
        if not model_id:
            model_id = str(uuid.uuid4())
        
        models_store[model_id] = {
            "model": model,
            "compiled": hasattr(model, '_compiled') and model._compiled,
            "name": f"Loaded_{model_id[:8]}"
        }
        
        return {
            "model_id": model_id,
            "filepath": filepath,
            "status": "loaded",
            "message": "Model loaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error loading model: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)











