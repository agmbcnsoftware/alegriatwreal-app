import sqlite3



def delete_reservations_from_user(from_number):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM trial_class_reservations
        WHERE whatsapp_number = ?
        """, (from_number,))
        conn.commit()
        print(f"Mensajes eliminados para el número: {from_number}")

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
        reminder_message = f"Telefono {whatsapp_number} Clase de prueba de {class_type} a las {class_time}."
        print("Mensaje: ", reminder_message)

print_all_reservations()    
delete_reservations_from_user("whatsapp:+34658595387")
print_all_reservations() 