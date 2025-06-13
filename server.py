from flask import Flask, jsonify, request, make_response, send_file, render_template, flash, session, Response
import os
import json
import csv
import messages_database
import pg_database
import emails
import date_operations
import send_whatsapps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Esto genera una clave secreta aleatoria

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
def home():
    return render_template("index.html")

  
@app.route("/n8nreservations")
def n8nreservations():
    filter_option = request.args.get("filter", "next_reservations")
    reservations = pgdb.get_filtered_reservations(filter_option)
    return render_template("n8nreservations.html", reservations=reservations, filter_option=filter_option)

@app.route("/n8nmessages")
def n8nmessages():
    filter_option = request.args.get("filter", "today")
    messages = pgdb.get_filtered_messages(filter_option)
    return render_template("n8nmessages.html", messages=messages, filter_option=filter_option)

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

# ============ CONFIGURACIÓN PARA RAILWAY ============

# Para Railway/Gunicorn
application = app

# Para desarrollo local
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
if __name__ == "__main__":
    load_users_from_encrypted_file()
    app.run(host='0.0.0.0', port=3000, debug=True)
    
