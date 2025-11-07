
import pandas as pd
import os

CSV_ORIGINAL = "used_car_prices.csv"
CSV_LIMPIO = "used_car_prices_limpio.csv"

if not os.path.exists(CSV_ORIGINAL):
    print(f"ERROR: No se encontró '{CSV_ORIGINAL}'")
    exit()

print("Cargando dataset original...")
df = pd.read_csv(CSV_ORIGINAL)
print(f"{len(df)} filas originales.")


# Limpieza de Milage y price

print("\nLimpiando 'milage' y 'price'...")
df['milage'] = df['milage'].astype(str).str.replace(r'[^0-9]', '', regex=True)
df['price'] = df['price'].astype(str).str.replace(r'[^0-9]', '', regex=True)

# Convertir a números, se tiene en cuenta que model_year ya es numérico con int64
df['milage'] = pd.to_numeric(df['milage'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')


# Filtro de datos validos
print("Filtrando datos válidos...")
df = df.dropna(subset=['milage', 'model_year', 'price'])
df = df[(df['model_year'] >= 2000) & (df['model_year'] <= 2025)]
df = df[df['milage'] >= 0]
df = df[df['price'] > 0]

print(f"{len(df)} filas válidas después de limpieza.")

if len(df) == 0:
    print("ERROR: No quedaron datos.")
    exit()

# Selección de columnas relevantes
print("Seleccionando columnas relevantes...")
df_limpio = df[['milage', 'model_year', 'price']].copy()

# Guardar el CSV limpio en un nuevo archivo
df_limpio.to_csv(CSV_LIMPIO, index=False)
print(f"\nCSV LIMPIO GUARDADO: '{CSV_LIMPIO}'")
print(f"   → Solo {len(df_limpio)} filas")
print(f"   → Solo 3 columnas: milage, model_year, price")
print(f"   → Listo para ML")