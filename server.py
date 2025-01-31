from flask import Flask, jsonify, request, make_response, send_file, render_template, flash, session, Response
from flask_httpauth import HTTPBasicAuth
from twilio.rest import Client
from openai import OpenAI
from cryptography.fernet import Fernet
import os
import threading
import schedule
import time
import messages_database
import emails
import date_operations
import traceback
import json
import send_whatsapps
import csv


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Esto genera una clave secreta aleatoria
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
        
def get_reservation_url(class_type):
    if class_type == "FLAMENCO":
        return "https://graciaflamenca.es/web/formulario-clase-gratuita-de-flamenco/"
    if class_type == "RUMBA":
        return "https://graciaflamenca.es/web/formulario-clase-gratuita-de-rumba/"
    if class_type == "SEVILLANAS":
        return "https://graciaflamenca.es/web/formulario-clase-gratuita-de-sevillanas/"

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
sw = send_whatsapps
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
        emails = eml.fetch_emails(mail, label="Clase de prueba")
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
                #print(extracted_data)
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
                    
def notify_appointments():   
    print("Enviando notificaciones)")     
    res_cursor  =  db.get_tomorrow_reservations()
    #res_cursor  =  db.get_all_reservations()
    reservations = res_cursor.fetchall()
    for res in reservations:
        reservation_id, user_name, user_surname, whatsapp_number, class_type, class_weekday_hour, class_date, class_time = res
        try:
            #Envío whatsapp al usuario
            sw.send_reminder_by_whatsapp(whatsapp_number, user_name, class_type, class_date, class_time)
            #Envío whatsapp al administrador
            sw.send_reminder_by_whatsapp_to_admin(user_name, class_type, class_date, class_time)          
            #Marco la notificación comio enviada
            db.set_reservation_to_sent(reservation_id)
        except Exception as e:
            traceback.print_exc()
        time.sleep(1) 
    print("Notificaciones enviadas")   
                
def start_appointment_notifications():
    schedule.every(15).minutes.do(get_appointments_from_mail)
    schedule.every().day.at("10:55").do(notify_appointments)
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
    filter_option = request.args.get("filter", "today")  # Por defecto "hoy"
    messages = db.get_filtered_messages(filter_option)  # Obtén los mensajes filtrados

    return render_template("messages.html", messages=messages, filter_option=filter_option)
  
@app.route("/download", methods=["GET"])
@auth.login_required
def download_database():
    database_path = os.getenv("DB_PATH")  # Cambia al nombre de tu archivo SQLite
    try:
        return send_file(
            database_path,
            as_attachment=True,
            attachment_filename="GraciaBot.db",  # Nombre del archivo que verá el usuario
        )
    except Exception as e:
        return f"Error al descargar el archivo: {e}", 500

# Función simulada para enviar mensajes
def send_whatsapp(p1, p2, p3):
    print(f"Enviando mensaje: {p1}, {p2}, {p3}")

def normalize_phone_number(phone):
    # Normaliza el número de teléfono
    phone = str(phone).strip().replace(" ", "")  # Elimina espacios adicionales
    if len(phone) == 9 and phone.isdigit():
        return f"whatsapp:+34{phone}"
    elif phone.startswith("+"):
        return f"whatsapp:{phone}"
    else:
        return None

# Procesar archivo CSV para obtener encabezados y primeras filas
def process_csv(file_path):
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames  # Obtener los nombres de las columnas
        preview_data = []
        for i, row in enumerate(reader):
            if i < 10:  # Mostrar solo las primeras 10 filas
                preview_data.append(row)
            else:
                break
    return headers, preview_data

# Ruta para gestionar campañas

@app.route("/campaigns", methods=["GET", "POST"])
def campaigns():
    column_headers = []
    preview_data = None

    # Manejo del archivo subido y columnas disponibles
    if request.method == "POST":
        # Subir archivo CSV
        if "file-upload" in request.files:
            file = request.files["file-upload"]
            if file.filename.endswith(".csv"):
                file_path = os.path.join("/tmp", file.filename)
                file.save(file_path)

                column_headers, _ = process_csv(file_path)
                session["uploaded_file"] = file_path
                session["columns"] = column_headers
            else:
                flash("Por favor, sube un archivo válido con extensión .csv.", "error")

        # Seleccionar columnas y mostrar las primeras filas
        elif "preview-columns" in request.form:
            file_path = session.get("uploaded_file")
            column_headers = session.get("columns")
            selected_cols = [
                request.form.get("col1"),
                request.form.get("col2"),
                request.form.get("col3"),
            ]

            if file_path and all(selected_cols):
                with open(file_path, newline='', encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    preview_data = []
                    for i, row in enumerate(reader):
                        if i < 5:  # Mostrar solo las primeras 3 filas de las columnas seleccionadas
                            preview_data.append({col: row[col] for col in selected_cols})
                        else:
                            break

        # Enviar mensajes
        elif "send-messages" in request.form:
            file_path = session.get("uploaded_file")
            selected_cols = [
                request.form.get("col1"),
                request.form.get("col2"),
                request.form.get("col3"),
            ]

            if file_path and all(selected_cols):
                with open(file_path, newline='', encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        phone = normalize_phone_number(row[selected_cols[0]])
                        send_whatsapp(phone, row[selected_cols[1]], row[selected_cols[2]])
                        time.sleep(0.5)
                flash("Mensajes enviados con éxito.", "success")
            else:
                flash("Selecciona las columnas y carga un archivo válido.", "error")

    return render_template(
        "campaigns.html",
        column_headers=column_headers,
        preview_data=preview_data,
    )



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
        print(incoming_message)
        # Si el mensaje tiene el literal Olvídame eliminamos todos los mensajes del usuario y ya está
        if (incoming_message == "Olvidame"):
            db.delete_messages_from_user(from_number)
            return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
        if (incoming_message == sw.reminder_accept_text):
            print("Ha aceptado la clase de prueba")
            sw.say_thanks(from_number)
            return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
        if (incoming_message == sw.reminder_reject_text):
            print("NO ha aceptado la clase de prueba")
            res_cursor = db.get_reservations_from_user(from_number)
            reservations = res_cursor.fetchall()
            link = "https://graciaflamenca.es"
            for res in reservations:
                reservation_id, user_name, user_surname, whatsapp_number, class_type, class_weekday_hour, class_date, class_time = res
                link = get_reservation_url(class_type)
            sw.say_pitty(from_number, link)
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
    threading.Thread(target=start_appointment_notifications).start()
    print("Yeah")
    
    