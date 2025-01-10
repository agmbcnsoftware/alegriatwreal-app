# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

content_variables = {
    "user_name": "Marta",           # Nombre
    ""
    "class_time": "jueves a las 18:45",  # Fecha y hora
    "class_type": "Sevillanas"    # Clase
}

message = client.messages.create(
  from_=twilio_number,
  content_sid='HXee3cf6439091a385009b6bb7a5314ded',
  content_variables= content_variables,
  to='whatsapp:+34658595387'
)



print(message.sid)