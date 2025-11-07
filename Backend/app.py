"""
app.py
Realizado por: Danny Leonardo Novoa Rodriguez
Propósito: API REST para predicción de precios de autos usados
Con entrenamiento automático si el modelo no existe
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib
import os
from typing import Optional

# ============================================
# CONFIGURACIÓN DE FASTAPI
# ============================================

app = FastAPI(
    title="Predictor de Precios de Autos Usados",
    description="API para predecir precios de vehiculos basado en millaje y año del modelo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CONFIGURACIÓN DE CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# VARIABLES GLOBALES
# ============================================

modelo = None
modelo_path = "modelo_precios.pkl"
csv_path = "used_car_prices_limpio.csv"

# ============================================
# FUNCIÓN DE ENTRENAMIENTO
# ============================================

def entrenar_modelo():
    """
    Entrena el modelo desde el CSV y lo guarda.
    Se ejecuta automáticamente si el modelo no existe.
    """
    print("="*60)
    print("ENTRENANDO MODELO DE PREDICCION...")
    print("="*60)
    
    # Verificar CSV
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")
    
    # Cargar datos
    print(f"Cargando {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Registros cargados: {len(df)}")
    
    # Preparar datos
    X = df[['milage', 'model_year']]
    y = df['price']
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Entrenar
    print("Entrenando modelo...")
    modelo_entrenado = LinearRegression()
    modelo_entrenado.fit(X_train, y_train)
    
    # Evaluar
    mae = mean_absolute_error(y_test, modelo_entrenado.predict(X_test))
    print(f"MAE: ${mae:,.2f}")
    
    # Guardar
    print(f"Guardando modelo en {modelo_path}...")
    joblib.dump(modelo_entrenado, modelo_path, compress=3)
    
    # Verificar
    size = os.path.getsize(modelo_path)
    print(f"Modelo guardado: {size} bytes ({size/1024:.2f} KB)")
    
    print("="*60)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*60)
    
    return modelo_entrenado

# ============================================
# CARGAR O ENTRENAR MODELO AL INICIAR
# ============================================

@app.on_event("startup")
async def cargar_o_entrenar_modelo():
    """
    Al iniciar la aplicación:
    1. Intenta cargar el modelo existente
    2. Si no existe, entrena uno nuevo
    """
    global modelo
    
    try:
        # Intentar cargar modelo existente
        if os.path.exists(modelo_path):
            print(f"Cargando modelo existente desde {modelo_path}...")
            modelo = joblib.load(modelo_path)
            print("Modelo cargado exitosamente")
        else:
            # Modelo no existe, entrenar uno nuevo
            print(f"Modelo no encontrado. Entrenando nuevo modelo...")
            modelo = entrenar_modelo()
            print("Modelo entrenado y listo")
            
    except Exception as e:
        print(f"ERROR al cargar/entrenar modelo: {e}")
        # Intentar entrenar como último recurso
        try:
            print("Intentando entrenar modelo como último recurso...")
            modelo = entrenar_modelo()
        except Exception as e2:
            print(f"ERROR CRITICO: No se pudo entrenar modelo: {e2}")
            raise e2

# ============================================
# MODELOS DE DATOS (SCHEMAS)
# ============================================

class DatosAuto(BaseModel):
    millas: float = Field(
        ..., 
        ge=0,
        description="Millaje del vehiculo en millas",
        example=50000
    )
    anio: int = Field(
        ..., 
        ge=2000, 
        le=2030,
        description="Año de fabricacion del modelo",
        example=2020
    )
    email: Optional[str] = Field(
        None,
        description="Email opcional para notificacion",
        example="usuario@ejemplo.com"
    )
    
    @validator('millas')
    def validar_millas(cls, v):
        if v < 0:
            raise ValueError('Las millas no pueden ser negativas')
        if v > 500000:
            raise ValueError('Millaje sospechosamente alto (maximo 500,000)')
        return v
    
    @validator('anio')
    def validar_anio(cls, v):
        if v < 2000:
            raise ValueError('Año minimo: 2000')
        if v > 2030:
            raise ValueError('Año maximo: 2030')
        return v


class RespuestaPrediccion(BaseModel):
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
    exito: bool = False
    error: str
    detalle: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["General"])
async def raiz():
    """Endpoint raíz - Información de la API"""
    return {
        "nombre": "API Predictor de Precios de Autos Usados",
        "version": "1.0.0",
        "estado": "Activo",
        "desarrollador": "Danny Leonardo Novoa Rodriguez",
        "endpoints": {
            "GET /": "Informacion general",
            "GET /health": "Estado del servicio",
            "POST /predecir": "Realizar prediccion de precio",
            "GET /docs": "Documentacion interactiva",
            "GET /redoc": "Documentacion alternativa"
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
    """Health check - Verifica que el servicio esté funcionando"""
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
    """
    
    # Verificar que el modelo esté cargado
    if modelo is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. El servidor puede estar iniciando."
        )
    
    try:
        # Realizar predicción
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
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar prediccion: {str(e)}"
        )


# ============================================
# EJECUTAR SERVIDOR (solo desarrollo local)
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("Iniciando servidor de desarrollo...")
    print("="*60)
    print("URL local: http://localhost:8000")
    print("Documentacion: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )