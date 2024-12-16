import imaplib
import email
from email.header import decode_header
import chardet  # Biblioteca para detectar codificaciones (opcional)
import re # Biblioteca para gestionar expresiones regulares

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
      
# Detectar la codificación de los bytes y decodificar de manera segura
def safe_decode(content):
    try:
        # Intentar UTF-8 primero
        return content.decode("utf-8")
    except UnicodeDecodeError:
        # Detectar codificación usando chardet (opcional pero útil)
        detected_encoding = chardet.detect(content)["encoding"]
        if detected_encoding:
            try:
                return content.decode(detected_encoding)
            except UnicodeDecodeError:
                pass
        # Como último recurso, decodificar de manera "tolerante"
        return content.decode("utf-8", errors="replace")  # Reemplaza caracteres inválidos


def fetch_emails(mail, folder="Test"):
    try:
        mail.select(folder)
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("No se pudieron recuperar los correos")
            return []
        
        email_ids = messages[0].split()
        emails = []

        for email_id in email_ids:
            # Recuperar correo
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                print(f"No se pudo recuperar el correo con ID {email_id}")
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    # Decodificar el asunto
                    email_subject, encoding = decode_header(msg["Subject"])[0]
                    email_subject = (
                        email_subject.decode(encoding)
                        if isinstance(email_subject, bytes) and encoding
                        else email_subject
                    )
                    email_from = msg.get("From")

                    # Procesar el cuerpo del correo
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body_bytes = part.get_payload(decode=True)
                                body = safe_decode(body_bytes) if body_bytes else ""
                                emails.append({
                                    "from": email_from,
                                    "subject": email_subject,
                                    "body": body
                                })
                                break
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        body = safe_decode(body_bytes) if body_bytes else ""
                        emails.append({
                            "from": email_from,
                            "subject": email_subject,
                            "body": body
                        })
        return emails
    except Exception as e:
        print(f"Error al recuperar los correos: {e}")
        return []

      
def extract_info(email_body):
    extracted_data = {}

    # Palabras clave y patrones asociados
    patterns = {
        "Nombre": r"Nombre\s*[:\-]?\s*(.*)",
        "Teléfono": r"Tel[eé]fono\s*[:\-]?\s*(.*)",
        "Correo Electrónico": r"Email\s*[:\-]?\s*(.*)",
        "Curso": r"Curso\s*[:\-]?\s*(.*)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            extracted_data[key] = match.group(1).strip()

    return extracted_data