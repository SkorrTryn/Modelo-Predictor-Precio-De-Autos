# === DIAGNÓSTICO DE COLUMNAS (AGREGA ESTO) ===
CSV_ORIGINAL = "used_car_prices.csv"
import pandas as pd
df = pd.read_csv(CSV_ORIGINAL)

print("\n" + "="*60)
print("       DIAGNÓSTICO DE COLUMNAS")
print("="*60)
print(f"Filas totales: {len(df)}")
print("\nCOLUMNAS EXACTAS EN EL CSV:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. '{col}'")  # ← Con comillas para ver espacios

print(f"\nPRIMERAS 3 FILAS:")
print(df.head(3))

print(f"\nTIPOS DE DATOS:")
print(df.dtypes)

input("\nPresiona Enter para continuar...")  # ← Pausa para que veas
print("="*60)

Tabla_datos="used_car_prices.csv"
td = pd.read_csv(Tabla_datos)
print(f"filas toales: {len(td)}")