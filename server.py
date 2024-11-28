from flask import Flask, jsonify, request
from twilio.rest import Client
from openai import OpenAI
import os


app = Flask(__name__)

# Configuración de los clientes de Twilio y openAI
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")  # Ejemplo: 'whatsapp:+14155238886'
twilio_client = Client(account_sid, auth_token)
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Leer la base de conocimiento de AI
with open("ai-knowledge-base.txt", "r") as file:
    base_context = file.read()

# Diccionario para el historial de conversaciones
conversations = {}

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
        user_message = data.get("Body", "").strip()
        from_number = data.get("From")  # Número del remitente
        print(f"Message body: {user_message}, From: {from_number}")
            
        # Crear el historial si no existe
        if from_number not in conversations:
            conversations[from_number] = [
                {"role": "system", "content": base_context}  # Contexto base
            ] 
        # Añadir el mensaje del usuario al historial
        conversations[from_number].append({"role": "user", "content": user_message})
        
        # Obtener la respuesta de OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[from_number]
        )
        
        ai_response = response.choices[0].message["content"]
        print(ai_response)
        #Esto es como lo hice la vez anterior
        #response_message = response.choices[0].message.content
        
        # Añadir la respuesta de la IA al historial
        conversations[from_number].append({"role": "assistant", "content": ai_response})
        
        
        # Enviar respuesta automatizada
        message = twilio_client.messages.create(
            from_=twilio_number,
            body=ai_response,
            to=from_number
        )
        
        print(f"Sent message SID: {message.sid}")

        return jsonify({"message": "Webhook processed and response sent successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
