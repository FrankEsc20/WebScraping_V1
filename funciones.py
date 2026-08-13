# Importamos librerias que pueden servir:
from datetime import datetime, timedelta

# Definimos una función para convertir la fecha en un formato más legible.
def convertir_fecha(fecha):
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
        