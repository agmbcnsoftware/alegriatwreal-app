from flask import Flask, jsonify
from flask import render_template
from flask import request
import model
from twilio.rest import Client
import os
import sys

print(f"Python version: {sys.version}")

app = Flask(__name__)

# Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
print("Datos para twilio")
print(TWILIO_AUTH_TOKEN[0:5])
print(TWILIO_ACCOUNT_SID[0:5])
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def home():
  print(f"Received data in route /")
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received webhook")
    try:
        # Procesa los datos URL-encoded enviados por Twilio
        data = request.form
        print("With data:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Accede a parámetros específicos
        message_body = data.get("Body")  # El contenido del mensaje
        from_number = data.get("From")  # El número que envía el mensaje

        print(f"Message body: {message_body}, From: {from_number}")

        return jsonify({"message": "Webhook processed successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Invalid data"}), 400


  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  