"""
Realizado por: Danny Leonardo Novoa Rodriguez
Propósito: Entrenar el modelo de regresión lineal y guardarlo como archivo .pkl
Ejecutar una sola vez antes de desplegar la API
"""

#Librerias
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import pickle
import os

def entrenar_y_guardar_modelo():
    """ 
    Entrena el modelo de predicción de precios y lo guarda en disco.
    """
    print("="*60)
    print("ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE PRECIOS")
    print("="*60)

    #Corroboraciones previas
    #Verifación del CSV
    csv_path = "used_car_prices_limpio.csv"
    if not os.path.exists(csv_path):
        print(f" Error: No se encontró el archivo '{csv_path}'")
        return False
    
    #Carga del Dataset
    print(f"\nCargando dataset desde '{csv_path}'...")
    try:
        df = pd.read_csv(csv_path)
        print(f" Dataset cargado: {len(df)} registros")
    except Exception as e:
        print(f" Error al cargar CSV: {e}")
        return False
    
    
    #Preparacion de los datos
    print("\n Preparando datos para entrenamiento...")
    X = df[['milage', 'model_year']]  # Características (features)
    y = df['price']                    # Variable objetivo (target)
    
    print(f"   • Características (X): {X.shape}")
    print(f"   • Objetivo (y): {y.shape}")
    
    #Divsión de entraniemiento y prueba
    print("\n Dividiendo datos (80% entrenamiento, 20% prueba)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,   
        random_state=42   
    )
    
    print(f" Datos de entrenamiento: {len(X_train)} registros")
    print(f" Datos de prueba: {len(X_test)} registros")
    
    #Entrenamiento del modelo
    print("\n Entrenando modelo de Regresión Lineal...")
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    print(" Modelo entrenado exitosamente")
    
    #Evaluacion del modelo
    print("\n Evaluando precisión del modelo...")
    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"    Error Absoluto Medio (MAE): ${mae:,.2f}")
    print(f"    Interpretación: El modelo se equivoca en promedio ±${mae:,.0f}")
    
    #Mostrar los coeficientes aprendidos
    print(f"\n Coeficientes del modelo:")
    print(f"    Impacto de millas: {modelo.coef_[0]:,.4f} (por cada milla)")
    print(f"    Impacto de año: {modelo.coef_[1]:,.2f} (por cada año)")
    print(f"    Intercepto: {modelo.intercept_:,.2f}")
    
    #Save del modelo
    modelo_path = "modelo_precios.pkl"
    print(f"\n Guardando modelo en '{modelo_path}'...")
    
    try:
        with open(modelo_path, 'wb') as archivo:
            pickle.dump(modelo, archivo)
        
        # Verificar que se guardó correctamente
        tamano_mb = os.path.getsize(modelo_path) / (1024 * 1024)
        print(f" Modelo guardado exitosamente ({tamano_mb:.2f} MB)")
        
    except Exception as e:
        print(f" Error al guardar modelo: {e}")
        return False
    
    # 9. VERIFICAR CARGA DEL MODELO
    print("\n Verificando el modelo.")
    try:
        with open(modelo_path, 'rb') as archivo:
            modelo_cargado = pickle.load(archivo)
        
        # Hacer una predicción de prueba
        test_millas = 50000
        test_anio = 2020
        precio_prueba = modelo_cargado.predict([[test_millas, test_anio]])[0]
        
        print(f" Modelo verificado correctamente")
        print(f"  Prueba: Auto {test_anio} con {test_millas:,} millas")
        print(f"  Predicción: ${precio_prueba:,.2f}")
        
    except Exception as e:
        print(f" Error al verificar modelo: {e}")
        return False
    
    print(" ENTRENAMIENTO COMPLETADO CON ÉXITO")
    return True

# EJECUTAR SI SE LLAMA DIRECTAMENTE
if __name__ == "__main__":
    exito = entrenar_y_guardar_modelo()
    
    if not exito:
        print("\n El entrenamiento falló.")
        exit(1)
    
    exit(0)