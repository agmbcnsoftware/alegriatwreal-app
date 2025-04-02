import sqlite3
import messages_database
import send_whatsapps

db = messages_database

def initialize_db():
    with get_connection() as conn:
        #Eliminar tabla de mensajes procesados para los usuariois
        cursor = conn.cursor()
                cursor.execute("""
            CREATE TABLE IF NOT EXISTS trial_class_reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Identificador único para cada reserva
            user_id INTEGER NOT NULL,                    -- ID del usuario relacionado
            user_name TEXT NOT NULL,                     -- Nombre de la persona que ha hecho la reserva
            user_surname TEXT NOT NULL,                  -- Apellidos  
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
update_reservation_date(105, '2025-03-26')
#db.print_all_reservations() 
#send_whatsapps.send_reminder_by_whatsapp("whatsapp:+34658595387", "Alvaro", "SEVILLANAS", "2024-01-22", "14:55")
