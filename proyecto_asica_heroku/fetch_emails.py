import email
from email.header import decode_header
import requests
import json
import os
import time
from dotenv import load_dotenv
from imapclient import IMAPClient

# Cargar variables de entorno
load_dotenv(dotenv_path='load_auth.env')

# Configuración del servidor de correo
username = os.getenv("EMAIL_USERNAME")
password = os.getenv("EMAIL_PASSWORD")
imap_url = os.getenv("IMAP_URL")

def connect_to_mail():
    try:
        mail = IMAPClient(imap_url, ssl=True)
        mail.login(username, password)
        mail.select_folder('INBOX')
        print("Conexión exitosa")
        return mail
    except Exception as e:
        print(f"Error al conectar al servidor IMAP: {e}")
        return None

def process_incoming_emails(mail):
    """Procesa todos los correos no leídos y los marca como leídos."""
    messages = mail.search(['UNSEEN'])  # Buscar solo correos no leídos
    if messages:
        print(f"Se encontraron {len(messages)} correos no leídos.")
        fetch_emails(mail, messages)
    else:
        print("No hay correos no leídos.")

def fetch_emails(mail, messages):
    for msg_id in messages:
        msg_data = mail.fetch([msg_id], ['RFC822'])
        for response_part in msg_data.values():
            msg = email.message_from_bytes(response_part[b'RFC822'])
            message_id = msg.get("Message-ID")
            if not is_email_processed(message_id):
                process_email(msg)
                mail.set_flags([msg_id], [b'\\Seen'])  # Marcar como leído

def is_email_processed(message_id):
    url = 'https://tu-app.herokuapp.com/helpdesk/receive_email/'
    data = {
        'message_id': message_id
    }
    try:
        response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response.json().get('exists', False)
    except requests.exceptions.RequestException as e:
        print(f"Error verificando email procesado: {e}")
        return False
    except ValueError:
        print("Respuesta no contiene un JSON válido:", response.text)
        return False

def process_email(msg):
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    from_ = msg.get("From")
    to_ = msg.get("To")
    message_id = msg.get("Message-ID")
    
    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                except:
                    pass
                body = filter_email_body(body)
                break
    else:
        body = msg.get_payload(decode=True).decode()
        body = filter_email_body(body)

    if body:
        send_email_to_django(from_, to_, subject, body, message_id)

def filter_email_body(body):
    lines = body.split('\n')
    response_delimiters = ["On ", "El ", "Enviado el "]
    filtered_lines = []
    
    for line in lines:
        if any(delimiter in line for delimiter in response_delimiters):
            break
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines).strip()

def send_email_to_django(sender, recipient, subject, body, message_id):
    url = 'https://tu-app.herokuapp.com/helpdesk/receive_email/'
    data = {
        'sender': sender or 'unknown@domain.com',
        'recipient': recipient or 'unknown@domain.com',
        'subject': subject or 'No Subject',
        'body': body or 'No Body',
        'message_id': message_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.status_code, response.text)


# Mantiene la conexión activa para detectar nuevos correos.
def idle(mail):
    print("Esperando nuevos correos...")
    while True:
        try:            
            mail.idle()
            responses = mail.idle_check(timeout=20)
            mail.idle_done()  # Asegurarse de terminar IDLE antes de continuar
            if responses:
                print("Nuevo correo detectado!")
                process_incoming_emails(mail)  # Procesar correos después de IDLE
        except IMAPClient.Error as e:
            print(f"Error durante IDLE (IMAPClient): {e}")
            reconnect_and_resume(mail)
        except Exception as e:
            print(f"Error inesperado durante IDLE: {e}")
            reconnect_and_resume(mail)

def reconnect_and_resume(mail):
    """Intentar reconectar y reanudar el proceso en caso de error."""
    mail.logout()
    time.sleep(5)  # Esperar 5 segundos antes de intentar reconectar
    new_mail = connect_to_mail()
    if new_mail:
        process_incoming_emails(new_mail)
        idle(new_mail)

if __name__ == "__main__":
    mail = connect_to_mail()
    if mail:
        process_incoming_emails(mail)  # Procesar correos no leídos al inicio
        idle(mail)  # Iniciar el proceso de espera activa para nuevos correos