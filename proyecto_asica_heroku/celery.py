from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración predeterminado de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_asica_heroku.settings')

app = Celery('proyecto_asica_heroku')

# Cargar la configuración de Celery desde el archivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubre tareas en los archivos tasks.py de cada app de Django
app.autodiscover_tasks()