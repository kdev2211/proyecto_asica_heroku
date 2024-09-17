from django.urls import path
from .views import *

urlpatterns = [

    # URL de el formulario para clientes.
    path('', view_formulario_contacto, name='view_formulario_contacto'),
    
    # URL de la funcion AJAX para procesar los datos ingresados en el formulario para clientes.
    path('submit/', view_enviar_consulta_ajax, name='view_enviar_consulta_ajax'),

    path('contactos/', view_tabla_contactos, name='view_tabla_contactos'),
     
]