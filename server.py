from flask import Flask
from flask import render_template
from flask import request
import model


app = Flask(__name__)

@app.route("/")
def home():
  return "Hello world!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"Received data: {data}")
    return "Webhook received", 200
  
if __name__ == "__main__":
  app.run()

  