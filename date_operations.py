from datetime import datetime, timedelta

def get_next_weekday_time(day_and_time, holidays):
    """
    Calcula la próxima fecha para un día y hora específicos, excluyendo días festivos.

    :param day_and_time: String con el formato 'Día HH:MMh', ej. 'Lunes 20:00h'
    :param holidays: Lista de fechas festivas en formato 'YYYY-MM-DD'
    :return: Tupla con la fecha (YYYY-MM-DD) y hora (HH:MM)
    """
    # Mapeo de días de la semana
    days_map = {
        "Lunes": 0, "Martes": 1, "Miércoles": 2, "Miercoles": 2,
        "Jueves": 3, "Viernes": 4, "Sábado": 5, "Sabado": 5, "Domingo": 6
    }
    
    # Separar el día y la hora
    day, time = day_and_time.split()
    hour, minute = map(int, time.replace("h", "").split(":"))
    
    # Obtener la fecha y hora actual
    now = datetime.now()
    target_day = days_map[day]  # Día de la semana objetivo

    # Fecha inicial objetivo
    target_date = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Calcular el siguiente día objetivo
    days_ahead = (target_day - now.weekday()) % 7
    if days_ahead == 0 and target_date < now:  # Si es hoy pero ya pasó la hora
        days_ahead += 7
    target_date += timedelta(days=days_ahead)

    # Excluir festivos
    holidays_set = set(holidays)  # Convertir la lista a un conjunto para eficiencia
    while target_date.strftime("%Y-%m-%d") in holidays_set:
        target_date += timedelta(days=7)  # Sumar una semana completa al mismo día
    
    # Devolver el resultado
    date_str = target_date.strftime("%Y-%m-%d")
    time_str = target_date.strftime("%H:%M")
    return date_str, time_str


# Ejemplo de uso
holidays = ["2024-06-03", "2024-06-10", "2024-06-17"]  # Lista de festivos en formato 'YYYY-MM-DD'
print(get_next_weekday_time("Lunes 20:00h", holidays))  # Excluye festivos
print(get_next_weekday_time("Miércoles 18:45h", holidays))
