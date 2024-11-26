from flask import Flask, jsonify
from flask import render_template
from flask import request
import model


app = Flask(__name__)

@app.route("/")
def home():
  print(f"Received data in route /")
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received webhook")
    print("Headers:", request.headers)
    print("Body:", request.data)  # Log the raw body
    try:
        
        data = request.get_json(force=True)  # Extrae JSON
        print("Parser json:", data)
        if not data:
            return jsonify({"error": "No JSON received"}), 400
        return jsonify({"message": "Webhook received successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Invalid JSON"}), 400
  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  