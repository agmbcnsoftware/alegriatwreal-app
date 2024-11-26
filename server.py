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
    print("Headers:", request.headers)
    print("Body:", request.data)  # Muestra el cuerpo crudo para depuración
    try:
        # Intenta cargar el JSON de la solicitud
        data = request.get_json(force=True, silent=True)
        print("Parsed JSON:", data)
        if not data:
            return jsonify({"error": "No JSON received"}), 400
        return jsonify({"message": "Webhook received successfully!"}), 200
    except Exception as e:
        print("Error while processing webhook:", e)
        return jsonify({"error": "Invalid JSON"}), 400

  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  