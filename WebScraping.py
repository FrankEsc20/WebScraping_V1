###########################################################################################################################################
# Importamos las librerías necesarias para el web scraping y el manejo de datos.
###########################################################################################################################################
import pandas as pd
import time
from pathlib import Path

from WebScraping_Indeed import ejecutar_indeed
from WebScraping_Computrabajo import ejecutar_computrabajo

###########################################################################################################################################
# Gestión de salidas:
###########################################################################################################################################
# Creamos la carpeta de salida si no existe
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

###########################################################################################################################################
# Ejecutamos los scrapers:
###########################################################################################################################################

df_indeed = ejecutar_indeed()
df_computrabajo = ejecutar_computrabajo()


###########################################################################################################################################
# Consolidamos la información:
###########################################################################################################################################

df = pd.concat(
    [
        df_indeed, 
        df_computrabajo],
    ignore_index=True
)

# Guardamos los DataFrames secundarios en archivos CSV individuales:
# df_indeed.to_csv(OUTPUT_DIR / 'trabajos_aplicados_indeed.csv', index=False)


###########################################################################################################################################
# Guardamos el DataFrame final:
###########################################################################################################################################

df.to_csv(OUTPUT_DIR / 'trabajos_aplicados.csv', index=False)