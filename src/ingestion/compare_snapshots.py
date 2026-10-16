import json
import duckdb
import pandas as pd
from pathlib import Path
from datetime import date

con = duckdb.connect('data/processed/radar.duckdb')

df_ayer = con.execute(
"""
SELECT suministro.cn AS cn,
       suministro.activo AS activo,
       suministro.fini AS fecha_inicial,
       suministro.ffin AS fecha_fin,
       suministro.tipoProblemaSuministro AS tipoProblemaSuministro
FROM ( SELECT unnest(resultados) AS suministro
       FROM read_json_auto('data/raw/cima/suministro_2026-10-08.json')
      )
"""
).df()

df_hoy = con.execute(
"""
SELECT suministro.cn AS cn,
       suministro.activo AS activo,
       suministro.fini AS fecha_inicial,
       suministro.ffin AS fecha_fin,
       suministro.tipoProblemaSuministro AS tipoProblemaSuministro
FROM ( SELECT unnest(resultados) AS suministro
       FROM read_json_auto('data/raw/cima/suministro_2026-10-09.json')
      )
"""
).df()

cn_comunes = df_ayer[df_ayer['cn'].isin(df_hoy['cn'])] #Vemos cuales siguen estando
cn_distintas_ayer = df_ayer[~df_ayer['cn'].isin(df_hoy['cn'])] # Con el prefijo ~ hacemos las que no estan en, lo contrario de isin
cn_distintas_hoy = df_hoy[~df_hoy['cn'].isin(df_ayer['cn'])]

"""
print(f'Comunes: \n{cn_comunes}')
print(f'Solo en ayer: \n{cn_distintas_ayer}')
print(f'Solo en hoy: \n{cn_distintas_hoy}')
print(f"Len ayer: {len(df_ayer['cn'])}, Len hoy: {len(df_hoy['cn'])}, Len comunes: {len(cn_comunes['cn'])}")
"""

contadores = {
    "activo": 0,
    "tipo_problema": 0,
    "fecha_inicial": 0,
    "fecha_fin_informada": 0,
    "fecha_fin_eliminada": 0,
    "fecha_fin_modificada": 0
}

fecha_snapshot_ayer = date.fromisoformat(Path('data/raw/cima/suministro_2026-10-08.json').stem.split('_')[1])
fecha_snapshot_hoy = date.fromisoformat(Path('data/raw/cima/suministro_2026-10-09.json').stem.split('_')[1])

eventos = []

for cn in cn_comunes['cn']:
    fila_ayer = df_ayer[df_ayer['cn'] == cn]
    fila_hoy = df_hoy[df_hoy['cn'] == cn]

    #Activo
    if fila_ayer['activo'].iloc[0] != fila_hoy['activo'].iloc[0]: #Comparamos los valores individuales
        eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'activo', fila_ayer['activo'].iloc[0], fila_hoy['activo'].iloc[0], 'valor_modificado'])
        contadores['activo'] +=1
        print(f'Cambio en el estado del activo')
        print(f"Fila ayer: \n{fila_ayer}\nFila hoy: \n{fila_hoy}\n")

    if fila_ayer['tipoProblemaSuministro'].iloc[0] != fila_hoy['tipoProblemaSuministro'].iloc[0]: #Comparamos los valores individuales
        eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'tipoProblemaSuministro', fila_ayer['tipoProblemaSuministro'].iloc[0], fila_hoy['tipoProblemaSuministro'].iloc[0], 'valor_modificado'])
        contadores['tipo_problema'] +=1
        print(f"Cambio en el tipo de problema de suministro")
        print(f"Fila ayer: \n{fila_ayer}\nFila hoy: \n{fila_hoy}\n")

    if fila_ayer['fecha_inicial'].iloc[0] != fila_hoy['fecha_inicial'].iloc[0]: #Comparamos los valores individuales
        eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'fecha_inicial', pd.to_datetime(fila_ayer['fecha_inicial'].iloc[0], unit='ms', utc=True), pd.to_datetime(fila_hoy['fecha_inicial'].iloc[0], unit='ms', utc=True), 'fecha_modificada'])
        contadores['fecha_inicial'] +=1
        print(f"Cambio en la fecha inicial")
        print(f"Fila ayer: \n{fila_ayer}\nFila hoy: \n{fila_hoy}\n")

    #Para la fecha final utilizamos pd para manejar correctamente los nulos
    if pd.isna(fila_ayer['fecha_fin'].iloc[0]) != pd.isna(fila_hoy['fecha_fin'].iloc[0]) or (not pd.isna(fila_ayer['fecha_fin'].iloc[0]) and not pd.isna(fila_hoy['fecha_fin'].iloc[0]) and fila_ayer['fecha_fin'].iloc[0] != fila_hoy['fecha_fin'].iloc[0]):
        print("Cambio en la fecha fin")
        print(f"Cambio en fecha_fin para CN {cn}")
        print(f"Ayer: {fila_ayer['fecha_fin'].iloc[0]}")
        print(f"Hoy: {fila_hoy['fecha_fin'].iloc[0]}")

        fin_ayer = fila_ayer['fecha_fin'].iloc[0]
        fin_hoy = fila_hoy['fecha_fin'].iloc[0]

        if pd.isna(fin_ayer) and not pd.isna(fin_hoy):
        # fecha_fin_informada
            eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'fecha_fin', None, pd.to_datetime(fila_hoy['fecha_fin'].iloc[0], unit='ms', utc=True), 'fecha_fin_informada'])
            contadores['fecha_fin_informada'] +=1

        elif not pd.isna(fin_ayer) and pd.isna(fin_hoy):
        # fecha_fin_eliminada
            eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'fecha_fin', pd.to_datetime(fila_ayer['fecha_fin'].iloc[0], unit='ms', utc=True), None, 'fecha_fin_eliminada'])
            contadores['fecha_fin_eliminada'] +=1

        elif not pd.isna(fin_ayer) and not pd.isna(fin_hoy) and fin_ayer != fin_hoy:
        # fecha_fin_modificada
            eventos.append([fecha_snapshot_ayer, fecha_snapshot_hoy, cn, 'fecha_fin', pd.to_datetime(fila_ayer['fecha_fin'].iloc[0], unit='ms', utc=True), pd.to_datetime(fila_hoy['fecha_fin'].iloc[0], unit='ms', utc=True), 'fecha_fin_modificada'])
            contadores['fecha_fin_modificada'] +=1

print(f"\n---RESUMEN FINAL---")
print(f"Cambios en activo: {contadores.get('activo')}")
print(f"Cambios en tipo de problema de suministro: {contadores.get('tipo_problema')}")
print(f"Cambios en fecha inicial: {contadores.get('fecha_inicial')}")
print(f"Cambios en fecha final: {contadores.get('fecha_fin_informada') + contadores.get('fecha_fin_eliminada') + contadores.get('fecha_fin_modificada')}")
print(f"Registros solo ayer: {len(cn_distintas_ayer)}")
print(f"Registros solo hoy: {len(cn_distintas_hoy)}")
print(f"Eventos detectados: {len(eventos)}")
print("Primeros eventos:")
print(eventos[:5])

eventos_nuevos = []

for evento in eventos:
    existe = con.execute("""
        SELECT COUNT(*)
        FROM historico_events
        WHERE snapshot_anterior = ?
          AND snapshot_actual = ?
          AND cn = ?
          AND atributo = ?
    """, [evento[0], evento[1], evento[2], evento[3]]).fetchone()[0]

    if existe == 0:
        eventos_nuevos.append(evento)

if eventos_nuevos:
    con.executemany("""
        INSERT INTO historico_events (
            snapshot_anterior,
            snapshot_actual,
            cn,
            atributo,
            valor_anterior,
            valor_nuevo,
            tipo_evento
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, eventos_nuevos)

print(f"Eventos detectados: {len(eventos)}")
print(f"Eventos nuevos insertados: {len(eventos_nuevos)}")