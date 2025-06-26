FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn prometheus-fastapi-instrumentator opentelemetry-instrumentation-fastapi pydantic structlog
CMD ["uvicorn", "fastapi_microservice:app", "--host", "0.0.0.0", "--port", "8080"] 