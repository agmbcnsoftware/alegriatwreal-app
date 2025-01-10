from flask import Flask, jsonify, request, make_response, send_file, render_template, Response
from flask_httpauth import HTTPBasicAuth
from twilio.rest import Client
from openai import OpenAI
from cryptography.fernet import Fernet
import os
import threading
import schedule
import time
import datetime
import messages_database
import emails
import date_operations
import traceback

app = Flask(__name__)
# Configurar autenticación básica
auth = HTTPBasicAuth()


# Cargo variable del entorno
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")  # Ejemplo: 'whatsapp:+14155238886'
twilio_client = Client(account_sid, auth_token)
encryption_key = os.environ.get("AI_INFO_KEY")
#admin_number = "whatsapp:+34651090177"
admin_number = "whatsapp:+34658595387"
email_server = os.getenv("EMAIL_SERVER")
email_address = os.getenv("EMAIL_ADDRESS")
email_pwd = os.getenv("EMAIL_PWD")

#Configuración de opeAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#Obtengo la información específica que hay en ai-knowledge-base.txt
cipher = Fernet(encryption_key.encode())

# Leer y desencriptar el contenido del archivo
with open("ai-info-base.txt", "r") as f:
    encrypted_content = f.read()
base_context = cipher.decrypt(encrypted_content).decode()
print(base_context[0:40])

# Credenciales (usuario: admin, contraseña: password)
USER_CREDENTIALS = {}

def load_users_from_encrypted_file():
    # Leer y desencriptar el archivo
    try:
        with open("users.txt", "r") as f:
            encrypted_users = f.read()
        decrypted_users = cipher.decrypt(encrypted_users.encode()).decode()

        # Parsear el contenido y llenar el diccionario USER_CREDENTIALS
        for line in decrypted_users.splitlines():
            user, password = line.split(":")
            USER_CREDENTIALS[user.strip()] = password.strip()
        print("Usuarios cargados exitosamente:", list(USER_CREDENTIALS.keys()))
    except Exception as e:
        print("Error al cargar usuarios:", e)
        raise

@auth.verify_password
def verify_password(username, password):
    # Verificar si el usuario existe y la contraseña coincide
    return USER_CREDENTIALS.get(username) == password  
  
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# Diccionario para el historial de conversaciones
conversations = {}
db = messages_database
eml = emails
date_ops = date_operations
#db.initialize_db()

# El sistema tiene tres procesos, 1) la web app 2) un proceso que se arrancará a ciertas horas para
# repasar el estado de las conversaciones y notificar al administrador, finalmente un proceso que 
# se encargará de enviar notificaciones a las personas que han pedido una clase de prueba, para 
# que no se olviden

def start_web_server():
    load_users_from_encrypted_file()
    app.run(host='0.0.0.0', port=3000)
    
def get_appointments_from_mail():
   #Obteniendo nuevos citas para clase de prueba desde correo electrónico
    mail = eml.connect_to_email_server(email_server, email_address, email_pwd)
    if mail:
        emails = eml.fetch_emails(mail)
        mail.logout()  # Cerrar la sesión
        # Procesar los correos recuperados
        # Integración con el bucle que recorre los correos
        for email_data in emails:
            #Para cada mail, obtengo su contenido y lo "limpio" de caracteres que puedan dar problemas
            email_body = email_data['body']
            clean_body = eml.clean_email_body(email_body)
            print(clean_body)
            try:
            #Obtengo la información contenida y la inserto en variables
                extracted_data = eml.extract_info(clean_body)
                print(extracted_data)
                nombre = extracted_data.get("Nombre", "No especificado")
                apellidos = extracted_data.get("Apellidos", "No especificado")
                whatsapp_number = "whatsapp:" + extracted_data.get("Teléfono", "No especificado")
                correo = extracted_data.get("Email", "No especificado")
                horario = extracted_data.get("Horario", "No especificado")
                clase = extracted_data.get("Clase", "No especificado")
                # A partir de la fecha reservada obtengo el día concreto en que se hará vendrá a probar
                class_date, class_time = date_ops.get_next_weekday_time(horario)
                #class_date, class_time = result.split(" ")
                # Inserto la información que me llega en los emails en base de datos
                user_id = db. get_or_create_user(whatsapp_number, nombre)
                db.get_or_create_reservation(user_id, nombre, apellidos, whatsapp_number, clase, horario, class_date, class_time)
            except Exception as e:
            # Captura la excepción y muestra la traza
                print("No se pudo gestionar el mail de:" + nombre)
                traceback.print_exc()
                
def create_reminder_text(user_name, class_type, class_date, class_time):
    template = (
        "¡Hola <user_name>!\n\n¿Cómo estas?\n\nTan sólo quería saludarte, y recordarte que te esperamos "
        "mañana <class_weekday> a las <class_time> para tu clase de prueba de <class_type>.\n\n"
        "Recuerda que si a la salida te apuntas, accederás a la oferta de matrícula a 20€ en lugar de 60.\n\n"
        "Si tienes cualquier consulta, no dudes en escribirme y estaré encantada de atenderte.\n\n"
        "¡Un abrazo y hasta mañana!💃🏽✨"
    )
    
    # Diccionario para traducir días de la semana
    days_translation = {
        "Monday": "lunes",
        "Tuesday": "martes",
        "Wednesday": "miércoles",
        "Thursday": "jueves",
        "Friday": "viernes",
        "Saturday": "sábado",
        "Sunday": "domingo"
    }
    
    date_object = datetime.datetime.strptime(class_date, "%Y-%m-%d")
    class_weekday_eng = date_object.strftime("%A")
    class_weekday_spa =  days_translation.get(class_weekday_eng,class_weekday_eng)   
    
    # Reemplazar las claves con los valores proporcionados
    message = (template
               .replace("<user_name>", user_name)
               .replace("<class_type>", class_type)
               .replace("<class_weekday>", class_weekday_spa)
               .replace("<class_time>", class_time))

    return message
           
def notify_appointments():   
    print("Enviando notificaciones)") 
    
    #res_cursor  =  db.get_tomorrow_reservations()
    res_cursor  =  db.get_all_reservations()
    reservations = res_cursor.fetchall()
    for res in reservations:
        reservation_id, user_name, user_surname, whatsapp_number, class_type, class_weekday_hour, class_date, class_time = res
        #Creo el texto que voy a enviar poor whatsapp
        reminder_message = create_reminder_text(user_name, class_type, class_date, class_time)
        # ATENCION PONGO A PIÑON MI NUMERO 
        whatsapp_number = admin_number
        message = twilio_client.messages.create(
            from_=twilio_number,
            body = reminder_message,
            to = whatsapp_number
        )
        #Queda pendiente avisar también al adminsitrador por whatsapp
        # El mensaje sería "Avisado: nombre, numero de whatsapp y clase"
        db.set_reservation_to_sent(reservation_id)
        time.sleep(1) 
    print("Notificaciones enviadas")   
        
        
def start_appointment_notifications():
    #schedule.every().minute.at(":20").do(notify_appointments)
    #schedule.every().minute.at(":00").do(get_appointments_from_mail)
    schedule.every(1).minutes.do(get_appointments_from_mail)
    schedule.every().day.at("09:00").do(notify_appointments)
    while True:
        schedule.run_pending()
        time.sleep(1)
      
@app.route("/")
@auth.login_required
def home():
    return render_template("index.html")  # Renderizar el archivo HTML
  
@app.route("/database")
@auth.login_required
def database():
    return render_template("database.html")
  
@app.route("/reservations")
@auth.login_required
def reservations():
    # Suponemos que `get_all_reservations` devuelve un cursor iterable
    reservations = db.get_all_reservations()  # Implementa esta función
    return render_template("reservations.html", reservations=reservations)
  
@app.route("/messages")
@auth.login_required
def messages():
    # Suponemos que tienes una función para obtener los mensajes
    messages = db.get_all_messages()  # Ejecuta la consulta y obtiene los resultados
    return render_template("messages.html", messages=messages)

@app.route("/download", methods=["GET"])
@auth.login_required
def download_database():
    database_path = "GraciaBot.db"  # Cambia al nombre de tu archivo SQLite
    try:
        return send_file(
            database_path,
            as_attachment=True,
            attachment_filename="GraciaBot.db",  # Nombre del archivo que verá el usuario
        )
    except Exception as e:
        return f"Error al descargar el archivo: {e}", 500


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
        #Mandamos la respuesta a través de Twilio
        message = twilio_client.messages.create(
            from_=twilio_number,
            body=response_message,
            to=from_number
        )
        
        return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred"}), 500


if __name__ == "__main__":
    # Inicia ambos hilos en paralelo
    threading.Thread(target=start_web_server).start()
    #threading.Thread(target=start_conversations_processing).start()
    threading.Thread(target=start_appointment_notifications).start()
    #threading.Thread(target=send_first_message_to_admin).start()    
    print("Yeah")
    
    