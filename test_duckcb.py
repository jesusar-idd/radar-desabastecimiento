import duckdb
import pandas as pd

#OBJETIVO: convertir a una tabla con duckdb para tener la información rescatada de la API de manera estructurada

con = duckdb.connect()

df = con.execute("""
    SELECT
        suministro.cn AS cn,
        suministro.nombre AS nombre,
        suministro.tipoProblemaSuministro AS tipo_problema_suministro,
        suministro.fini AS fecha_inicio,
        suministro.activo AS activo,
        suministro.observ AS observaciones
    FROM (
        SELECT unnest(resultados) AS suministro
        FROM read_json_auto(
            'data/raw/cima/suministro_2026-10-08.json'
        )
    )
""").df()

#Transformación de fechas
fecha_inicio_datetime = pd.to_datetime(df['fecha_inicio'], unit='ms') #Pasamos la fecha en pandas a datetime

df['fecha_inicio'] = fecha_inicio_datetime
"""
VALIDACIONES
Primero hice validaciones exploratorias sobre el dataset para comprobar nulos, unicidad y estados. 
Posteriormente trasladaría estas reglas a tests automatizados de dbt.

print("Valores nulos de cn:", df['cn'].isnull().sum()) #Vemos que no hay ningun valor nulo de cn
print("Valores nulos de fecha_inicio:", df['fecha_inicio'].isnull().sum())

print('Valores de cn unicos:', df['cn'].nunique())
print('Valores de cn duplicados:', df['cn'].duplicated().sum())

print('Medicamento estado activo:', (df['activo'] == True).sum())
print('Medicamento estado apagado:', (df['activo'] == False).sum())
"""
anio = df['fecha_inicio'].dt.year
print('Número de registros por año', df.groupby(anio)['fecha_inicio'].count())

print("Filas:", df['fecha_inicio'].head())
print(df.dtypes)