from flask import Flask, jsonify, request, make_response, send_file, render_template, flash, session, Response
from flask_httpauth import HTTPBasicAuth
from cryptography.fernet import Fernet
import os
import json
import csv
import messages_database
import pg_database
import date_operations

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Esto genera una clave secreta aleatoria

# Configurar autenticación básica
auth = HTTPBasicAuth()

encryption_key = os.environ.get("AI_INFO_KEY")
cipher = Fernet(encryption_key.encode())

# Credenciales de usuarios
USER_CREDENTIALS = {}

def load_users_from_encrypted_file():
    """Carga usuarios desde archivo encriptado"""
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
    """Verificar credenciales de usuario"""
    return USER_CREDENTIALS.get(username) == password  
  
@app.after_request
def add_header(response):
    """Evitar cache en respuestas"""
    response.headers["Cache-Control"] = "no-store"
    return response

# Instancias de módulos
db = messages_database
eml = emails
date_ops = date_operations
sw = send_whatsapps
pgdb = pg_database

# ============ RUTAS DE LA APLICACIÓN ============

@app.route("/")
@auth.login_required
def home():
    return render_template("index.html")
  
@app.route("/database")
@auth.login_required
def database():
    return render_template("database.html")
  
@app.route("/reservations")
@auth.login_required
def reservations():
    filter_option = request.args.get("filter", "next_reservations")
    reservations = db.get_filtered_reservations(filter_option)
    return render_template("reservations.html", reservations=reservations, filter_option=filter_option)
 
@app.route("/n8nreservations")
@auth.login_required
def n8nreservations():
    filter_option = request.args.get("filter", "next_reservations")
    reservations = pgdb.get_filtered_reservations(filter_option)
    return render_template("n8nreservations.html", reservations=reservations, filter_option=filter_option)

@app.route("/messages")
@auth.login_required
def messages():
    filter_option = request.args.get("filter", "today")
    messages = db.get_filtered_messages(filter_option)
    return render_template("messages.html", messages=messages, filter_option=filter_option)

@app.route("/n8nmessages")
@auth.login_required
def n8nmessages():
    filter_option = request.args.get("filter", "today")
    messages = pgdb.get_filtered_messages(filter_option)
    return render_template("n8nmessages.html", messages=messages, filter_option=filter_option)
  
@app.route("/download", methods=["GET"])
@auth.login_required
def download_database():
    database_path = os.getenv("DB_PATH")
    try:
        return send_file(
            database_path,
            as_attachment=True,
            attachment_filename="GraciaBot.db",
        )
    except Exception as e:
        return f"Error al descargar el archivo: {e}", 500

# ============ FUNCIONES AUXILIARES ============

def normalize_phone_number(phone):
    """Normaliza el número de teléfono"""
    phone = str(phone).strip().replace(" ", "")
    if len(phone) == 9 and phone.isdigit():
        return f"whatsapp:+34{phone}"
    elif phone.startswith("+"):
        return f"whatsapp:{phone}"
    else:
        return None

def process_csv(file_path):
    """Procesar archivo CSV para obtener encabezados y primeras filas"""
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        preview_data = []
        for i, row in enumerate(reader):
            if i < 10:  # Mostrar solo las primeras 10 filas
                preview_data.append(row)
            else:
                break
    return headers, preview_data

# ============ CONFIGURACIÓN PARA RAILWAY ============

def create_app():
    """Función para crear la app (compatible con Gunicorn)"""
    load_users_from_encrypted_file()
    return app

# Para Railway/Gunicorn
application = create_app()

# Para desarrollo local
if __name__ == "__main__":
    load_users_from_encrypted_file()
    app.run(host='0.0.0.0', port=3000, debug=True)
    
