###########################################################################################################################################
# Importamos las librerías necesarias para el web scraping y el manejo de datos.
###########################################################################################################################################
import requests
from bs4 import BeautifulSoup as bs
import random
import time
import pandas as pd
import numpy as np
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

#############################################################################################################################################

#HEADERS = {
#    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
#    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
#    'Accept-Language': 'en-US,en;q=0.9',
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#}

###########################################################################################################################################
# Empezamos por Indeed:
###########################################################################################################################################
# Abrimos el navegador, iniciamos sesion con el correo sin usar google paara que no nos bloquee el inicio de sesion.
def ejecutar_indeed():
    browser = webdriver.Chrome()

    try:
        browser.get('https://myjobs.indeed.com/applied')

        # Esperamos a que el usuario termine de autenticarse manualmente.
        # Selenium continuará automáticamente cuando aparezca al menos un trabajo aplicado.
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(browser, 300).until(
            lambda driver: driver.find_elements(By.CSS_SELECTOR, 'header.atw-JobInfo')
        )

        # Esperamos un intervalo aleatorio para permitir que la página termine de cargar su contenido.
        time.sleep(random.uniform(2, 5))

        #Obtenemos el HTML de la página
        html = browser.page_source
        # Le damos un mejor formato al HTML para poder analizarlo mejor
        soup = bs(html, 'html.parser')

        #Obtenemos el primer trabajo de la lista de trabajos aplicados:
        job = soup.find('header', {'class': 'atw-JobInfo'}).find('a', {'class': 'atw-JobInfo-jobTitle'}).find(string=True, recursive=False).strip()


        # Ahora pasamos a conseguir la lista de trabajos aplicados y sus links para poder acceder a ellos y obtener la información que necesitamos.
        jobs = soup.find_all('header', {'class': 'atw-JobInfo'})
        # Ahora obtenemos el status de los trabajos aplicados y los guardamos en una lista.
        status = [job.find('div', {'class': 'atw-JobInfo-statusTag'}).find(string=True).strip() for job in jobs]
        # Ahora obtenemos los nombres de los trabajos aplicados y los guardamos en una lista.
        nombres = [job.find('a', {'class': 'atw-JobInfo-jobTitle'}).find(string=True, recursive=False).strip() for job in jobs]
        # Obtenemos los links de los trabajos aplicados y los guardamos en una lista.
        links = [job.find('a', {'class': 'atw-JobInfo-jobTitle'})['href'] for job in jobs]
        #Obtenemos los patrones de los trabajos aplicados y los guardamos en una lista.
        patrones = [job.find('div', {'class': 'atw-JobInfo-companyLocation'}).find(string=True).strip() for job in jobs]
        #Obtenemos los lugares de los trabajos aplicados y los guardamos en una lista.
        lugares = [job.find('div', {'class': 'atw-JobInfo-companyLocation'}).find_all(string=True)[1].strip() for job in jobs]
        #Obtenemos las fechas de los trabajos aplicados y los guardamos en una lista.
        fechas = [job.find('div', {'class': 'css-1afmp4o e37uo190'}).find_all(string=True)[0].strip() for job in jobs]

        # Traemos igual todos los div con el estatus de los trabajos aplicados para poder obtener la caducidad de los mismos.
        div_status = soup.find_all('div', {'class': 'atw-AppliedJobActions-labels'})

        #Obtenemos la caducidad de los trabajos aplicados y los guardamos en una lista.
        caducidad = [div.find('div', {'class': 'atw-JobWarningLabel-text'}).get_text(strip=True)
            if div.find('div', {'class': 'atw-JobWarningLabel-text'})
            else None
            for div in div_status
        ]


        ###########################################################################################################################################
        #Creamos un DataFrame con la información obtenida.
        df = pd.DataFrame({'Nombre': nombres, 'Patron': patrones, 'Lugar': lugares, 'Estatus': status, 'Caducidad': caducidad, 'Fecha_Str': fechas, 'Link': links})
        # Creamos una nueva columna 'Fecha' en el DataFrame aplicando la función convertir_fecha a la columna 'Fecha_Str'.
        df['Fecha'] = df['Fecha_Str'].apply(fn.convertir_fecha_indeed)
        # Creamos la columna de la página de la que se extrajo la información, en este caso 'Indeed'.
        df['Pagina'] = 'Indeed'
        df['Caducidad'] = np.where(df['Caducidad'].isnull(), 'Sigue abierto el empleo', df['Caducidad'])
        # Ahora le damos orden a las columnas del DataFrame para que queden en el orden que queremos.
        df = df[['Nombre', 'Fecha', 'Patron', 'Lugar', 'Estatus', 'Caducidad', 'Pagina', 'Fecha_Str', 'Link']]
        return df
    finally:
        # Guardamos el DataFrame en un archivo CSV.
        #df.to_csv('trabajos_aplicados.csv', index=False)
    
        # Esperamos un tiempo aleatorio antes de cerrar el navegador para simular un comportamiento humano y evitar ser bloqueados por la página.
        time.sleep(random.uniform(3, 5))
        browser.quit()
