
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import pickle
import os
from typing import Optional


#Configuración de la app FastAPI

app = FastAPI(
    title="Predictor de Precios de Autos Usados",
    description="API para predecir precios de vehiculos basado en millaje y año del modelo",
    version="1.0.0",
    docs_url="/docs",           # Documentación interactiva en /docs
    redoc_url="/redoc"          # Documentación alternativa en /redoc
)


# CONFIGURACIÓN DE CORS (para conectar con frontend)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # En producción, especifica tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],        # Permite GET, POST, etc.
    allow_headers=["*"],        # Permite todos los headers
)


#Cargar el modelo antes de iniciar la app

modelo = None
modelo_path = "modelo_precios.pkl"

@app.on_event("startup")
async def cargar_modelo():
    """
    Se ejecuta al iniciar la aplicación.
    Carga el modelo entrenado en memoria.
    """
    global modelo
    
    if not os.path.exists(modelo_path):
        print(f"ERROR CRITICO: No se encontro '{modelo_path}'")
        print("   Ejecuta 'python entrenar_modelo.py' primero")
        raise FileNotFoundError(f"Archivo '{modelo_path}' no encontrado")
    
    try:
        with open(modelo_path, 'rb') as archivo:
            modelo = pickle.load(archivo)
        print(f"Modelo cargado exitosamente desde '{modelo_path}'")
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        raise e

#Modelos de datos (Schemas)


class RespuestaPrediccion(BaseModel):
    """
    Esquema de datos de salida de la API.
    """
    exito: bool = Field(description="Indica si la prediccion fue exitosa")
    millas: float = Field(description="Millaje ingresado")
    anio: int = Field(description="Año ingresado")
    precio_estimado: float = Field(description="Precio predicho en dolares")
    mensaje: str = Field(description="Mensaje descriptivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "exito": True,
                "millas": 50000,
                "anio": 2020,
                "precio_estimado": 28450.50,
                "mensaje": "Prediccion realizada exitosamente"
            }
        }


class ErrorResponse(BaseModel):
    """
    Esquema de respuesta en caso de error.
    """
    exito: bool = False
    error: str
    detalle: Optional[str] = None

class DatosAuto(BaseModel):
    """
    Esquema de entrada para la predicción del precio de un auto.
    """
    millas: float = Field(..., description="Millaje del vehiculo", ge=0, le=500000)
    anio: int = Field(..., description="Año del modelo", ge=2000, le=2030)
    email: Optional[str] = Field(None, description="Email opcional para notificaciones")

    @validator("millas")
    def validar_millas(cls, v):
        if v is None:
            raise ValueError("millas es obligatorio")
        if v < 0 or v > 500000:
            raise ValueError("millas debe estar entre 0 y 500000")
        return v

    @validator("anio")
    def validar_anio(cls, v):
        if v is None:
            raise ValueError("anio es obligatorio")
        if v < 2000 or v > 2030:
            raise ValueError("anio debe estar entre 2000 y 2030")
        return v

#Endpoints

@app.get("/", tags=["General"])
async def raiz():
    """
    Endpoint raíz - Información de la API.
    """
    return {
        "nombre": "API Predictor de Precios de Autos Usados",
        "version": "1.0.0",
        "estado": "Activo",
        "desarrollador": "Danny Leonardo Novoa Rodriguez",
        "endpoints": {
            "GET /": "Informacion general",
            "GET /health": "Estado del servicio",
            "POST /predecir": "Realizar prediccion de precio",
            "GET /docs": "Documentacion interactiva (Swagger UI)",
            "GET /redoc": "Documentacion alternativa (ReDoc)"
        },
        "ejemplo_uso": {
            "url": "/predecir",
            "metodo": "POST",
            "body": {
                "millas": 50000,
                "anio": 2020
            }
        }
    }


@app.get("/health", tags=["General"])
async def health_check():
    """
    Health check - Verifica que el servicio esté funcionando.
    """
    modelo_cargado = modelo is not None
    
    return {
        "estado": "healthy" if modelo_cargado else "unhealthy",
        "modelo_cargado": modelo_cargado,
        "version": "1.0.0"
    }


@app.post("/predecir", response_model=RespuestaPrediccion, tags=["Prediccion"])
async def predecir_precio(datos: DatosAuto):
    """
    Predice el precio de un auto usado basado en millaje y año.
    
    **Parametros:**
    - **millas**: Millaje del vehiculo (>=0, <=500,000)
    - **anio**: Año del modelo (2000-2030)
    - **email**: (Opcional) Email para notificacion
    
    **Retorna:**
    - Precio estimado en dolares
    - Datos ingresados
    - Mensaje de exito/error
    
    **Ejemplo de request:**
```json
    {
        "millas": 50000,
        "anio": 2020,
        "email": "usuario@ejemplo.com"
    }
```
    
    **Ejemplo de response:**
```json
    {
        "exito": true,
        "millas": 50000,
        "anio": 2020,
        "precio_estimado": 28450.50,
        "mensaje": "Prediccion realizada exitosamente"
    }
```
    """
    
    # Verificar que el modelo esté cargado
    if modelo is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. Contacta al administrador."
        )
    
    try:
        # Realizar predicción
        # El modelo espera: [[millas, anio]]
        entrada = [[datos.millas, datos.anio]]
        precio_predicho = modelo.predict(entrada)[0]
        
        # Redondear a 2 decimales
        precio_predicho = round(precio_predicho, 2)
        
        # Validar que el precio sea razonable
        if precio_predicho < 0:
            precio_predicho = 0.0
            mensaje = "Prediccion ajustada a $0 (valor minimo)"
        else:
            mensaje = "Prediccion realizada exitosamente"
        
        # Retornar respuesta
        return RespuestaPrediccion(
            exito=True,
            millas=datos.millas,
            anio=datos.anio,
            precio_estimado=precio_predicho,
            mensaje=mensaje
        )
        
    except Exception as e:
        # Capturar cualquier error durante la predicción
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar prediccion: {str(e)}"
        )


# EEjecución del serivdor de forma local

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("Iniciando servidor de desarrollo...")
    print("="*60)
    print("URL local: http://localhost:8000")
    print("Documentacion: http://localhost:8000/docs")
    print("Para produccion, usa: uvicorn app:app --host 0.0.0.0 --port 8000")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app:app",  # ← CAMBIO: Cadena de texto en lugar de objeto
        host="0.0.0.0",
        port=8000,
        reload=True
    )