import string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from proyecto_asica_heroku import settings
from app_tickets.models import *
from app_autenticacion.models import *
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
@never_cache     # La pagina siempre se refrescará
def view_tabla_usuarios(request):
    # Obtener el usuario actual
    user = request.user

    # Verificar si el usuario pertenece al grupo "Supervisor"
    if user.groups.filter(name='Supervisor').exists():
        # Datos de los usuarios pertenecientes al departamento del supervisor que inició sesión.
        user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=user)
        user_departamento = user_perfil.departamento
        perfiles_lista = Perfil_Usuario.objects.filter(departamento=user_departamento)

        data = {'usuarios_lista': perfiles_lista}
        return render(request, 'tabla_usuarios.html', data)
    else:
        # Si el usuario no pertenece al grupo "Supervisor", renderiza la plantilla "not_found.html"
        return render(request, 'not_found.html')
    




# Función para generar nombre de usuario aleatorio y estandarizado.

def funcion_generar_nombre_usuario(exclude_username=None):
    while True:
        numeros = ''.join(random.choices(string.digits, k=3))  # Generar 3 números aleatorios
        letras = ''.join(random.choices(string.ascii_lowercase, k=3))  # Generar 3 letras aleatorias
        username = f"asi{numeros}{letras}"

        if exclude_username is None or username != exclude_username:
            if not User.objects.filter(username=username).exists():
                return username

# Agregar usuarios: crea el usuario y su perfil con los datos ingresados en el formulario que se encuentra en la plantilla "tabla_usuarios". 
# La view enviará una invitacion con un enlace unico que permitira al usuario ingresar sus credenciales para activar su cuenta
# Ademas de poder cambiar su contraseña temporal por una mejor, la contraseña temporal no funciona en el login por motivos de autenticacion. 

@login_required
def view_agregar_usuario_ajax(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_usuario')
        apellido = request.POST.get('apellido_usuario')
        email = request.POST.get('email_usuario').lower()
        telefono = request.POST.get('telefono_usuario')
        puesto = request.POST.get('puesto_usuario')

        user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=request.user)
        departamento_id = user_perfil.departamento.id

        try:
            # Verificar si el email ya está registrado
            user_email = User.objects.filter(email=email).first()
            invitacion = Invitacion_Usuario.objects.filter(email=email).first()

            if user_email:
                last_login = user_email.last_login
                if last_login:
                    return JsonResponse({
                        'success': True,
                        'message': 'El usuario ya tiene una cuenta activa. No es necesario reenviar la invitación.',
                        'existing': True
                    })

                # Reenviar invitación
                if invitacion:
                    invitacion.actualizar_token()
                    contrasena_temporal = invitacion.contrasena_temporal
                    token = invitacion.token
                    link_activacion = request.build_absolute_uri(reverse('app_autenticacion:view_formulario_activacion_cuenta', args=[token]))
                    mensaje = (f"Hola {nombre},\n\nHas sido invitado a unirte. Usa tu correo y la siguiente contraseña temporal: "
                               f"{contrasena_temporal}\nAccede al sistema usando este enlace: {link_activacion}.\n"
                               f"Una vez que actives tu cuenta, se te redirigirá para iniciar sesión con tu nueva contraseña.")
                    email_from = settings.EMAIL_HOST_USER
                    email_message = EmailMessage(
                        subject='Reenvío de Invitación a unirse',
                        body=mensaje,
                        from_email=email_from,
                        to=[email],
                    )
                    email_message.send()

                    return JsonResponse({
                        'success': True,
                        'message': 'La invitación ha sido reenviada al usuario con la misma contraseña temporal.',
                        'existing': True
                    })

            else:
                # Crear nuevo usuario
                contrasena_temporal = get_random_string(10)
                username = funcion_generar_nombre_usuario()
                usuario = User.objects.create_user(
                    username=username,
                    first_name=nombre,
                    last_name=apellido,
                    email=email,
                    password=contrasena_temporal,
                    is_active=False
                )
                departamento = Departamento.objects.get(id=departamento_id)
                Perfil_Usuario.objects.create(
                    user=usuario,
                    nombre_completo=f"{nombre} {apellido}",
                    departamento=departamento,
                    nombre_puesto=puesto,
                    telefono_usuario=telefono
                )
                token = uuid.uuid4()
                Invitacion_Usuario.objects.create(
                    email=email,
                    contrasena_temporal=contrasena_temporal,
                    token=token
                )
                link_activacion = request.build_absolute_uri(reverse('app_autenticacion:view_formulario_activacion_cuenta', args=[token]))
                mensaje = (f"Hola {nombre},\n\nHas sido invitado a unirte. Usa tu correo y la siguiente contraseña temporal: "
                        f"{contrasena_temporal}\nAccede al sistema usando este enlace: {link_activacion}.\n"
                        f"Una vez que actives tu cuenta, se te redirigirá para iniciar sesión con tu nueva contraseña.")
                email_from = settings.EMAIL_HOST_USER
                email_message = EmailMessage(
                    subject='Invitación a unirse',
                    body=mensaje,
                    from_email=email_from,
                    to=[email],
                )
                email_message.send()

                return JsonResponse({
                    'success': True,
                    'message': 'Usuario creado, la invitación ha sido enviada.',
                    'existing': False
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})



@login_required

def funcion_actualizar_usuario(request, user_id):
    if request.method == 'POST':
        try:
            # Obtener el usuario que se va a actualizar
            usuario = User.objects.get(id=user_id)

            # Datos del formulario
            nombre_usuario = request.POST.get('nombre_usuario')
            apellido_usuario = request.POST.get('apellido_usuario')
            email_usuario = request.POST.get('email_usuario').lower()
            telefono_usuario = request.POST.get('telefono_usuario')
            puesto_usuario = request.POST.get('puesto_usuario')

            if usuario.last_login is not None:

                status_usuario = request.POST.get('userStatus')

            else: 
                status_usuario = False

            # Validar si el email ya está registrado por otro usuario
            if User.objects.filter(email=email_usuario).exclude(id=user_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un usuario registrado con este correo electrónico.'
                }, status=400)

            # Actualizar los datos del usuario
            usuario.first_name = nombre_usuario
            usuario.last_name = apellido_usuario
            usuario.email = email_usuario
            usuario.is_active = True if status_usuario == 'True' else False
            usuario.save()

            # Actualizar datos adicionales del perfil (si aplica)
            perfil = usuario.perfil_usuario
            perfil.telefono_usuario = telefono_usuario
            perfil.nombre_puesto = puesto_usuario
            perfil.save()

            return JsonResponse({'status': 'success', 'message': 'Usuario actualizado correctamente.'})

        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'El usuario no existe.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al actualizar el usuario: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido.'
        }, status=405)



@csrf_exempt
def funcion_reenviar_invitacion_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('id')
            
            # Verificar si el email ya está registrado
            user_email = User.objects.filter(id=user_id).first()
            if not user_email:
                return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})

            invitacion = Invitacion_Usuario.objects.filter(email=user_email.email).first()
            if user_email.last_login:
                return JsonResponse({
                    'success': True,
                    'message': 'El usuario ya tiene una cuenta activa. No es necesario reenviar la invitación.',
                    'existing': True
                })

            if invitacion:
                invitacion.actualizar_token()
                contrasena_temporal = invitacion.contrasena_temporal
                token = invitacion.token
                link_activacion = request.build_absolute_uri(reverse('app_autenticacion:view_formulario_activacion_cuenta', args=[token]))

                mensaje = (f"Hola {user_email.first_name},\n\nHas sido invitado a unirte. "
                           f"Usa tu correo y la siguiente contraseña temporal: {contrasena_temporal}\n"
                           f"Accede al sistema usando este enlace: {link_activacion}.\n"
                           "Una vez que actives tu cuenta, se te redirigirá para iniciar sesión con tu nueva contraseña.")

                email_from = settings.EMAIL_HOST_USER
                email_message = EmailMessage(
                    subject='Reenvío de Invitación a unirse',
                    body=mensaje,
                    from_email=email_from,
                    to=[user_email.email],
                )
                email_message.send()

                return JsonResponse({
                    'success': True,
                    'message': 'La invitación ha sido reenviada al usuario con la misma contraseña temporal.',
                    'existing': True
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})


    

# View de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        
        if '@' in username_or_email:
            user_email = username_or_email.lower()
            try:
                user = User.objects.get(email=user_email)
                username = user.username
            except User.DoesNotExist:
                user = None
        else:
            username = username_or_email
            user = None
        
        if user is None:
            user = authenticate(request, username=username, password=password)
        else:
            user = authenticate(request, username=user.username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or reverse('app_tickets:view_panel_principal')
                return redirect(next_url)
            else:
                return render(request, 'asica_login.html', {'error': 'Tu cuenta está inactiva. Contacta al administrador.'})
        else:
            return render(request, 'asica_login.html', {'error': 'Nombre de usuario, correo electrónico o contraseña incorrectos'})
    
    return render(request, 'asica_login.html')


# View de cierre de sesión
def logout_view(request):
    logout(request)
    return redirect('app_autenticacion:login_view')



@never_cache     # La pagina siempre se refrescará
@login_required
#Template de el perfil de usuario, detalles y cambio de contraseña. 
def view_perfil_usuario (request):

    perfil_usuario = Perfil_Usuario.objects.filter(user=request.user).first()

    data={'perfil_usuario':perfil_usuario}

    return render(request, 'perfil_usuario.html', data)


# El usuario podrá cambiar su contraseña y activar su cuenta mediante este formulario. Se pedirá una contraseña nueva que cumpla con requisitos definidos en la template:
# formulario_activacion_cuenta.html
def view_formulario_activacion_cuenta(request, token):
    try:
        # Asegúrate de que el token se convierta a cadena si no lo es ya
        if isinstance(token, uuid.UUID):
            token = str(token)

        # Convertir el token en un objeto UUID
        token = uuid.UUID(token)
        
        invitacion = get_object_or_404(Invitacion_Usuario, token=token)

        if not invitacion.es_token_valido():
            return HttpResponse('Token inválido o expirado.', status=400)




        # Renderizar la página de activación
        return render(request, 'formulario_activacion_cuenta.html', {'token': token})

    except Invitacion_Usuario.DoesNotExist:
        return HttpResponse('Token inválido o expirado.', status=400)
    except ValueError:
        # El token proporcionado no es un UUID válido
        return HttpResponse('Token inválido.', status=400)
    


# Esta view maneja los datos enviados en el formulario de la view anterior, procesa la informacion para que el estado de el token unico sea marcado como "usado"
# De modo que este ya no sea valido, el estado de el usuario pasa a ser marcado como activo para que este pueda iniciar sesión con normalidad. 
def funcion_submit_formulario_activacion_cuenta_ajax(request, token):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password_temporal = request.POST.get('password_temporal')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')

        invitacion = get_object_or_404(Invitacion_Usuario, token=token)

        if not invitacion.es_token_valido():
            return JsonResponse({'success': False, 'error': 'El token ha expirado o ya ha sido usado.'})

        
        # Validación de contraseña temporal
        if invitacion.contrasena_temporal != password_temporal:
            return JsonResponse({
                'success': False, 
                'error': 'Email o contraseña temporal incorrectos.'
            })

        # Validación de requisitos de seguridad de la contraseña
        if (not any(char.isupper() for char in password_nueva) or
            not any(char.islower() for char in password_nueva) or
            not any(char.isdigit() for char in password_nueva) or
            not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in password_nueva) or
            len(password_nueva) < 8):
            return JsonResponse({
                'success': False, 
                'error': 'Tu nueva contraseña no cumple los requisitos de seguridad.'
            })

                # Validación de coincidencia de contraseñas
        if password_nueva != password_confirmacion:
            return JsonResponse({
                'success': False, 
                'error': 'Tu nueva contraseña y la información ingresada para confirmarla no coinciden.'
            })



        # Marca el token como usado


        try:

            invitacion.token_usado = True
            invitacion.save()
            # Obtén al usuario con el correo proporcionado
            user = User.objects.get(email=email)
            # Establece la nueva contraseña
            user.set_password(password_nueva)
            # Activa al usuario
            user.is_active = True
            # Guarda los cambios del usuario
            user.save()
            
            return JsonResponse({'success': True, 'message': 'La cuenta ha sido activada y la contraseña actualizada.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No se encontró el usuario con el correo proporcionado.'})

    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})




# Esta funcion envía un enlace de reinicio de contraseña por medio de un correo electronico. Esta funcion puede usarse desde la template:
# asica_login, la cual es usada para iniciar sesión. Esto se hace por medio de un modal que se despliega al hacer click en la etiquete "Haz click aqui"
# en caso de contraseñas olvidadas.
def view_forgot_password_ajax(request):
    if request.method == 'POST':
        email = request.POST.get('forgot_password_email').lower()
        
        # Verificar si el email existe y si el usuario está activo
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return JsonResponse({'success': False, 'error': 'El usuario no está activo.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No existe un usuario con ese correo electrónico.'})
        
        # Verificar si ya existe una solicitud de cambio de contraseña para este email
        solicitud = Solicitud_Forgot_Password.objects.filter(email=email).first()
        
        if solicitud:
            # Si existe, actualizar el token y los campos correspondientes
            solicitud.actualizar_token()
        else:
            # Si no existe, crear una nueva solicitud
            solicitud = Solicitud_Forgot_Password.objects.create(email=email)
        
        # Enviar el correo electrónico con el enlace
        reset_link = request.build_absolute_uri(reverse('app_autenticacion:view_formulario_forgot_password', args=[solicitud.token]))  # Usar solicitud.token para obtener el token actualizado o recién creado
        
        mensaje = f"Haz click en el siguiente enlace para reestablecer tu contraseña: {reset_link}.\n"
                        
        # Enviar el correo
        email_from = settings.EMAIL_HOST_USER
        email_message = EmailMessage(
            subject='Reestablecimiento de contraseña',
            body=mensaje,
            from_email=email_from,
            to=[email],
        )
        email_message.send()

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})


# Esta view es usada para procesar el token (enlace) enviado por correo electronico, esta view es el formulario con validaciones y requisitos de seguridad 
# de modo que la contraseña pueda ser reemplazada de forma exitosa. 
def view_formulario_forgot_password(request, token):
    try:
        # Convertir el token en un objeto UUID, si es necesario
        if isinstance(token, str):
            token = uuid.UUID(token)
        
        # Buscar la solicitud de cambio de contraseña por el token
        solicitud_forgot_password = get_object_or_404(Solicitud_Forgot_Password, token=token)

        # Verificar si el token es válido
        if not solicitud_forgot_password.es_token_valido():
            if solicitud_forgot_password.token_usado:
                return HttpResponse('Este token ya ha sido utilizado.', status=400)
            else:
                return HttpResponse('El token ha expirado.', status=400)

        # Renderizar la página de restablecimiento de contraseña
        return render(request, 'formulario_forgot_password.html', {'token': token})

    except Solicitud_Forgot_Password.DoesNotExist:
        return HttpResponse('Token inválido o expirado.', status=400)
    except ValueError:
        # El token proporcionado no es un UUID válido
        return HttpResponse('Token inválido.', status=400)
    



# Funcion ajax usada para procesar la informacion enviada por medio de el formulario descrito en la view anterior. Esta view cambia el estado de el token y
# realiza el cambio de contraseña.
def funcion_submit_formulario_forgot_password_ajax(request, token):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')

        solicitud_forgot_password = get_object_or_404(Solicitud_Forgot_Password, token=token)

        if not solicitud_forgot_password.es_token_valido():
            return JsonResponse({'success': False, 'error': 'El token ha expirado o ya ha sido usado.'})

        

        # Validación de requisitos de seguridad de la contraseña
        if (not any(char.isupper() for char in password_nueva) or
            not any(char.islower() for char in password_nueva) or
            not any(char.isdigit() for char in password_nueva) or
            not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in password_nueva) or
            len(password_nueva) < 8):
            return JsonResponse({
                'success': False, 
                'error': 'Tu nueva contraseña no cumple los requisitos de seguridad.'
            })

                # Validación de coincidencia de contraseñas
        if password_nueva != password_confirmacion:
            return JsonResponse({
                'success': False, 
                'error': 'Tu nueva contraseña y la información ingresada para confirmarla no coinciden.'
            })





        try:

            # Marca el token como usado
            solicitud_forgot_password.token_usado = True
            solicitud_forgot_password.save()

            # Obtén al usuario con el correo proporcionado
            user = User.objects.get(email=email)
            # Establece la nueva contraseña
            user.set_password(password_nueva)
            # Activa al usuario
            user.is_active = True
            # Guarda los cambios del usuario
            user.save()
            
            return JsonResponse({'success': True, 'message': 'La cuenta ha sido activada y la contraseña actualizada.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No se encontró el usuario con el correo proporcionado.'})

    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})



@login_required

def funcion_cambiar_password_usuario_ajax(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')
        cerrar_sesion = request.POST.get('cerrar_sesion', 'off') == 'on'

        # Verificar si la contraseña actual es correcta
        user = request.user
        if not user.check_password(password_actual):
            return JsonResponse({'success': False, 'error': 'La contraseña actual es incorrecta.'})

        # Verificar si las contraseñas nuevas coinciden
        if password_nueva != password_confirmacion:
            return JsonResponse({'success': False, 'error': 'Las nuevas contraseñas no coinciden.'})

        # Verificar si la nueva contraseña cumple con los requisitos de seguridad
        try:
            validate_password(password_nueva, user=user)
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': ' '.join(e.messages)})

        # Cambiar la contraseña del usuario
        user.set_password(password_nueva)
        user.save()

        # Mantener la sesión activa si no se seleccionó "cerrar sesión"
        if cerrar_sesion:
            logout(request)
            return JsonResponse({'success': True, 'message': 'Cambio de contraseña exitoso. Sesión cerrada.', 'redirect': '/'})
        else:
            update_session_auth_hash(request, user)  # Mantener al usuario autenticado
            return JsonResponse({'success': True, 'message': 'Cambio de contraseña exitoso.'})
    
    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido'})




# Template para manejar algunas excepciones y errores. 
def not_found (request):


    return render(request, 'not_found.html')


