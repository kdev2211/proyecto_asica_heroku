from django.urls import path
from .views import *

urlpatterns = [

    # URL de el formulario para clientes.
    path('contactanos/', view_formulario_contacto, name='view_formulario_contacto'),
    

     
]