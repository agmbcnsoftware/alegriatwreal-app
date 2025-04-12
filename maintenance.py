import sqlite3
import messages_database
import send_whatsapps

db = messages_database

def create_prospects_table():
    with db.get_connection() as conn:
        #Crear la tabla de prospects
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospects_reservation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Identificador único para cada usuario
            user_id INTEGER NOT NULL,                    -- ID del usuario relacionado
            user_name TEXT NOT NULL,                     -- Nombre de la persona que ha hecho la reserva
            user_surname TEXT NOT NULL,                  -- Apellidos  
            whatsapp_number TEXT NOT NULL,               -- Número de WhatsApp del usuario
            user_email TEXT NOT NULL,                    -- Email del usuario
            class_type TEXT NOT NULL,                    -- Tipo de clase (e.g., 'Rumba', 'Flamenco', 'Sevillanas')
            class_date DATE NOT NULL,                    -- Fecha de la clase, en formato 'YYYY-MM-DD'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora de creación del registro
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Última actualización del registro
            FOREIGN KEY(user_id) REFERENCES users(id)    -- Relación con la tabla de usuarios
        )
        """)
        conn.commit()
        
def insert_new_propect(user_id, user_name, user_surname, whatsapp_number, user_email, class_type, class_date):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO propects_reservations (user_id, user_name, user_surname, whatsapp_number, class_weekday_hour, class_type, class_date, class_time)
        VALUES ( ?, ?, ?, ?, ?, ?, ?)
         """, (user_id, user_name, user_surname, whatsapp_number, user_email, class_type, class_date))
        conn.commit()


def delete_reservations_from_user(from_number):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM trial_class_reservations
        WHERE whatsapp_number = ?
        """, (from_number,))
        conn.commit()
        print(f"Mensajes eliminados para el número: {from_number}")

def delete_reservations_from_user_date(from_number, class_date):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM trial_class_reservations
        WHERE whatsapp_number = ? and class_date = ?
        """, (from_number, class_date))
        conn.commit()
        print(f"Mensajes eliminados para el número: {from_number} y fecha: {class_date}")
        
def update_reservation_date(reservation_id, reservation_date):
    with db.get_connection() as conn:
        cursor = conn.cursor()     
        cursor.execute("""
        UPDATE trial_class_reservations
        SET reminder_sent = 0, class_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """, (reservation_date, reservation_id,))
        conn.commit()
        


#db.print_all_reservations()    
#delete_reservations_from_user("whatsapp:+34625740413")
#delete_reservations_from_user_date("whatsapp:+34667285233", "2025-01-27")
#update_reservation_date(105, '2025-03-26')
#db.print_all_reservations() 
#send_whatsapps.send_reminder_by_whatsapp("whatsapp:+34658595387", "Alvaro", "SEVILLANAS", "2024-01-22", "14:55")
#create_prospects_table()
