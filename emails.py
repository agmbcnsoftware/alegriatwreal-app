import imaplib
import email
from email.header import decode_header



# Conexión al servidor IMAP
def connect_to_email_server(email_server, email_address, password):
    try:
        # Conexión al servidor IMAP
        mail = imaplib.IMAP4_SSL(email_server)
        mail.login(email_address, password)
        return mail
    except Exception as e:
        print(f"Error conectando al servidor de correo: {e}")
        return None
      
# Obtener correos de una carpeta
def fetch_emails(mail, folder="Test"):
    try:
        mail.select(folder)  # Seleccionar la carpeta
        status, messages = mail.search(None, "ALL")  # Buscar todos los correos
        if status != "OK":
            print("No se pudieron recuperar los correos")
            return []
        
        email_ids = messages[0].split()  # IDs de los correos
        emails = []

        for email_id in email_ids:
            # Recuperar el correo por ID
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                print(f"No se pudo recuperar el correo con ID {email_id}")
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Analizar el contenido del correo
                    msg = email.message_from_bytes(response_part[1])
                    email_subject, encoding = decode_header(msg["Subject"])[0]
                    email_subject = email_subject.decode(encoding) if isinstance(email_subject, bytes) else email_subject
                    email_from = msg.get("From")
                    
                    # Procesar el cuerpo del correo
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # Extraer texto del cuerpo
                                body = part.get_payload(decode=True).decode()
                                emails.append({"from": email_from, "subject": email_subject, "body": body})
                                break
                    else:
                        # Caso no multipart
                        body = msg.get_payload(decode=True).decode()
                        emails.append({"from": email_from, "subject": email_subject, "body": body})
        return emails
    except Exception as e:
        print(f"Error al recuperar los correos: {e}")
        return []

      