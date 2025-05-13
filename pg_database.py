import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta
import os

pg_host = os.getenv("PG_HOST")
pg_user = os.getenv("DB_USER")
pg_pwd = os.getenv("DB_PWD")
pg_port = os.getenv("DB_PORT")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host = 'crossover.proxy.rlwy.net',  # Tu host
            port = 55419,                       # Puerto específico
            database ='railway',             # Reemplaza con el nombre de tu base de datos
            user = 'postgres',                  # Tu usuario
            password = 'kNcuqlRsCPWmtqiMzDtmxhhyTYomOjTt'          # Reemplaza con tu contraseña
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
    
    #postgresql://postgres:kNcuqlRsCPWmtqiMzDtmxhhyTYomOjTt@crossover.proxy.rlwy.net:55419/railway
    
   
def get_filtered_messages2(filter_option):
    
    query = 'SELECT whatsapp_number, whatsapp_profile, message, timestamp, sender FROM "Alegria".messages'
    params = []
    print("n8nMensajes")
    # Obtener fechas basadas en la opción de filtro
    now = datetime.now()
    
    if filter_option == "today":
        print("Today")
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "yesterday":
        print("Yesterday")
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "last7days":
        start_date = now - timedelta(days=7)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "lastmonth":
        start_date = now - timedelta(days=30)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "all":
        # Sin condiciones adicionales, selecciona todos los mensajes
        pass
    else:
        raise ValueError(f"Opción de filtro no válida: {filter_option}")
    print("Query:")
    print(query)
    # Ejecutar la consulta
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT whatsapp_number, whatsapp_profile, message, timestamp, sender FROM "Alegria".messages'
    #cursor.execute(query, params)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
  
  
  #--------------------------
def get_filtered_messages(filter_option):
    
    #query = 'SELECT whatsapp_number, whatsapp_profile, message, timestamp, sender FROM "Alegria".messages'
    query = 'SELECT u.whatsapp_number, u.whatsapp_profile, m.message, m.timestamp, m.sender FROM "Alegria".messages m JOIN "Alegria".users u ON m.user_id = u.id'
    
    now = datetime.now()
    
    if filter_option == "today":
        print("Today")
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "yesterday":
        print("Yesterday")
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "last7days":
        start_date = now - timedelta(days=7)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "lastmonth":
        start_date = now - timedelta(days=30)
        end_date = now
        query += " WHERE timestamp BETWEEN %s AND %s"
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
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        # También puedes registrar el error en un archivo log
        return None
    
   
 
        