import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta, date
import os

# Variables de entorno
pg_host = "crossover.proxy.rlwy.net"
pg_user = "postgres"
pg_pwd = "kNcuqlRsCPWmtqiMzDtmxhhyTYomOjTt"
pg_port = "5432"
pg_database = "railway"

def get_variables_info():
    """Función simple para mostrar variables sin conectar"""
    return {
        'pg_host': pg_host,
        'pg_user': pg_user,
        'pg_port': pg_port,
        'pg_database': pg_database,
        'pg_pwd_set': bool(pg_pwd),
        'pg_pwd_length': len(pg_pwd) if pg_pwd else 0
    }

def get_db_connection():
    pg_host = "crossover.proxy.rlwy.net"
    pg_user = "postgres"
    pg_pwd = "kNcuqlRsCPWmtqiMzDtmxhhyTYomOjTt"
    pg_port = "5432"
    pg_database = "railway"
    print(f"=== DEBUGGING VARIABLES ===")
    print(f"PG_HOST: '{pg_host}' (tipo: {type(pg_host)})")
    print(f"PG_PORT: '{pg_port}' (tipo: {type(pg_port)})")
    print(f"PG_USER: '{pg_user}' (tipo: {type(pg_user)})")
    print(f"PG_DATABASE: '{pg_database}' (tipo: {type(pg_database)})")
    print(f"PG_PWD existe: {bool(pg_pwd)} (longitud: {len(pg_pwd) if pg_pwd else 0})")
    print(f"=== FIN DEBUG ===")

    try:
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            database=pg_database,
            user=pg_user,
            password=pg_pwd
        )
        print("✅ Conexión establecida exitosamente")
        
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print(f"Versión de PostgreSQL: {db_version}")
        
        return conn
      
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        raise

def get_filtered_messages(filter_option):
    print(f"=== get_filtered_messages llamada con: {filter_option} ===")
    
    query = 'SELECT u.whatsapp_number, u.whatsapp_profile, m.message, m.timestamp, m.sender FROM "Alegria".messages m JOIN "Alegria".users u ON m.user_id = u.id'
    params = []
    now = datetime.now()
    
    if filter_option == "today":
        print("Filtro: Today")
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "yesterday":
        print("Filtro: Yesterday")
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "last7days":
        print("Filtro: Last 7 days")
        start_date = now - timedelta(days=7)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "lastmonth":
        print("Filtro: Last month")
        start_date = now - timedelta(days=30)
        end_date = now
        query += " WHERE m.timestamp BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif filter_option == "all":
        print("Filtro: All")
        pass
    else:
        print(f"❌ Opción de filtro no válida: {filter_option}")
        raise ValueError(f"Opción de filtro no válida: {filter_option}")
    
    query += ' ORDER BY m.timestamp ASC'
    print(f"Query ejecutada: {query}")
    print(f"Parámetros: {params}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        print(f"✅ Resultados obtenidos: {len(results)} filas")
        conn.close()
        return results
    
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta: {str(e)}")
        return None

def get_filtered_reservations(filter_option):
    print(f"=== get_filtered_reservations llamada con: {filter_option} ===")
    
    query = 'SELECT r.id, u.first_name, u.last_name, u.whatsapp_number, r.class_type, r.class_schedule, r.class_date, r.reminder_sent, r.created_at FROM "Alegria".trial_class_reservations r JOIN "Alegria".users u ON r.user_id = u.id'
    params = []
    
    today = date.today().isoformat()
    now = datetime.now()
    
    if filter_option == 'next_reservations':
        print("Filtro: Next reservations")
        query += " WHERE r.class_date >= %s"
        params = [today]
    elif filter_option == 'yesterday_reservations':
        print("Filtro: Yesterday reservations")
        yesterday = (now - timedelta(days=1)).date().isoformat()
        query += " WHERE r.created_at >= %s"
        params = [yesterday]
    elif filter_option == 'all':
        print("Filtro: All reservations")
        pass
    else:
        print(f"❌ Opción de filtro no válida: {filter_option}")
   
    query += " ORDER BY r.created_at DESC"
    print(f"Query ejecutada: {query}")
    print(f"Parámetros: {params}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        print(f"✅ Resultados obtenidos: {len(results)} filas")
        conn.close()
        return results
    
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta: {str(e)}")
        return None
        
