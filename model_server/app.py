from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import List

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from model_server.config import ServerConfig, ModelConfig, BatchConfig
from src.models.mlp_classifier import MLPClassifier


server_cfg = ServerConfig()
model_cfg = ModelConfig()
batch_cfg = BatchConfig()

app = FastAPI(title="MLPClassifier Inference API", version="1.0.0")


class PredictRequest(BaseModel):
    inputs: List[List[float]] = Field(..., description="Batch of feature vectors")


class PredictResponse(BaseModel):
    logits: List[List[float]]
    probabilities: List[List[float]]


def load_model() -> torch.nn.Module:
    device = torch.device(model_cfg.device)
    model = MLPClassifier(model_cfg.input_dim, list(model_cfg.hidden_dims), model_cfg.num_classes, model_cfg.dropout)
    model.eval()
    model.to(device)
    if model_cfg.checkpoint_path:
        state = torch.load(model_cfg.checkpoint_path, map_location=device)
        if "model" in state:
            model.load_state_dict(state["model"])  # type: ignore[arg-type]
        else:
            model.load_state_dict(state)  # type: ignore[arg-type]
    return model


model = load_model()
device = next(model.parameters()).device


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "server": asdict(server_cfg)}


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    if not req.inputs:
        raise HTTPException(status_code=400, detail="Empty inputs")
    with torch.no_grad(), torch.cuda.amp.autocast(enabled=(model_cfg.amp and device.type == "cuda")):
        x = torch.tensor(req.inputs, dtype=torch.float32, device=device)
        logits = model(x)
        probs = torch.softmax(logits, dim=-1)
    return PredictResponse(
        logits=logits.detach().cpu().tolist(),
        probabilities=probs.detach().cpu().tolist(),
    )



