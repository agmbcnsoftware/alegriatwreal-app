import sqlite3
import messages_database
import send_whatsapps

db = messages_database
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
        
        


#db.print_all_reservations()    
#delete_reservations_from_user("whatsapp:+34625740413")
#delete_reservations_from_user_date("whatsapp:+34625740413", class_date)
#db.print_all_reservations() 
#send_whatsapps.send_reminder_by_whatsapp("whatsapp:+34658595387", "Alvaro", "SEVILLANAS", "2024-01-22", "14:55")
