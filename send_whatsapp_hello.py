# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_number = 'whatsapp:' + os.getenv("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

message = client.messages.create(
  from_= twilio_number,
  content_sid='HXcd2b1e54c65066d6b80c7d24b28eb6d2',
  to='whatsapp:+34658595387'
)

print(message.sid)