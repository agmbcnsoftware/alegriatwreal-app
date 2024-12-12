from flask import Flask, jsonify, request
from twilio.rest import Client
from openai import OpenAI
from cryptography.fernet import Fernet
import os
import threading
import schedule
import time
import datetime
import messages_database

app = Flask(__name__)

# Configuración de Twilio
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")  # Ejemplo: 'whatsapp:+14155238886'
twilio_client = Client(account_sid, auth_token)
encryption_key = os.environ.get("AI_INFO_KEY")
admin_number = "whatsapp:+651090177"

#Configuración de opeAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#Obtengo la información específica que hay en ai-knowledge-base.txt
cipher = Fernet(encryption_key.encode())

# Leer y desencriptar el contenido del archivo
with open("ai-info-base.txt", "r") as f:
    encrypted_content = f.read()
base_context = cipher.decrypt(encrypted_content).decode()

print(base_context[0:40])

# Diccionario para el historial de conversaciones
conversations = {}
db = messages_database
#db.initialize_database()

# El sistema tiene tres procesos, 1) la web app 2) un proceso que se arrancará a ciertas horas para
# repasar el estado de las conversaciones y notificar al administrador, finalmente un proceso que 
# se encargará de enviar notificaciones a las personas que han pedido una clase de prueba, para 
# que no se olviden

def start_web_server():
    app.run(host='0.0.0.0', port=3000)

def process_conversations():
    print("Procesando conversaciones...")
    num_cursor = db.get_unprocessed_users()
    for row in num_cursor.fetchall():
        whatsapp_number = row[0]
        print ("Mensajes pendientes de procesar para ", whatsapp_number)
        #Inicializo messsages con con el prompt para la IA pidiendole  uun resumen
        summary_prompt = """Eres un asistente experto en procesar conversaciones. A continuación, recibirás una transcripción completa entre un usuario y un bot. 
        Tu tarea es resumir la conversación, con mucha brevedad incluyendo el nombre del usuario en el caso en que dispongas de él y analizar si el usuario ha reservado una clase de prueba. """         
        messages = [{"role": "system", "content" : summary_prompt }]          
        msg_cursor = db.get_messages_by_user(whatsapp_number)
        for message, sender, timestamp in msg_cursor.fetchall():            
            messages.append({"role": sender, "content": message})
            #print(messages)
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages = messages)
        for choice in response.choices:
            messages.append({"role": "assistant", "content": choice.message.content})
        response_message = response.choices[0].message.content   
        print(response_message, "Número: ", whatsapp_number)
        #Mandamos la respuesta a través de Twilio al telefono del admin
        message = twilio_client.messages.create(
            from_=twilio_number,
            body = response_message,
            to = admin_number
        )
        #Apunto que ya he procesado los mensajes de este usuario
        db.update_processed_messages(whatsapp_number)
        time.sleep(1)
    print("Conversaciones procesadas")

def notify_appointments():
    print("Enviando notificaciones)") 
    
    res_cursor  =  db.get_today_reservations()
    reservations = res_cursor.fetchall()
    for res in reservations:
        reservation_id, whatsapp_number, class_type, class_date, class_time = res
        reminder_message = f"Hola! Te recordamos tu clase de prueba de {class_type} hoy a las {class_time}. ¡Te esperamos!"
        print("Mensaje: ", reminder_message)
        message = twilio_client.messages.create(
            from_=twilio_number,
            body = remminder_message,
            to = whatsaapp_number
        )
        db.set_reservation_to_sent(reservation_id)
        time.sleep(1) 
    print("Notificaciones enviadas")   
    
def start_conversations_processing():
    print("Thread for conversation running")
    schedule.every().day.at("11:50").do(process_conversations)
    #schedule.every().minute.at(":23").do(process_conversations)
    while True:
        schedule.run_pending()
        time.sleep(1)       
        
        
def start_appointment_notifications():
    #print("Thread for notifications running")
    schedule.every().day.at("08:00").do(notify_appointments)
    schedule.every().minute.at(":23").do(notify_appointments)
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.route("/")
def home():
    return "Hello World!"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received webhook")
    try:
        data = request.form

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extraer información del mensaje
        incoming_message = data.get("Body", "").strip()
        from_number = data.get("From")  # Número del remitente
        profile_name = data.get("ProfileName", "").strip() # Nombre que se ha puesto en WhatsApp
        
        # Si el mensaje tiene el literal Olvídame eliminamos todos los mensajes del usuario y ya está
        if (incoming_message == "Olvidame"):
            db.delete_messages_from_user(from_number)
            return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
        
        #Tengo a este cliente en base de datos? busco conversaciones por su número
        # Si lo tengo las cargo
        user_id = db.get_or_create_user(from_number)
        db.insert_message(user_id, from_number, profile_name, incoming_message, "user")     
        #Cargo la información básica, el prompt pra la IA desde cero
        messages = [{"role": "system", "content" : base_context}]
        #Obtengo de la base de datos los mensajes del usuario
        cursor = db.get_messages_by_user(from_number)
        for message, sender, timestamp in cursor.fetchall():            
            messages.append({"role": sender, "content": message})
            #print(messages) 
        
        #Genero la petción a opeAI, invocando el objeto response le paso como argument
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages = messages)
        for choice in response.choices:
            messages.append({"role": "assistant", "content": choice.message.content})
        response_message = response.choices[0].message.content
        
        #Me guardo em mensaje de respuesta de la IA
        db.insert_message(user_id, from_number, profile_name, response_message, "assistant")
        #db.set_user_messages_unprocessed(from_number)
        #Mandamos la respuesta a través de Twilio
        message = twilio_client.messages.create(
            from_=twilio_number,
            body=response_message,
            to=from_number
        )
        #Meto a piñon un recordatorio en base de datos con formato
        #user_id (int): ID del usuario relacionado.
        #whatsapp_number (str): Número de WhatsApp del usuario.
        #class_type (str): Tipo de clase (e.g., 'Rumba', 'Flamenco', 'Sevillanas').
        #class_date (str): Fecha de la clase en formato 'YYYY-MM-DD'.
        #class_time (str): Hora de la clase en formato 'HH:MM'.
        insert_new_reservation(user_id, from_number, "Rumba", "2024-12-12", "20:00")
        
        return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred"}), 500


if __name__ == "__main__":
    # Inicia ambos hilos en paralelo
    threading.Thread(target=start_web_server).start()
    threading.Thread(target=start_conversations_processing).start()
    threading.Thread(target=start_appointment_notifications).start()
    print("Yeah")
    
    