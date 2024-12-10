import sqlite3
import os

# Ruta para la base de datos
DB_PATH = "GraciaBot.db"

# Inicializa la conexión con la base de datos
def get_connection():
    return sqlite3.connect(DB_PATH)
  
def update_db_structure():
  print("Actualizando tablas")

# Crea las tablas si no existen
def initialize_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        #Eliminar tabla de mensajes
        cursor.execute("""DROP TABLE IF EXISTS messages""")
        conn.commit()
        #Eliminar tabla de usuarios
        cursor.execute("""DROP TABLE IF EXISTS users""")
        conn.commit()
        # Crear tabla de usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_number TEXT UNIQUE NOT NULL,
            name TEXT
        )
        """)
        conn.commit()
        # Crear tabla de mensajes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            whatsapp_number TEXT NOT NULL,
            whatsapp_profile TEXT NOT_NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender TEXT NOT NULL, -- 'user' o 'bot'
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        conn.commit()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_user_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_number TEXT NOT NULL,
            last_processed TIMESTAMP DEFAULT NULL,
            UNIQUE(whatsapp_number)
        )
        """)
        conn.commit

# Inserta un nuevo usuario o recupera su ID si ya existe
def get_or_create_user(whatsapp_number, name=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Intenta buscar el usuario
        cursor.execute("SELECT id FROM users WHERE whatsapp_number = ?", (whatsapp_number,))
        result = cursor.fetchone()
        if result:
            print("Numero encontrado")
            return result[0]  # Devuelve el ID del usuario existente
        # Si no existe, lo crea
        cursor.execute("INSERT INTO users (whatsapp_number, name) VALUES (?, ?)", (whatsapp_number, name))
        conn.commit()
        return cursor.lastrowid  # Devuelve el ID del nuevo usuario

# Inserta un nuevo mensaje
def insert_message(user_id, whatsapp_number, whatsapp_profile, message, sender):
    print("Inserting message")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE whatsapp_number = ?", (whatsapp_number,))
        result = cursor.fetchone()
        print("Obteniendo todo sobre mensajes")
        #print(result)
        cursor.execute("""
        INSERT INTO messages (user_id, whatsapp_number, whatsapp_profile, message, sender)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, whatsapp_number, whatsapp_profile, message, sender))
        conn.commit()

                      
# Obtiene el historial de mensajes de un usuario
def get_messages_by_user(whatsapp_number):
    print("Obteniendo mensajes del usuario")
    print(whatsapp_number)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.message, m.sender, m.timestamp
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE u.whatsapp_number = ?
        ORDER BY m.timestamp ASC
        """, (whatsapp_number,))
        return cursor
        
# Elimina los mensajes de un usuario que lo ha solicitado

def delete_messages_from_user(from_number):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM messages
        WHERE whatsapp_number = ?
        """, (from_number,))
        conn.commit()
        print(f"Mensajes eliminados para el número: {from_number}")