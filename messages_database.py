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
        
        #Eliminar tabla de mensajes procesados para los usuariois
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS processed_user_messages""")
        conn.commit()
        #Eliminar tabla  de  recordatorios
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS trial_class_reservations""")
        conn.commit()
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
        # Crear  tabla de mensajes procesados  y resumidoos
        #cursor.execute("""
        #    CREATE TABLE IF NOT EXISTS processed_user_messages (
        #    id INTEGER PRIMARY KEY AUTOINCREMENT,
        #    whatsapp_number TEXT NOT NULL,
        #    last_processed TIMESTAMP CURRENT_TIMESTAMP,
        #    UNIQUE(whatsapp_number)
        #)
        #""")
        #conn.commit()
        #Crear tabla de recordatorios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trial_class_reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Identificador único para cada reserva
            user_id INTEGER NOT NULL,                    -- ID del usuario relacionado
            whatsapp_number TEXT NOT NULL,               -- Número de WhatsApp del usuario
            class_type TEXT NOT NULL,                    -- Tipo de clase (e.g., 'Rumba', 'Flamenco', 'Sevillanas')
            class_weekday_hour TEXT NOT NULL,
            class_date DATE NOT NULL,                    -- Fecha de la clase, en formato 'YYYY-MM-DD'
            class_time TIME NOT NULL,                    -- Hora de la clase, en formato 'HH:MM'
            reminder_sent BOOLEAN DEFAULT 0,             -- Indica si ya se envió el recordatorio (0 = No, 1 = Sí)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora de creación del registro
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Última actualización del registro
            FOREIGN KEY(user_id) REFERENCES users(id)    -- Relación con la tabla de usuarios
        )
        """)
        conn.commit()


# Inserta un nuevo usuario o recupera su ID si ya existe
def get_or_create_user(from_number, name=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Intenta buscar el usuario
        cursor.execute("SELECT id FROM users WHERE whatsapp_number = ?", (from_number,))
        result = cursor.fetchone()
        if result:
            print("Numero encontrado, id: ", result[0])
            return result[0]  # Devuelve el ID del usuario existente
        # Si no existe, lo crea tanto en tabla de usuarios como tabla de usuarios con mensajes pendientes de procesar
        #cursor.execute("INSERT INTO processed_user_messages (whatsapp_number) VALUES (?)", (from_number,))
        #conn.commit()
        cursor.execute("INSERT INTO users (whatsapp_number, name) VALUES (?, ?)", (from_number, name))
        conn.commit()
        return cursor.lastrowid  # Devuelve el ID del nuevo usuario

# Inserta un nuevo mensaje
def insert_message(user_id, from_number, whatsapp_profile, message, sender):
    print("Inserting message. Whatsapp number: ",from_number )
    print("and ")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE whatsapp_number = ?", (from_number,))
        result = cursor.fetchone()
        cursor.execute("""
        INSERT INTO messages (user_id, whatsapp_number, whatsapp_profile, message, sender)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, from_number, whatsapp_profile, message, sender))
        conn.commit()

        
# Obtiene el historial de mensajes de un usuario
def get_messages_by_user(from_number):
    print("Obteniendo mensajes del usuario")
    print(from_number)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.message, m.sender, m.timestamp
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE u.whatsapp_number = ?
        ORDER BY m.timestamp ASC
        """, (from_number,))
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

def insert_processed_messages(from_number):
    with get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("""
          INSERT INTO processed_user_messages (whatsapp_number)
          VALUES (?)
      """, (from_number,))
      conn.commit()

def update_processed_messages(from_number):
    with get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("""
      UPDATE processed_user_messages 
      SET last_processed = CURRENT_TIMESTAMP 
      WHERE whatsapp_number = ?
      """, (from_number,))
      conn.commit()
      
def set_user_messages_processed(from_number):
  with get_connection() as conn:
        cursor = conn.cursor()
        # Intenta buscar el usuario
        print(type(from_number), from_number)
        cursor.execute("SELECT id FROM processed_user_messages WHERE whatsapp_number = ?", (from_number,))
        result = cursor.fetchone()
        if result:
            print("Actualizamos mensajes procesados")
            cursor.execute("""
            UPDATE processed_user_messages 
            SET last_processed = CURRENT_TIMESTAMP 
            WHERE whatsapp_number = ?
            """, (from_number,))
            conn.commit()
        else:
            print("Creamos mensajes procesados")
            print(from_number)
            cursor.execute("INSERT INTO processed_user_messages (whatsapp_number) VALUES (?)", (from_number,))
            print("insertado antes del commit")
            conn.commit()  
            
        # Si no existe, lo crea
        
def get_unprocessed_users():
    
    #Obtiene los números de WhatsApp de los usuarios que tienen mensajes pendientes de procesamiento.
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT m.whatsapp_number as whatsapp_number
        FROM messages m
        LEFT JOIN processed_user_messages p
        ON m.whatsapp_number = p.whatsapp_number
        WHERE p.last_processed IS NULL OR m.timestamp > p.last_processed
        """)
        # Devuelve una lista de números de WhatsApp con mensajes sin procesar
        return cursor
      
def print_all_reservations():
  with get_connection() as conn:
      cursor = conn.cursor()
      # Obtener reservas del día actual sin recordatorio enviado
      cursor.execute("""
      SELECT whatsapp_number, class_type, class_weekday_hour, class_date, class_time FROM trial_class_reservations
      """)
      reservations = cursor.fetchall()  
      for res in reservations:
        whatsapp_number, class_type, class_weekday_hour, class_date, class_time = res
        reminder_message = f"Hola! Te recordamos tu clase de prueba de {class_type} hoy a las {class_time}. ¡Te esperamos!"
        print("Mensaje: ", reminder_message)
        
def get_all_reservations():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Obtener reservas del día actual sin recordatorio enviado
        cursor.execute("""
        SELECT id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time
        FROM trial_class_reservations
        """)
        
        return cursor  

def get_today_reservations():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Obtener reservas del día actual sin recordatorio enviado
        cursor.execute("""
        SELECT id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time
        FROM trial_class_reservations
        WHERE class_date = DATE('now')
          AND reminder_sent = 0;
        """)
        
        return cursor
 
def get_today_afternoon_reservations():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Obtener reservas del día actual sin recordatorio enviado
        cursor.execute("""
        SELECT id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time
        FROM trial_class_reservations
        WHERE class_date = DATE('now') AND class_time > '14:30:00'
          AND reminder_sent = 0;
        """)
        
        return cursor

def get_tomorrow_morning_reservations():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Obtener reservas del día actual sin recordatorio enviado
        cursor.execute("""
        SELECT id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time
        FROM trial_class_reservations
        WHERE class_date = DATE('now', '+1 day') AND class_time < '14:30:00'
          AND reminder_sent = 0;
        """)
        
        return cursor     


def set_reservation_to_sent(reservation_id):
    with get_connection() as conn:
        cursor = conn.cursor()     
        cursor.execute("""
        UPDATE trial_class_reservations
        SET reminder_sent = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """, (reservation_id,))
        conn.commit()
    
def insert_new_reservation(user_id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO trial_class_reservations (user_id, whatsapp_number, class_weekday_hour, class_type, class_date, class_time)
        VALUES ( ?, ?, ?, ?, ?, ?)
         """, (user_id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time))
        conn.commit()
  
def get_or_create_reservation(user_id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time):
      with get_connection() as conn:
        cursor = conn.cursor()
        # Intenta buscar el usuario
        cursor.execute("""
        SELECT id FROM trial_class_reservations 
        WHERE user_id = ? AND whatsapp_number = ? AND class_type = ? AND  class_date = ? AND class_time = ?
        """, (user_id, whatsapp_number, class_type, class_date, class_time))
        result = cursor.fetchone()
        if result:
            print("Numero encontrado, id: ", result[0])
            return result[0] 
        cursor.execute("""
        INSERT INTO trial_class_reservations (user_id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time)
        VALUES ( ?, ?, ?, ?, ?, ?)
         """, (user_id, whatsapp_number, class_type, class_weekday_hour, class_date, class_time))
        conn.commit()
        return cursor.lastrowid