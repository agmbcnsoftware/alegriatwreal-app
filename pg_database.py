import psycopg2
from psycopg2 import pool

pg_host = os.getenv("PG_HOST")
pg_user = os.getenv("DB_USER")
pg_pwd = os.getenv("DB_PWD")
pg_port = os.getenv("DB_PORT")

def get_db_connection():
    conn = psycopg2.connect(
        host = pg_host,  # Tu host
        port = pg_port,                       # Puerto específico
        database ='railway',             # Reemplaza con el nombre de tu base de datos
        user = pg_user,                  # Tu usuario
        password = pg_pwd          # Reemplaza con tu contraseña
    )
    conn.autocommit = True
    
    # Establecer el esquema específico
   
