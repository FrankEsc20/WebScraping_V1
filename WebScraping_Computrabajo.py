###########################################################################################################################################
# Importamos las librerías necesarias para el web scraping y el manejo de datos.
###########################################################################################################################################
import requests
from bs4 import BeautifulSoup as bs
import random
import re
import time
import pandas as pd
import numpy as np
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
#import undetected_chromedriver as uc
import funciones as fn

#############################################################################################################################################

# Ponemos las opciones de formatos:
pd.set_option('display.max_columns', None) # Opción para que se puedan ver todas las columnas en el print:
pd.options.display.float_format = '{:.6f}'.format # Opcion para que no se ponga en notación cientifica

###########################################################################################################################################
# Gestión de salidas:
###########################################################################################################################################
# Creamos la carpeta de salida si no existe
OUTPUT_HISTORY = Path('data/history')
OUTPUT_HISTORY.mkdir(parents=True, exist_ok=True)

###########################################################################################################################################
# Empezamos por Computrabajo:
###########################################################################################################################################
# Abrimos el navegador, iniciamos sesion con el correo sin usar google paara que no nos bloquee el inicio de sesion.
def ejecutar_computrabajo():
    try:
        # Abrimos el navegador:
        browser = webdriver.Chrome()
        browser.get('https://candidato.mx.computrabajo.com/candidate/match/')

        # Esperamos a que el usuario termine de autenticarse manualmente.
        # Selenium continuará automáticamente cuando aparezca al menos un trabajo aplicado.
        WebDriverWait(browser, 300).until(
                    lambda driver: driver.find_elements(By.CSS_SELECTOR, 'div.w70_mB.fl')
                )

        # Definimos el dataframe:
        df = pd.DataFrame()

        # Definimos la primera iteracion:
        i = 1

        # Ponemos un espacio para mejor legibilidad
        print('')
        print('Comenzando el proceso de scraping de Computrabajo...')

        # Comenzmos a iterar sobre las páginas de resultados 
        # hasta que no haya más trabajos aplicados.
        while True:
            # Definimos la URL de la página de resultados de trabajos aplicados:
            url = f'https://candidato.mx.computrabajo.com/candidate/match/?=idap3&f=FEE939887FF3D46C&p={i}'
            browser.get(url)

            # Esperamos un intervalo aleatorio para permitir que la página termine de cargar su contenido.
            time.sleep(random.uniform(2, 5))

            #Obtenemos el HTML de la página
            html = browser.page_source
            # Le damos un mejor formato al HTML para poder analizarlo mejor
            soup = bs(html, 'html.parser')

            # Obtemeos la sección de la página que contiene la información de la paginación:
            pagina = soup.find('div', {'class': 'w70_mB fl'})

            # Validamos si la sección de paginación existe y si contiene el número de página actual. 
            # Si no, salimos del bucle.
            if pagina is None or pagina.find('span', {'class': 'sel'}) is None:
                print(f'Proceso finalizado. Se procesaron {i - 1} páginas.')
                print('')

                # Esperamos un tiempo aleatorio antes de cerrar el navegador para simular un comportamiento humano y evitar ser bloqueados por la página.
                time.sleep(random.uniform(3, 5))
                browser.quit()
                break ### <=============================================== FINALIZACIÓN DEL BUCLE ###
            
            # Obtenemos el número de la página actual:
            pagina_actual = int(
                pagina.find('span', {'class': 'sel'})
                .get_text(strip=True)
                .split()[-1]
            )

            # Hacemos la prueba de que si el número de iteraciones es mayor que 
            # el número de páginas, entonces salimos del bucle.
            if i == pagina_actual:
                # Ahora conseguimos los datos de los trabajos de la pagina:
                # Conseguimos la lista de trabajos aplicados:
                lista_jobs = soup.find('div', {'class': 'w70_mB fl'})
                lista_jobs

                # Ahora obtenemos los nombres de los trabajos aplicados y los guardamos en una lista.
                nombres = [
                    nombre.get_text(strip=True)
                    for nombre in lista_jobs.find_all('h1', {'class': 'fs18 fwB mAll0'})
                ]
                nombres

                # Obtenemos los patrones de los trabajos aplicados y los guardamos en una lista.
                patrones = [
                    re.sub(r'\d+(?:\.\d+)?$', '', patron.get_text(strip=True)).strip()
                    for patron in lista_jobs.find_all('p', {'class': 'fs16 fc_base mt5 dIB_m'})
                ]
                patrones

                #Obtenemos los lugares de los trabajos aplicados y los guardamos en una lista.
                lugares = [
                    lugar.get_text(strip=True)
                    for lugar in lista_jobs.find_all('p', {'class': 'fs16 fc_base dIB_m'})
                ]
                lugares

                # Ahora obtenemos el status de los trabajos aplicados y los guardamos en una lista.
                status = [
                    stat.get_text(strip=True)
                    for stat in lista_jobs.find_all('p', {'class': lambda x: x and 'fs16' in x and 'fwB' in x and 'dIB_m' in x})
                ]
                status

                # Obtenemos las fechas de los trabajos aplicados y los guardamos en una lista.
                fechas = [
                    fecha.get_text(strip=True)
                        for fecha in lista_jobs.find_all('p', {'class': 'fc_aux fs13 dIB_m'})
                    ]
                fechas

                # Obtenemos los links de los trabajos aplicados y los guardamos en una lista.
                links = [
                    link.get('data-shortcut-see-offer')
                    for link in lista_jobs.find_all('span', {'class': 'dB fc_base cp'})
                    if link.get('data-shortcut-see-offer') is not None
                    ]
                links 

                # Obtenemos la caducidad de los trabajos aplicados y los guardamos en una lista.
                caducidad = [
                    'Caducado' if status == 'Proceso finalizado' else None
                    for status in status
                ]


                # Adjuntamos los datos obtenidos a nuestro DataFrame:
                df_aux = pd.DataFrame(
                    {'Nombre': nombres, 
                     'Patron': patrones, 
                     'Lugar': lugares, 
                     'Estatus': status, 
                     'Caducidad': caducidad, 
                     'Fecha_Str': fechas, 
                     'Link': links})

                # Ahora unimos todos los DataFrames obtenidos en cada iteración en un solo DataFrame:
                df = pd.concat([df, df_aux], ignore_index=True)
                print(f'Iteración {i} completada. Datos obtenidos de la página {pagina_actual}.')

                # Aumentamos el contador:
                i += 1

            else:
                break 
            
        # Definimos el nombre del archivo CSV donde guardaremos los datos obtenidos anteriormente:
        archivo = OUTPUT_HISTORY / 'trabajos_aplicados_computrabajo.csv'

        # Creamos una nueva columna 'Fecha' en el DataFrame aplicando la función convertir_fecha a la columna 'Fecha_Str'.
        df['Fecha'] = df['Fecha_Str'].apply(fn.convertir_fecha_computrabajo)

        # Creamos la columna de la página de la que se extrajo la información, en este caso 'Indeed'.
        df['Pagina'] = 'Computrabajo'
        df['Caducidad'] = np.where(df['Caducidad'].isnull(), 'Sigue abierto el empleo', df['Caducidad'])
        # Ahora le damos orden a las columnas del DataFrame para que queden en el orden que queremos.
        df = df[['Nombre', 
                 'Fecha', 
                 'Patron', 
                 'Lugar', 
                 'Estatus', 
                 'Caducidad', 
                 'Pagina', 
                 'Fecha_Str', 
                 'Link']]

        # Recuperamos las fechas históricas de los trabajos aplicados:
        df = fn.recuperar_fechas_anteriores(df, archivo)

        # Guardamos el archivo actualizado:
        #df.to_csv(archivo, index=False)

        return df
    finally:
        # Guardamos el DataFrame en un archivo CSV.
        df.to_csv(OUTPUT_HISTORY / 'trabajos_aplicados_computrabajo.csv', index=False)
    
        # Esperamos un tiempo aleatorio antes de cerrar el navegador para simular un comportamiento humano y evitar ser bloqueados por la página.
        time.sleep(random.uniform(3, 5))
        browser.quit()
