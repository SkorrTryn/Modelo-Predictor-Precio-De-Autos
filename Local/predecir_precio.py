#URL del Dataset de Kaggle: https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset 
#Realizado por: Danny Leonardo Novoa Rodriguez
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np


CSV_LIMPIO = "used_car_prices_limpio.csv"
df = pd.read_csv(CSV_LIMPIO)
print(f"{len(df)} autos listos para ML.")

#Entranmiento del modelo
X = df[['milage', 'model_year']]
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = LinearRegression().fit(X_train, y_train)

mae = mean_absolute_error(y_test, modelo.predict(X_test))
print(f"Error promedio (MAE): ${mae:,.0f}")

#Grafico de Millage vs Price
plt.figure(figsize=(10, 6))
plt.scatter(df['milage'], df['price'], alpha=0.6, color='green', label='Datos reales')
millas_range = np.linspace(df['milage'].min(), df['milage'].max(), 100)
anio_promedio = df['model_year'].mean()
X_tendencia = np.column_stack([millas_range, np.full_like(millas_range, anio_promedio)])
pred_tendencia = modelo.predict(X_tendencia)

plt.plot(millas_range, pred_tendencia, color='red', linewidth=3, label='Tendencia del modelo')

plt.xlabel("Millas recorridas", fontsize=12)
plt.ylabel("Precio ($)", fontsize=12)
plt.title("Relación: Millas vs Precio", fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

#Logica del predictor para la terminal
print("\n" + "="*60)
print("     PREDICTOR DE PRECIOS DE AUTOS USADOS")
print("="*60)

while True:
    try:
        print("\n" + "-"*50)
        millas = float(input("Millas recorridas: "))
        anio = int(input("Año del modelo: "))
        
        if not (2000 <= anio <= 2025):
            print("Año inválido (2000-2025).")
            continue
        if millas < 0:
            print("Millas no pueden ser negativas.")
            continue
            
        precio = modelo.predict([[millas, anio]])[0]
        print(f"\nPRECIO ESTIMADO: ${precio:,.0f}")
        
        otra = input("\n¿Predecir otro auto? (s/n): ").strip().lower()
        if otra != 's':
            break
            
    except ValueError:
        print("Entrada inválida. Usa solo números.")
    except Exception as e:
        print(f"Error: {e}")

print("\n¡La simulación ha finalizado!")