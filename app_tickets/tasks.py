from celery import shared_task
from proyecto_asica_heroku.fetch_emails import connect_to_mail, process_incoming_emails

@shared_task
def process_emails_task():
    """Tarea que se ejecuta cada 20 segundos para procesar correos."""
    print("Iniciando tarea de procesamiento de correos")
    mail = connect_to_mail()
    if mail:
        print("Conexión exitosa. Procesando correos.")
        process_incoming_emails(mail)
    else:
        print("No se pudo conectar al servidor de correo.")