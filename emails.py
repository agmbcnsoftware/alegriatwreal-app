import imaplib
import email
from email.header import decode_header
import chardet  # Biblioteca para detectar codificaciones (opcional)
import re # Biblioteca para gestionar expresiones regulares
import html

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


def fetch_emails(mail, label):
    try:
        #mail.select(folder)
        status, messages = mail.select(f'"{label}"')
        if status != "OK":
            print("No se pudieron recuperar los correos")
            return []
        status, data = mail.search(None, "ALL")
        if status != "OK":
            print("Error al buscar los correos")
            return []
        
        #email_ids = messages[0].split()  # IDs de los correos
        email_ids = data[0].split()  # IDs de los correos
        #print(f"Número de correos encontrados en {label}: {len(email_ids)}")
        #print(f"IDs de los correos: {email_ids}")  # Imprime los IDs obtenidos
        #email_ids = messages[0].split()
        emails = []

        for email_id in email_ids:
            # Recuperar correo
            #print("Recupero un mail")
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
                    #print(email_subject)
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

def clean_email_body(email_body):
    """
    Limpia el contenido del correo, eliminando caracteres invisibles y decodificando HTML si es necesario.
    """
    # Decodificar entidades HTML (&nbsp;, &lt;, etc.)
    email_body = html.unescape(email_body)
    
    # Reemplazar caracteres no estándar y normalizar
    email_body = email_body.replace("\xa0", " ")  # Espacio no estándar
    email_body = email_body.replace("\r", "")    # Retornos de carro
    
    email_body = email_body.strip()              # Quitar espacios al principio y al final
    
    return email_body

def extract_info(email_body):
    """
    Extrae información clave del cuerpo del correo.
    """
    extracted_data = {}

    # Patrones mejorados para detectar palabras clave y manejar posibles líneas intermedias
    patterns = {
        "Clase": r"clase gratuita de\s*\*?(\w+)\*?",  # Maneja palabras con o sin asteriscos
        "Horario": r"Horario\s*[:\-]?\s*(.+?)\s*(?=(Nombre|Apellidos|Email|Teléfono|Fecha solicitud|Nivel|$))",
        "Nombre": r"Nombre\s*[:\-]?\s*(.+?)\s*(?=(Apellidos|Email|Teléfono|Fecha solicitud|$))",
        "Apellidos": r"Apellidos\s*[:\-]?\s*(.+?)\s*(?=(Email|Teléfono|Fecha solicitud|$))",
        "Email": r"Email\s*[:\-]?\s*(.+?)\s*(?=(Teléfono|Fecha solicitud|$))",
        "Teléfono": r"Tel[eé]fono\s*[:\-]?\s*(.+?)\s*(?=(Fecha solicitud|$))",
        "Fecha solicitud": r"Fecha solicitud\s*[:\-]?\s*(.+)"
    }

    # Buscar cada patrón en el cuerpo del correo
    for key, pattern in patterns.items():
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            extracted_data[key] = match.group(1).strip()

    return extracted_data


