from flask import Flask, jsonify, request
from twilio.rest import Client
import openai
import os

# Configura OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

# Configuración de Twilio
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")  # Ejemplo: 'whatsapp:+14155238886'
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(account_sid, auth_token)

@app.route("/")
def home():
    return "Hello World!"

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
            from_=twilio_number,
            body=response_message,
            to=from_number
        )

        

        print(f"Sent message SID: {message.sid}")

        return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
