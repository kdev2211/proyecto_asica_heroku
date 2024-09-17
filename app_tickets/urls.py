from django.urls import path
from .views import *

urlpatterns = [

    #URL de el Panel Principal o Dashboard
    path('inicio/', view_panel_principal, name='view_panel_principal'),




    
    # URL para mostrar la informacion de cada ticket.
    path('ticket_tabla/', view_tabla_ticket, name='view_tabla_ticket'),

    # URL que muestra los detalles de un unico ticket junto a un formulario usado para editar la informacion en este.
    path('ticket_tabla/ticket/<int:id>/', view_formulario_ticket, name='view_formulario_ticket'), 
    path('crear_ticket_usuario_ajax/', crear_ticket_usuario_ajax, name='crear_ticket_usuario_ajax'),


    path('view_cargar_usuarios_ajax/<int:id>/', view_cargar_usuarios_ajax, name='view_cargar_usuarios_ajax'), #AJAX PARA CARGAR USUARIOS EN EL SELECT DE USUARIOS DE EL FORMULARIO DE TICKETS
    


]