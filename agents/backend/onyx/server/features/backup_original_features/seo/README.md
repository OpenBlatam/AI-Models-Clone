# Onyx Feature: SEO

Este módulo implementa endpoints y lógica para scraping y análisis SEO como parte de la arquitectura modular Onyx.

## Endpoints

- `POST /seo/scrape` — Realiza scraping SEO de una URL. Requiere un JSON con el campo `url`.

## Estructura
- `models.py`: Modelos Pydantic para requests y responses SEO.
- `service.py`: Lógica central de scraping y análisis (placeholder).
- `api.py`: Router FastAPI con endpoints SEO.
- `tests/`: Pruebas unitarias e integración para el feature.

## Ejemplo de request
```json
{
  "url": "https://ejemplo.com"
}
``` 