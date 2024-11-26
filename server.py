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
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def home():
  print(f"Received data in route /")
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Received data:", data)
        
        # Responding to the sender using Twilio API
        message = client.messages.create(
            body="Thanks for your message!",
            from_="+<your-twilio-number>",  # Replace with your Twilio number
            to=data["from"]  # Assumes 'from' field contains sender's number
        )
        print("Message sent:", message.sid)

        return jsonify({"message": "Webhook processed"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to process webhook"}), 400
  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  