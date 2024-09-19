from django.urls import path
from .views import *

urlpatterns = [

    #URL de el Panel Principal o Dashboard
    path('inicio/', view_panel_principal, name='view_panel_principal'),




    
    # URL para mostrar la informacion de cada ticket.
    path('ticket_tabla/', view_tabla_ticket, name='view_tabla_ticket'),

    path('ticket_tabla_usuario/', view_tabla_ticket_creado_por_usuario, name='view_tabla_ticket_creado_por_usuario'),



    # URL que muestra los detalles de un unico ticket junto a un formulario usado para editar la informacion en este.
    path('ticket_tabla/ticket/<int:id>/', view_formulario_ticket, name='view_formulario_ticket'), 



    path('crear_ticket_usuario_ajax/', crear_ticket_usuario_ajax, name='crear_ticket_usuario_ajax'),


    path('view_cargar_usuarios_ajax/<int:id>/', view_cargar_usuarios_ajax, name='view_cargar_usuarios_ajax'), #AJAX PARA CARGAR USUARIOS EN EL SELECT DE USUARIOS DE EL FORMULARIO DE TICKETS
    



    # Funcion ajax usada para procesar tanto notas privadas/comentarios en un ticket como respuestas a clientes. 
    path('agregar_nota/<int:id>/', view_agregar_nota_ajax, name='view_agregar_nota_ajax'),

    # URL para la view que se encarga de procesar y guardar cada respuesta (enviadas por correo electronico) por parte de el cliente. 
    path('receive_email/', receive_email, name='receive_email'),




]