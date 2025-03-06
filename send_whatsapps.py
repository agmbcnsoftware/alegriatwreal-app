# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import date_operations
import json

admin_number = "whatsapp:+34658595387"

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")
# Forulario inicial de prueba que solo dice hola
def send_hello():
    client = Client(account_sid, auth_token)

    message = client.messages.create(
      from_= twilio_number,
      content_sid='HXcd2b1e54c65066d6b80c7d24b28eb6d2',
      to='whatsapp:+34658595387'
    )
    print(message.sid)
 #Formulario de recordatorio


def send_reminder_by_whatsapp(whatsapp_number, user_name, class_type, class_date, class_time):
  # Diccionario para traducir días de la semana
    client = Client(account_sid, auth_token)
    class_weekday_spa = date_operations.get_spanish_weekday(class_date)   
    variables = {
        "user_name": user_name,
        "class_weekday": class_weekday_spa,
        "class_time": class_time,
        "class_type": class_type
    }

    message = client.messages.create(
      from_=twilio_number,
      content_sid='HX367017145e56f0e972cd76bdde7087fc',
      content_variables = json.dumps(variables),
      to=whatsapp_number
    ) 

def send_reminder_by_whatsapp_to_admin(user_name, class_type, class_date, class_time):
    whatsapp_number = admin_number
    send_reminder_by_whatsapp(whatsapp_number, user_name, class_type, class_date, class_time)

    #Respuestas de formulario de recordatorio
reminder_accept_text = "Genial! Allí estaré"
reminder_reject_text = "Lástima. No puedo ir"

# Formulario de respuesta al rechazo a la reserva
def say_pitty(whatsapp_number, link):
    client = Client(account_sid, auth_token)  
    variables = {"1": link}

    message = client.messages.create(
      from_=twilio_number,
      content_sid='HX9dae81c6fce85e0c0c541d42cb9f27bc',
      content_variables = json.dumps(variables),
      to=whatsapp_number
    ) 

#Formulario de respuesta a la confirmación del recordatorio 
def say_thanks(whatsapp_number):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_= twilio_number,
      content_sid='HXad680384c1e77cbefce50d4a71d85ca5',
      to = whatsapp_number
    )
    print(message.sid)