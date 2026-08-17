
# Importamos librerias que pueden servir:
import os
import re
import pandas as pd
from datetime import datetime, timedelta
from datetime import datetime, timedelta


# Definimos una función para convertir la fecha en un formato más legible.
def convertir_fecha_indeed(fecha):
    dias_semana = {
        "lunes": 0,
        "martes": 1,
        "miércoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sábado": 5,
        "domingo": 6
    }

    meses = {
        "ene": 1,
        "feb": 2,
        "mar": 3,
        "abr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "ago": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dic": 12
    }

    fecha = fecha.lower().strip()
    hoy = datetime.today()

    # Si la postulación fue hoy, devolvemos la fecha de hoy.
    if "hoy" in fecha:
        return hoy.date()

    # Si la postulación fue ayer, devolvemos la fecha de ayer.
    if "ayer" in fecha and "anteayer" not in fecha and "antier" not in fecha:
        return (hoy - timedelta(days=1)).date()

    # Si la postulación fue anteayer, devolvemos la fecha de anteayer.
    if "antier" in fecha or "anteayer" in fecha:
        return (hoy - timedelta(days=2)).date()

    # Fecha expresada como día de la semana
    for dia, numero in dias_semana.items():
        if dia in fecha:
            diferencia = (hoy.weekday() - numero) % 7
            return (hoy - timedelta(days=diferencia)).date()

    # Fecha expresada como día y mes
    try:
        fecha_texto = fecha.split(" el ")[-1]
        fecha_texto = fecha_texto.replace(".", "").strip()

        dia, mes = fecha_texto.split(" de ")

        dia = int(dia)
        mes = meses[mes]

        fecha_candidata = datetime(hoy.year, mes, dia)

        # Si todavía no ha ocurrido este año,
        # asumimos que pertenece al año anterior.
        if fecha_candidata.date() > hoy.date():
            fecha_candidata = datetime(hoy.year - 1, mes, dia)

        return fecha_candidata.date()

    except (ValueError, KeyError):
        return None



# Función para convertir la fecha de Computrabajo a formato datetime:
def convertir_fecha_computrabajo(fecha_str):
    """
    Convierte las fechas obtenidas de Computrabajo a formato datetime.
    """

    fecha_str = fecha_str.strip().lower()
    ahora = datetime.now()

    # Caso: "Más de 30 días"
    if "más de 30 días" in fecha_str:
        return None

    # Caso: "Hace X horas"
    match_horas = re.search(r'hace\s+(\d+)\s+horas?', fecha_str)

    if match_horas:
        horas = int(match_horas.group(1))
        return (ahora - timedelta(hours=horas)).date()

    # Caso: "Hace X días"
    match_dias = re.search(r'hace\s+(\d+)\s+días?', fecha_str)

    if match_dias:
        dias = int(match_dias.group(1))
        return (ahora - timedelta(days=dias)).date()

    # Caso: "6 de agosto"
    match_fecha = re.search(
        r'(\d{1,2})\s+de\s+([a-záéíóú]+)',
        fecha_str
    )

    if match_fecha:
        dia = int(match_fecha.group(1))
        mes_nombre = match_fecha.group(2)

        meses = {
            'enero': 1,
            'febrero': 2,
            'marzo': 3,
            'abril': 4,
            'mayo': 5,
            'junio': 6,
            'julio': 7,
            'agosto': 8,
            'septiembre': 9,
            'octubre': 10,
            'noviembre': 11,
            'diciembre': 12
        }

        mes = meses.get(mes_nombre)

        if mes:
            return datetime(ahora.year, mes, dia).date()

    # Si no se reconoce el formato
    return None


# Función para recuperar las fechas históricas de los trabajos aplicados:
def recuperar_fechas_anteriores(df, archivo_anterior):
    """
    Recupera las fechas históricas de los trabajos que actualmente
    tienen Fecha = None, utilizando el Link como identificador.
    """

    if not os.path.exists(archivo_anterior):
        return df

    df_anterior = pd.read_csv(archivo_anterior)

    fechas_anteriores = (
        df_anterior
        .dropna(subset=['Fecha'])
        .drop_duplicates(subset=['Link'])
        .set_index('Link')['Fecha']
        .to_dict()
    )

    df['Fecha'] = df.apply(
        lambda fila: fechas_anteriores.get(fila['Link'], fila['Fecha'])
        if pd.isna(fila['Fecha'])
        else fila['Fecha'],
        axis=1
    )

    return df