from flask import Flask
from flask import render_template
from flask import request
import model


app = Flask(__name__)

@app.route("/")
def home():
  print(f"Received data")
  data = request.get_json()
  print("Received data:", data)
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()  # Extrae JSON
        print("Received data:", data)
        if not data:
            return jsonify({"error": "No JSON received"}), 400
            print("no data received")
        #return jsonify({"message": "Webhook received successfully!"}), 200
    except Exception as e:
        print("Error:", e)
        #return jsonify({"error": "Invalid JSON"}), 400
  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000)

  