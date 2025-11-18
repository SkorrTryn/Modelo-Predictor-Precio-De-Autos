"""
Realizado por: Danny Leonardo Novoa Rodriguez
Propósito: Entrenar el modelo de regresión lineal y guardarlo como archivo .pkl
Ejecutar una sola vez antes de desplegar la API
"""

# Librerías
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import pickle
import os
import sys

def entrenar_y_guardar_modelo():
    print("="*60)
    print("ENTRENAMIENTO DEL MODELO V3 - PICKLE")
    print("="*60)
    
    # 1. CARGAR DATASET
    csv_path = "used_car_prices_limpio.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: No se encontró {csv_path}")
        return False
    
    print(f"\nCargando {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Dataset cargado: {len(df)} registros")
    print(f"Columnas: {list(df.columns)}")
    
    # 2. VERIFICAR COLUMNAS
    columnas_requeridas = ['milage', 'model_year', 'price']
    if not all(col in df.columns for col in columnas_requeridas):
        print(f"ERROR: Faltan columnas. Se encontraron: {list(df.columns)}")
        return False
    
    # 3. PREPARAR DATOS
    print("\nPreparando datos...")
    X = df[['milage', 'model_year']]
    y = df['price']
    
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    
    # 4. DIVIDIR DATOS
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} registros")
    print(f"Test set: {len(X_test)} registros")
    
    # 5. ENTRENAR
    print("\nEntrenando modelo...")
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    print("✓ Modelo entrenado")
    
    # 6. EVALUAR
    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"\nMAE: ${mae:,.2f}")
    print(f"Coeficientes: {modelo.coef_}")
    print(f"Intercepto: {modelo.intercept_:.2f}")
    
    # 7. GUARDAR CON PICKLE (NO JOBLIB)
    modelo_path = "modelo_precios.pkl"
    print(f"\nGuardando modelo en {modelo_path}...")
    
    try:
        # CAMBIO CRÍTICO: Usar pickle en vez de joblib
        with open(modelo_path, 'wb') as f:
            pickle.dump(modelo, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        print("✓ pickle.dump() completado")
        
        # Verificar que se creó
        if not os.path.exists(modelo_path):
            print("ERROR: El archivo NO se creó")
            return False
        
        # Ver tamaño
        tamano = os.path.getsize(modelo_path)
        print(f"Tamaño del archivo: {tamano} bytes ({tamano/1024:.2f} KB)")
        
        # Verificar tamaño mínimo
        if tamano < 1000:
            print("WARNING: El archivo es sospechosamente pequeño")
            return False
        
        # 8. PROBAR CARGA
        print("\nProbando cargar el modelo...")
        with open(modelo_path, 'rb') as f:
            modelo_cargado = pickle.load(f)
        
        print("✓ Modelo cargado exitosamente")
        
        # Hacer predicción de prueba
        test_X = [[50000, 2020]]
        pred = modelo_cargado.predict(test_X)[0]
        print(f"Predicción de prueba: ${pred:,.2f}")
        
        print("\n" + "="*60)
        print("✓✓✓ ÉXITO: Modelo guardado y verificado ✓✓✓")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = entrenar_y_guardar_modelo()
    sys.exit(0 if exito else 1)

