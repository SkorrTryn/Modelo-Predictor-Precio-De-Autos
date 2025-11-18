"""
app.py
Realizado por: Danny Leonardo Novoa Rodriguez
Propósito: API REST para predicción de precios de autos usados
Con entrenamiento automático si el modelo no existe
"""

import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
import os

# Cargar modelo entrenado
with open('modelo_precios_autos.pkl', 'rb') as f:
    modelo = pickle.load(f)

# Inicializar FastAPI
app = FastAPI(
    title="API Predictor de Precios de Autos Usados",
    version="2.0.0",
    description="API para predecir precios de vehículos usados con analytics integradas"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS DE DATOS ====================

class DatosVehiculo(BaseModel):
    millas: float = Field(..., description="Millaje del vehículo", ge=0, le=500000)
    anio: int = Field(..., description="Año del modelo", ge=2000, le=2030)
    
    class Config:
        json_schema_extra = {
            "example": {
                "millas": 50000,
                "anio": 2020
            }
        }

class WebhookMake(BaseModel):
    """Modelo para recibir datos desde Make"""
    tipo: str = Field(..., description="Tipo de evento: 'prediccion', 'analytics', etc.")
    datos: dict = Field(..., description="Datos del evento")

# ==================== ENDPOINTS PRINCIPALES ====================

@app.get("/")
async def raiz():
    """Endpoint raíz con información de la API"""
    return {
        "nombre": "API Predictor de Precios de Autos Usados",
        "version": "2.0.0",
        "estado": "Activo",
        "desarrollador": "Danny Leonardo Novoa Rodriguez",
        "endpoints": {
            "GET /": "Información general",
            "GET /health": "Estado del servicio",
            "POST /predecir": "Realizar predicción de precio",
            "GET /analytics/global": "Estadísticas globales del mercado",
            "GET /analytics/compare": "Comparar vehículo con el mercado",
            "POST /webhook/make": "Webhook para recibir datos de Make"
        },
        "integraciones": {
            "frontend": "Vercel",
            "automation": "Make.com",
            "chatbot": "Telegram"
        }
    }

@app.get("/health")
async def health_check():
    """Health check para Render"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "modelo_cargado": modelo is not None
    }

@app.post("/predecir")
async def predecir_precio(datos: DatosVehiculo):
    """
    Predice el precio de un vehículo basado en millaje y año
    
    Este endpoint:
    1. Valida los datos de entrada
    2. Realiza la predicción con el modelo ML
    3. Retorna el resultado
    
    Nota: El envío a Make se hace desde el frontend
    """
    try:
        # Crear DataFrame con los datos de entrada
        datos_prediccion = pd.DataFrame({
            'mileage': [datos.millas],
            'year': [datos.anio]
        })
        
        # Realizar predicción
        prediccion = modelo.predict(datos_prediccion)
        precio_estimado = float(prediccion[0])
        
        # Preparar respuesta
        respuesta = {
            "exito": True,
            "millas": datos.millas,
            "anio": datos.anio,
            "precio_estimado": round(precio_estimado, 2),
            "mensaje": "Predicción realizada exitosamente",
            "timestamp": datetime.now().isoformat()
        }
        
        return respuesta
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar predicción: {str(e)}"
        )

# ==================== ENDPOINTS DE ANALYTICS ====================

@app.get("/analytics/global")
async def analytics_global():
    """
    Retorna estadísticas globales del mercado
    
    En producción, estos datos vendrán de Google Sheets vía Make.
    Por ahora, retornamos datos calculados o mock.
    """
    try:
        #Datos mock (temporal)
        
        stats = {
            "total_predicciones": 1245,
            "anio_popular": 2020,
            "rango_millas": "40,000 - 60,000",
            "precio_promedio": 47850,
            "consultas_semana": 324,
            "ultima_actualizacion": datetime.now().isoformat(),
            "fuente": "mock_data"  # Cambiar a "make_sheets" en producción
        }
        
        # OPCIÓN B: Leer de archivo JSON (cuando Make lo genere)
        # try:
        #     with open('analytics_global.json', 'r') as f:
        #         stats = json.load(f)
        # except FileNotFoundError:
        #     stats = {...}  # Fallback a mock
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener analytics: {str(e)}"
        )

@app.get("/analytics/compare")
async def analytics_compare(anio: int, millas: float):
    """
    Compara un vehículo específico con el mercado
    
    Parámetros:
    - anio: Año del vehículo
    - millas: Millaje del vehículo
    
    Retorna comparación con promedios del mercado para ese año
    """
    try:
        # Validar parámetros
        if anio < 2000 or anio > 2030:
            raise HTTPException(status_code=400, detail="Año debe estar entre 2000 y 2030")
        if millas < 0 or millas > 500000:
            raise HTTPException(status_code=400, detail="Millas debe estar entre 0 y 500,000")
        
        # OPCIÓN A: Datos mock (temporal)
        # En producción, estos datos vendrán de Google Sheets filtrados por año
        
        # Simular cálculo de promedio para el año específico
        # (En realidad, Make calculará esto desde Google Sheets)
        promedio_precio_anio = 48320
        promedio_millas_anio = 62000
        consultas_anio = 287
        
        # Calcular percentil (simplificado)
        if millas < promedio_millas_anio:
            percentil = 65
        else:
            percentil = 35
        
        comparacion = {
            "anio": anio,
            "promedio_precio_anio": promedio_precio_anio,
            "promedio_millas_anio": promedio_millas_anio,
            "consultas_anio": consultas_anio,
            "percentil": percentil,
            "comparacion_millas": "mejor" if millas < promedio_millas_anio else "promedio",
            "ultima_actualizacion": datetime.now().isoformat(),
            "fuente": "mock_data"  # Cambiar a "make_sheets" en producción
        }
        
        # OPCIÓN B: Consultar Google Sheets via API (cuando Make lo configure)
        # import gspread
        # gc = gspread.service_account(filename='credentials.json')
        # sheet = gc.open("PredictAuto_Analytics").worksheet("data")
        # data = sheet.get_all_records()
        # filtered = [d for d in data if d['anio'] == anio]
        # promedio_precio = sum([d['precio'] for d in filtered]) / len(filtered)
        # ...
        
        return comparacion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar: {str(e)}"
        )

# ==================== WEBHOOK PARA MAKE ====================

@app.post("/webhook/make")
async def webhook_make(data: WebhookMake):
    """
    Recibe notificaciones desde Make
    
    Usos:
    - Make puede notificar cuando actualiza analytics
    - Make puede registrar eventos
    - Opcional: logging de actividad
    """
    try:
        # Log del evento (opcional)
        print(f"[Make Webhook] Tipo: {data.tipo}, Datos: {data.datos}")
        
        # Procesar según tipo de evento
        if data.tipo == "analytics_updated":
            # Make notifica que actualizó las estadísticas
            return {
                "recibido": True,
                "mensaje": "Analytics actualizadas correctamente",
                "timestamp": datetime.now().isoformat()
            }
        
        elif data.tipo == "email_sent":
            # Make notifica que envió un email
            return {
                "recibido": True,
                "mensaje": "Email confirmado",
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            # Evento desconocido pero lo aceptamos
            return {
                "recibido": True,
                "mensaje": f"Evento {data.tipo} procesado",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en webhook: {str(e)}"
        )

# ==================== ENDPOINT PARA MAKE (ALTERNATIVO) ====================

@app.post("/make/prediccion")
async def make_prediccion(datos: dict):
    """
    Endpoint simplificado para que Make capture predicciones directamente
    
    Make puede llamar a este endpoint después de cada predicción
    para almacenar datos en Google Sheets sin pasar por el frontend
    """
    try:
        required_fields = ["millas", "anio", "precio", "email"]
        for field in required_fields:
            if field not in datos:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo requerido: {field}"
                )
        
        # Simplemente confirmamos recepción
        # Make guardará estos datos en Google Sheets
        return {
            "guardado": True,
            "datos_recibidos": {
                "millas": datos["millas"],
                "anio": datos["anio"],
                "precio": datos["precio"],
                "email": datos.get("email", "no_proporcionado")
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar: {str(e)}"
        )

# ==================== SERVIDOR ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Iniciando servidor de desarrollo...")
    print("=" * 60)
    print("URL local: http://localhost:10000")
    print("Documentación: http://localhost:10000/docs")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=10000,  # Render usa 10000
        reload=False  # False en producción
    )