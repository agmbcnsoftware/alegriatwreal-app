import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta, date
import os

pg_host = os.getenv("PG_HOST")
pg_user = os.getenv("PG_USER")
pg_pwd = os.getenv("PG_PWD")
pg_port = os.getenv("PG_PORT")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host = pg_host,  # Tu host
            port = 55419,                       # Puerto específico
            database ='railway',             # Reemplaza con el nombre de tu base de datos
            user = 'postgres',                  # Tu usuario
            password = pg_pwd          # Reemplaza con tu contraseña
        )
        print("Conexión establecida exitosamente")
        
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print(f"Versión de PostgreSQL: {db_version}")
        
        return conn
      
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        raise
        
    # Establecer el esquema específico
    

def get_filtered_messages(filter_option):
    
    #query = 'SELECT whatsapp_number, whatsapp_profile, message, timestamp, sender FROM "Alegria".messages'
    query = 'SELECT u.whatsapp_number, u.whatsapp_profile, m.message, m.timestamp, m.sender FROM "Alegria".messages m JOIN "Alegria".users u ON m.user_id = u.id'
    params = []
    now = datetime.now()
    
    if filter_option == "today":
        print("Today")
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "yesterday":
        print("Yesterday")
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "last7days":
        start_date = now - timedelta(days=7)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "lastmonth":
        start_date = now - timedelta(days=30)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "all":
        # Sin condiciones adicionales, selecciona todos los mensajes
        pass
    else:
        raise ValueError(f"Opción de filtro no válida: {filter_option}")
    
    query +=' ORDER BY m.timestamp DESC'
    # Obtener fechas basadas en la opción de filtro
    print("Query:")
    print(query)
    # Ejecutar la consulta
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query,params)
        results = cursor.fetchall()
        return results
    
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        # También puedes registrar el error en un archivo log
        return None
    
   
def get_filtered_reservations(filter_option):    
    query = 'SELECT r.id, u.first_name, u.last_name, u.whatsapp_number, r.class_type, r.class_schedule, r.class_date, r.reminder_sent, r.created_at FROM "Alegria".trial_class_reservations r JOIN "Alegria".users u ON r.user_id = u.id'
    params = []
    
    # Obtener fechas basadas en la opción de filtro
    today = date.today().isoformat()
    now = datetime.now()
    
    #if filter_option == "next_reservations":
    #    query += " WHERE class_date >= ? ORDER BY class_date ASC"
    #    params = [today]
    #elif filter_option == "yesterday_reservations":
    #    start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    #    query += " WHERE created_at >= ?"
    #    params = [start_date]
    #elif filter_option == "all":
    #    # Sin condiciones adicionales, selecciona todos los mensajes
    #    pass
    
    print(query)
    # Ejecutar la consulta
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query,params)
        results = cursor.fetchall()
        return results
    
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        # También puedes registrar el error en un archivo log
        return None
        