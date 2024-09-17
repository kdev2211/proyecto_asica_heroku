from django.urls import path
from .views import *

urlpatterns = [

    # URL para visualizar la tabla de usuarios

    path ('usuarios/', view_tabla_usuarios, name='view_tabla_usuarios'),

        # View para añadir registros en la tabla de usuarios mediante ajax
    path('agregar_usuario/', view_agregar_usuario_ajax, name='view_agregar_usuario_ajax'),


    path('actualizar_usuario/<int:user_id>/', funcion_actualizar_usuario, name='funcion_actualizar_usuario'),

    path('reenviar-invitacion/', funcion_reenviar_invitacion_ajax, name='funcion_reenviar_invitacion_ajax'),

    # Views de autenticacion
    path('', login_view, name='login_view'), # URL para login
    path('logout/', logout_view, name='logout_view'),  # URL para logout





   # Perfil de usuario
    path('perfil_usuario/', view_perfil_usuario, name='view_perfil_usuario'),





    # Views relacionados a cambios de creedenciales:

    # Formulario para el cambio de credenciales temporales y activacion de usuarios
    path('activar_cuenta/<uuid:token>/', view_formulario_activacion_cuenta, name='view_formulario_activacion_cuenta'),

    # View para el submit de el formulario de cambio de credenciales de acceso
    path('view_activar_cuenta/<uuid:token>/', funcion_submit_formulario_activacion_cuenta_ajax, name='funcion_submit_formulario_activacion_cuenta_ajax'),

    # View para el envio de solicitud de cambio de contraseña (forgot password)
    path('forgot-password-form/', view_forgot_password_ajax, name='view_forgot_password_ajax'),



    # Formulario de cambio de contraseña (forgot password)
    path('forgot-password/<str:token>/', view_formulario_forgot_password, name='view_formulario_forgot_password'),

    # Submit de cambio de contraseña (forgot password)
    path('forgot-password-change/<uuid:token>/', funcion_submit_formulario_forgot_password_ajax, name='funcion_submit_formulario_forgot_password_ajax'),

    path('cambiar-password/', funcion_cambiar_password_usuario_ajax, name='funcion_cambiar_password_usuario_ajax'),


    # Not Found
    path('no_disponible/', not_found, name='not_found'),
]