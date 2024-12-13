import imaplib
import email
from email.header import decode_header



# Conexión al servidor IMAP
def connect_to_email_server(email_server, email_address, password):
    try:
        # Conexión al servidor IMAP
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_address, password)
        return mail
    except Exception as e:
        print(f"Error conectando al servidor de correo: {e}")
        return None
      
      