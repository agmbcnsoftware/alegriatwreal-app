from datetime import datetime, timedelta

def load_holidays():
    """
    Carga los días festivos desde un archivo de texto.

    Args:
        file_path (str): Ruta al archivo que contiene los días festivos.

    Returns:
        list: Lista de días festivos en formato 'YYYY-MM-DD'.
    """
    file_path = 'holidays.txt'
    print('a')
    try:
        with open(file_path, 'r') as file:
            holidays = file.read().strip().split(',')
            return [date.strip() for date in holidays if date.strip()]
    except FileNotFoundError:
        print(f"Archivo {file_path} no encontrado. No se cargarán días festivos.")
        return []

def get_next_weekday_time(day_time_string):
    """
    Calcula la próxima fecha y hora en que ocurre el día y hora especificado, excluyendo días festivos.

    Args:
        day_time_string (str): Cadena en el formato 'Día de HH:MMh a HH:MMh'.
        holidays_file (str): Ruta al archivo de días festivos.

    Returns:
        str: La fecha y hora en formato 'YYYY-MM-DD HH:MM'.
    """
    # Cargar días festivos
    holidays = load_holidays()

    # Parsear el día y la hora de inicio
    parts = day_time_string.split(" de ")
    day_of_week = parts[0].strip()  # 'Lunes'
    start_time = parts[1].split(" a ")[0].strip()  # '16:15h'

    # Remover la 'h' final de la hora
    start_time = start_time.replace('h', '')

    # Mapear nombres de días en español a índices de días de la semana
    weekdays = {
        'Lunes': 0,
        'Martes': 1,
        'Miércoles': 2,
        'Jueves': 3,
        'Viernes': 4,
        'Sábado': 5,
        'Domingo': 6,
    }

    # Obtener el índice del día de la semana correspondiente
    target_weekday = weekdays[day_of_week]

    # Obtener la fecha y hora actual
    now = datetime.now()

    # Calcular la próxima ocurrencia del día y hora objetivo
    days_ahead = (target_weekday - now.weekday()) % 7
    if days_ahead == 0 and now.time() > datetime.strptime(start_time, "%H:%M").time():
        days_ahead = 7

    next_date = now + timedelta(days=days_ahead)
    next_date = next_date.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=0, microsecond=0)

    # Verificar si la fecha calculada cae en un día festivo y ajustar
    while next_date.strftime('%Y-%m-%d') in holidays:
        next_date += timedelta(days=7)

    # Formatear la fecha y hora
    return next_date.strftime('%Y-%m-%d %H:%M')

