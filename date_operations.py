from datetime import datetime, timedelta
import re

def load_holidays():
    """
    Carga una lista de días festivos desde un archivo proporcionado.
    
    :param holidays_file: Ruta al archivo que contiene las fechas de días festivos (formato YYYY-MM-DD, separados por comas).
    :return: Lista de objetos date correspondientes a los días festivos.
    """
    file_path = 'holidays.txt'
    with open(file_path, 'r') as file:
        holidays = file.read().split(',')
        return [datetime.strptime(h.strip(), "%Y-%m-%d").date() for h in holidays]

def get_next_weekday_time(schedule_string, holidays_file=None):
    """
    Calcula la próxima fecha y hora basándose en un string de horario
    soportando múltiples formatos.
    """
    # Expresión regular para capturar los diferentes formatos
    match = re.match(
        r"(?i)(\w+)(?: de| a las)? (\d{1,2}[.:]\d{2})(?:h)?(?: a \d{1,2}[.:]\d{2}(?:h)?)?",
        schedule_string
    )
    if not match:
        raise ValueError(f"Formato de horario no válido: {schedule_string}")

    # Extraer el día y la hora de inicio
    day_name, start_time = match.groups()

    # Reemplazar '.' con ':' en la hora, si es necesario
    start_time = start_time.replace('.', ':')

    # Mapear días a índices
    days_of_week = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6
    }
    day_name = day_name.lower()
    if day_name not in days_of_week:
        raise ValueError(f"Día de la semana no reconocido: {day_name}")

    target_weekday = days_of_week[day_name]

    # Obtener la fecha y hora actual
    now = datetime.now()

    # Calcular la fecha objetivo
    current_weekday = now.weekday()
    days_until_target = (target_weekday - current_weekday) % 7
    if days_until_target == 0 and now.time() > datetime.strptime(start_time, "%H:%M").time():
        days_until_target = 7

    next_date = now + timedelta(days=days_until_target)

    # Combinar fecha y hora
    next_datetime = datetime.strptime(f"{next_date.date()} {start_time}", "%Y-%m-%d %H:%M")

    # Manejar festivos si se proporciona un archivo
    
    holidays = load_holidays()

    while next_datetime.date() in holidays:
        next_datetime += timedelta(days=7)

    # Retornar en el formato deseado
    return next_datetime.strftime("%Y-%m-%d"), next_datetime.strftime("%H:%M")

def get_spanish_weekday(class_date):
    days_translation = {
        "Monday": "lunes",
        "Tuesday": "martes",
        "Wednesday": "miércoles",
        "Thursday": "jueves",
        "Friday": "viernes",
        "Saturday": "sábado",
        "Sunday": "domingo"
    }
    date_object = datetime.datetime.strptime(class_date, "%Y-%m-%d")
    class_weekday_eng = date_object.strftime("%A")
    class_weekday_spa =  days_translation.get(class_weekday_eng,class_weekday_eng)  
    return class_weekday_spa