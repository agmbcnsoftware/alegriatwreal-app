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
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
print("Datos para twilio")
print(TWILIO_AUTH_TOKEN[0:5])
print(TWILIO_ACCOUNT_SID[0:5])
print(TWILIO_NUMBER[0:5])

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def home():
  print(f"Received data in route /")
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received webhook")
    try:
        data = request.form
        print("With data:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extraer información del mensaje
        message_body = data.get("Body")  # Mensaje recibido
        from_number = data.get("From")  # Número del remitente

        print(f"Message body: {message_body}, From: {from_number}")

        # Enviar respuesta automatizada
        response_message = "¡Gracias por tu mensaje! Pronto te responderemos."
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            to=from_number,
            body=response_message
        )

        print(f"Sent message SID: {message.sid}")

        return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred"}), 500

  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  