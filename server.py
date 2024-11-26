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

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extraer información del mensaje
        incoming_message = data.get("Body", "").strip()
        from_number = data.get("From")  # Número del remitente
        print(f"Message body: {incoming_message}, From: {from_number}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil que responde preguntas de WhatsApp."},
                {"role": "user", "content": incoming_message},
            ]
        )
        #response_message = "¡Gracias por tu mensaje! Pronto te responderemos."
        response_message = response['choices'][0]['message']['content'].strip()

        # Enviar respuesta automatizada
        
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
