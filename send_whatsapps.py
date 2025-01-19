# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")

def send_hello():
    client = Client(account_sid, auth_token)

    message = client.messages.create(
      from_= twilio_number,
      content_sid='HXcd2b1e54c65066d6b80c7d24b28eb6d2',
      to='whatsapp:+34658595387'
    )
    print(message.sid)
    
def send_reminder_by_whatsapp(whatsapp_number, user_name, class_type, class_date, class_time):
  # Diccionario para traducir días de la semana
    client = Client(account_sid, auth_token)
    class_weekday_spa = date_ops.get_spanish_weekday(class_date)   
    variables = {
        "user_name": user_name,
        "class_weekday": class_weekday_spa,
        "class_time": class_time,
        "class_type": class_type
    }

    message = client.messages.create(
      from_=twilio_number,
      content_sid='HXee3cf6439091a385009b6bb7a5314ded',
      content_variables = json.dumps(variables),
      to=whatsapp_number
    ) 

def send_reminder_by_whatsapp_to_admin(user_name, class_type, class_date, class_time):
    whatsapp_number = admin_number
    send_reminder_by_whatsapp(whatsapp_number, user_name, class_type, class_date, class_time)

def send_(link)
client = Client(account_sid, auth_token)
    class_weekday_spa = date_ops.get_spanish_weekday(class_date)   
    variables = {"1": link}

    message = client.messages.create(
      from_=twilio_number,
      content_sid='HXee3cf6439091a385009b6bb7a5314ded',
      content_variables = json.dumps(variables),
      to=whatsapp_number
    ) 