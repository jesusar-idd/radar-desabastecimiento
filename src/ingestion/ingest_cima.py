import json 
import math 
from datetime import datetime #La usaremos para transformar las fechas
from pathlib import Path
import requests #Necesaria para hacer el GET

#URL del endpoint de donde sacaremos la información
URL_BASE = "https://cima.aemps.es/cima/rest/psuministro" 

def get_pages():
	response = requests.get(URL_BASE) 
	response.raise_for_status() #Manejo de errores

	data = response.json()

	totalFilas = data['totalFilas']
	tamanioPagina = data['tamanioPagina']

	n_pages = math.ceil(totalFilas/tamanioPagina) #Redondea hacia arriba en caso de existir decimales

	resultados = data['resultados'] #Guardaremos seguidamente todos los resultados de todas lás paginas con un bucle

	for page in range(2, n_pages+1): #Empezamos 2 para ahorrar tiempo y memoria ya que la página 1 ya la tenemos
		response = requests.get(URL_BASE, params={'pagina': page})
		response.raise_for_status()

		resultados.extend(response.json()['resultados']) #Añade seguidamente la información, 

	return {'totalFilas': totalFilas, 'tamanioPagina': tamanioPagina, 'resultados': resultados}

snapshot = get_pages() #Será nuestra snapshot diaria de todos los psuministros.json()
ruta = Path('data/raw/cima') #Directorio donde guardaremos las snapshots
fecha = datetime.now().strftime("%Y-%m-%d") #Fecha del día en el que realizamos la snapshot
ruta.mkdir(parents=True, exist_ok=True) #Chequeamos que la ruta esté correcta
archivo = ruta / f"suministro_{fecha}.json" #Generamos el archivo del día concreto

with open(archivo, 'w', encoding='utf-8') as f:#Guardamos los posibles caractéres especiales con encoding = utf-8
	#Convertimos nuestro diccionario a JSON 
	json.dump(snapshot, f, 
	ensure_ascii=False, #Permitimos caracteres especiales
	indent = 2) #Para que el JSON sea legible para nosotros

#Mensaje final para comprobar que todo funciona correctamente
print(f'Snapshot guardado en: {archivo}')
print(f'Registros descargados: {len(snapshot['resultados'])}')