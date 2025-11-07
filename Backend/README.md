---
title: Predictor Precios Autos
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Predictor de Precios de Autos Usados

API REST para predecir precios de vehículos usados basado en Machine Learning.

## Endpoints

- `GET /`: Información general de la API
- `GET /health`: Estado del servicio
- `POST /predecir`: Realizar predicción

## Ejemplo de uso
```bash
curl -X POST https://tu-usuario-predictor-autos.hf.space/predecir \
  -H "Content-Type: application/json" \
  -d '{"millas": 50000, "anio": 2020}'
```

## Tecnologías

- Python 3.11
- FastAPI
- scikit-learn
- pandas
- uvicorn

## Desarrollado por

Danny Leonardo Novoa Rodriguez





