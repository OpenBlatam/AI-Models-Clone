"""
API de inferencia LLM con recarga automática del modelo fine-tuneado
- FastAPI + Transformers
- Soporte batch y control de parámetros de generación
- Validación de entrada/salida con Pydantic
- Endpoints /health y /version
- Recarga en background cada 10 segundos
- Uso de GPU si está disponible
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import time
import threading
import logging

MODEL_PATH = './fine_tuned_model'
CHECK_INTERVAL = 10  # segundos

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
app = FastAPI()
model = None
tokenizer = None
last_loaded = 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="Prompt de entrada")
    max_new_tokens: int = Field(32, ge=1, le=512)
    temperature: float = Field(1.0, ge=0.0, le=2.0)
    top_p: float = Field(1.0, ge=0.0, le=1.0)

class BatchGenerationRequest(BaseModel):
    prompts: List[str]
    max_new_tokens: int = 32
    temperature: float = 1.0
    top_p: float = 1.0

class GenerationResponse(BaseModel):
    result: str

class BatchGenerationResponse(BaseModel):
    results: List[str]

def get_model_mtime():
    try:
        return max(
            os.path.getmtime(os.path.join(MODEL_PATH, f))
            for f in os.listdir(MODEL_PATH)
            if f.endswith('.bin') or f.endswith('.json') or f.endswith('.txt')
        )
    except Exception:
        return 0

def load_model():
    global model, tokenizer, last_loaded
    logging.info("Cargando modelo...")
    model_ = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
    tokenizer_ = AutoTokenizer.from_pretrained(MODEL_PATH)
    model_.to(device)
    model_.eval()
    last_loaded = get_model_mtime()
    logging.info("Modelo cargado.")
    return model_, tokenizer_

def maybe_reload_model():
    global model, tokenizer, last_loaded
    try:
        mtime = get_model_mtime()
        if mtime > last_loaded or model is None or tokenizer is None:
            m, t = load_model()
            model, tokenizer = m, t
            last_loaded = mtime
    except Exception as e:
        logging.error(f"Error comprobando recarga de modelo: {e}")

def background_reloader():
    while True:
        maybe_reload_model()
        time.sleep(CHECK_INTERVAL)

@app.on_event("startup")
def startup_event():
    global model, tokenizer
    model, tokenizer = load_model()
    threading.Thread(target=background_reloader, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"model_path": MODEL_PATH, "last_loaded": last_loaded}

@app.post("/predict", response_model=GenerationResponse)
async def predict(req: GenerationRequest):
    try:
        maybe_reload_model()
        inputs = tokenizer(req.prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=req.max_new_tokens,
                temperature=req.temperature,
                top_p=req.top_p,
                do_sample=True
            )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"result": result}
    except Exception as e:
        logging.error(f"Error en inferencia: {e}")
        return {"result": f"Error: {str(e)}"}

@app.post("/batch_predict", response_model=BatchGenerationResponse)
async def batch_predict(req: BatchGenerationRequest):
    try:
        maybe_reload_model()
        results = []
        for prompt in req.prompts:
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=req.max_new_tokens,
                    temperature=req.temperature,
                    top_p=req.top_p,
                    do_sample=True
                )
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            results.append(result)
        return {"results": results}
    except Exception as e:
        logging.error(f"Error en batch inferencia: {e}")
        return {"results": [f"Error: {str(e)}"]}

"""
# Ejemplo de uso:
# uvicorn agents.backend.onyx.server.features.utils.llm_inference_api:app --host 0.0.0.0 --port 8000
# POST /predict {"prompt": "¿Cuál es la capital de Francia?", "max_new_tokens": 32}
# POST /batch_predict {"prompts": ["Hola", "Adiós"]}
""" 