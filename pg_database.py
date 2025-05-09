import psycopg2
from psycopg2 import pool

def get_db_connection():
    conn = psycopg2.connect(
        host='crossover.proxy.rlwy.net',  # Tu host
        port=55419,                       # Puerto específico
        database='railway',             # Reemplaza con el nombre de tu base de datos
        user='postgres',                  # Tu usuario
        password='tu_contraseña'          # Reemplaza con tu contraseña
    )
    conn.autocommit = True
    
    # Establecer el esquema específico
    with conn.cursor() as cur:
        cur.execute("SET search_path TO Alegria")  # Reemplaza 'tu_esquema' con el nombre de tu esquema
    
    return conn
