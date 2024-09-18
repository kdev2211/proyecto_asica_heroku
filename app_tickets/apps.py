from django.apps import AppConfig


class AppTicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_tickets'


    def ready(self):
        import app_tickets.notificaciones_signals  # Importar el archivo de señales