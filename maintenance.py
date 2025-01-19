import sqlite3
import messages_database

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


#db.print_all_reservations()    
delete_reservations_from_user("whatsapp:+34625740413")
db.print_all_reservations() 