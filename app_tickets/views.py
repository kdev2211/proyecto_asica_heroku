from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
import json
import re
from proyecto_asica_heroku import settings
from app_tickets.models import *
from app_autenticacion.models import *
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime, time, timedelta
from .track_sesiones import ActiveUserMiddleware
from django.views.decorators.cache import never_cache


# PANEL PRINCIPAL / DASHBOARD

@login_required
def view_panel_principal(request):

# Obtiene el usuario actual
    user = request.user
    user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=user)
    user_departamento = user_perfil.departamento
    
    filtro = request.GET.get('filter', 'hoy').replace('_', ' ').title()
    today = timezone.now().date()

    if filtro == 'Hoy':
        start_date = datetime.combine(datetime.now(), time.min)
        end_date = datetime.combine(datetime.now(), time.max)
    elif filtro == 'Este Mes':
        start_date = today.replace(day=1)
        next_month = start_date + timedelta(days=31)
        end_date = next_month.replace(day=1)
    elif filtro == 'Este Año':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(year=today.year + 1, month=1, day=1)
    else:
        # Por defecto, usar hoy
        start_date = today
        end_date = datetime.combine(datetime.now(), time.max)



    # Definir el rango de tiempo reciente
    dias_recientes = 7
    fecha_inicio = timezone.now() - timedelta(days=dias_recientes)

    # Filtrar las vistas recientes del usuario y ordenarlas por la última fecha de visualización
    vistas_recientes = TicketVisto.objects.filter(
            usuario=user, 
            fecha_vista__gte=fecha_inicio
        ).order_by('-fecha_vista')

    # Usar un diccionario para evitar duplicados y mantener solo la vista más reciente
    tickets_unicos = {}
    for vista in vistas_recientes:
            tickets_unicos[vista.ticket.id] = vista

    # Tomar los primeros 5 tickets recientes (ordenados por la vista más reciente)
    tickets_recientes = list(tickets_unicos.values())[:5]   



# Personalizar el contenido basado en el grupo del usuario
    if user.groups.filter(name='Supervisor').exists():
        # FILTROS PARA GRÁFICOS (CORREGIR ESTO A UN SWITCH)

# KPIs DE TICKETS (QUERY/CONULTA A LA BASE DE DATOS)
        total_tickets = Ticket.objects.filter(departamento_id=user_departamento).count()    
        tickets_pendientes =Ticket.objects.filter(status_id=1, departamento_id=user_departamento).count()
        tickets_sin_asignar=Ticket.objects.filter(usuario_id=None, departamento_id=user_departamento).count()
        
       

        
# Obtener los usuarios activos que pertenecen al mismo departamento
        usuarios_activos_departamento = User.objects.filter(
            perfil_usuario__departamento=user_departamento,
            is_active=True)

   
# Filtrar las sesiones activas de esos usuarios
        sesiones_activas_departamento = Session.objects.filter(
            expire_date__gte=timezone.now(),  # sesiones que no han expirado
            session_key__in=[
                session.session_key for session in Session.objects.all()
                if session.get_decoded().get('_auth_user_id') and
                int(session.get_decoded().get('_auth_user_id')) in usuarios_activos_departamento.values_list('id', flat=True)
                ])

# Contar el número de usuarios con status "activo", esto con el fin de contar usuarios que podrian haber renunciado o dejado la empresa temporalmente.
        total_usuarios_activos_departamento = usuarios_activos_departamento.count()

# Contar cuántas sesiones activas están asociadas a usuarios logueados en el departamento
        sesiones_activas = sesiones_activas_departamento.count()


#Obtiene exactamente la informacion de usuarios conectados mediante una modificacion de middleware
#Dado que django no tiene una opcion para hacer esto (unicamente la informacion de las sesiones), fue necesario usar esta variable para capturar estos datos
        users_with_status = ActiveUserMiddleware.get_users_with_status(department=user_departamento, timeout_minutes=5)

# DESDE ESTA PARTE, ES NECESARIO CORREGIR LINEAS DE CODIGO PARA TENER LA INFORMACION UNICAMENTE DESDE EL DEPARTAMENTO.
# KPIs RELACIONADOS A TICKETS POR PRODUCTOS
        tickets_por_producto = Ticket.objects.filter(
            departamento_id= user_departamento, fecha_creacion__range=(start_date, end_date)
        ).values('producto__descripcion_producto').annotate(count=Count('producto')).order_by('producto__descripcion_producto')



        # KPIs RELACIONADOS A TICKETS POR CATEGORIA
        tickets_por_categoria = Ticket.objects.filter(
             departamento_id= user_departamento, fecha_creacion__range=(start_date, end_date)
        ).values('categoria__descripcion_categoria').annotate(count=Count('categoria')).order_by('categoria__descripcion_categoria')

        # PORCENTAJES PARA KPIs DE TARJETAS
        
        porcentaje_tickets_pendientes = (tickets_pendientes / total_tickets) * 100 if total_tickets > 0 else 0
        porcentaje_sesiones_activas = (sesiones_activas / total_usuarios_activos_departamento) * 100 if total_usuarios_activos_departamento > 0 else 0
        porcentaje_tickets_sin_asignar = (tickets_sin_asignar / total_tickets) * 100 if total_tickets > 0 else 0




        context = {
            'total_usuarios_conectados':users_with_status, #INFORMACION DE LOS USUARIOS CON SESION ACTIVA
            'tickets_pendientes': tickets_pendientes, 
            'sesiones_activas': sesiones_activas,  #SESIONES ACTIVAS
            'tickets_sin_asignar': tickets_sin_asignar,

            'porcentaje_sesiones_activas': porcentaje_sesiones_activas,
            'porcentaje_tickets_pendientes': porcentaje_tickets_pendientes,
            'porcentaje_tickets_sin_asignar': porcentaje_tickets_sin_asignar,
            
            'tickets_por_producto': json.dumps(list(tickets_por_producto)),  # Convertir a JSON
            'tickets_por_categoria': json.dumps(list(tickets_por_categoria)),  # Convertir a JSON

            'filtro_actual': filtro,  # Para saber qué filtro se seleccionó
            'user_group': 'Supervisor',

            'tickets_recientes':tickets_recientes
    }   
     


    else:
        # Lógica para otros usuarios

        user = request.user
        user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=user)
        user_departamento = user_perfil.departamento        
        total_tickets = Ticket.objects.filter(departamento_id=user_departamento, usuario_id=user).count() 
        tickets_pendientes =Ticket.objects.filter(status_id=1, departamento_id=user_departamento, usuario_id=user).count()
        total_tickets_urgentes = Ticket.objects.filter(departamento_id=user_departamento, usuario_id=user, prioridad_id=2, status_id=1).count()

        porcentaje_tickets_pendientes = (tickets_pendientes / total_tickets) * 100 if total_tickets > 0 else 0
        porcentaje_tickets_urgentes = (total_tickets_urgentes / total_tickets) * 100 if total_tickets > 0 else 0

        tickets_urgentes = Ticket.objects.filter(departamento_id=user_departamento, usuario_id=user, prioridad_id=2, status_id=1)


        # DESDE ESTA PARTE, ES NECESARIO CORREGIR LINEAS DE CODIGO PARA TENER LA INFORMACION UNICAMENTE DESDE EL DEPARTAMENTO.
# KPIs RELACIONADOS A TICKETS POR PRODUCTOS
        tickets_por_producto = Ticket.objects.filter(
            departamento_id= user_departamento, usuario_id= user, fecha_creacion__range=(start_date, end_date)
        ).values('producto__descripcion_producto').annotate(count=Count('producto')).order_by('producto__descripcion_producto')



        # KPIs RELACIONADOS A TICKETS POR CATEGORIA
        tickets_por_categoria = Ticket.objects.filter(
             departamento_id= user_departamento, usuario_id= user, fecha_creacion__range=(start_date, end_date)
        ).values('categoria__descripcion_categoria').annotate(count=Count('categoria')).order_by('categoria__descripcion_categoria')


        context = {'user_group': 'otro',
                   'tickets_pendientes': tickets_pendientes, 
                   'porcentaje_tickets_pendientes': porcentaje_tickets_pendientes,
                   'tickets_recientes':tickets_recientes,
                   'tickets_urgentes':tickets_urgentes,
                   'total_tickets_urgentes':total_tickets_urgentes,
                   'porcentaje_tickets_urgentes':porcentaje_tickets_urgentes,
                   'tickets_por_producto': json.dumps(list(tickets_por_producto)),  # Convertir a JSON
                   'tickets_por_categoria': json.dumps(list(tickets_por_categoria)) # Convertir a JSON
                  
                   }
    


    return render(request, 'panel_principal.html', context)




# TABLA DE TICKETS
@login_required #PROTECCION: INICIO DE SESION REQUERIDO PARA ACCEDER A LA INFORMACION

@never_cache
def view_tabla_ticket(request):   
    # Obtener el usuario actual
    user = request.user
    user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=user)
    user_departamento = user_perfil.departamento

    producto_lista = Producto.objects.all()
    
    status_lista = Status.objects.all()
    prioridad_lista = Prioridad.objects.all()
    departamentos_lista = Departamento.objects.all()



    
    
    # Personalizar el contenido basado en el grupo del usuario
    if user.groups.filter(name='Supervisor').exists():
        lista_ticket = Ticket.objects.prefetch_related('categoria', 'contacto', 'status', 'usuario', 'departamento').filter(departamento_id=user_departamento)

 

        categoria_lista = Categoria.objects.all()
        # Lógica para los usuarios en el grupo "Grupo_Admin"
        data = {'tickets':lista_ticket, 
                'user_group': 'Supervisor',
                'lista_productos':producto_lista,
                'lista_categoria':categoria_lista,
                'status_lista':status_lista,
                'prioridad_lista':prioridad_lista,
                'departamentos_lista':departamentos_lista,

                }
    else:
        lista_ticket = Ticket.objects.prefetch_related('categoria', 'contacto', 'status').filter(usuario_id=user)


        perfiles_activos = Perfil_Usuario.objects.filter(
        user__is_active=True,
        departamento_id=user_departamento
    )
        

        categoria_lista = Categoria.objects.filter(id__in=[1, 2])
        # Lógica para los usuarios en el grupo "Grupo_Soporte"
        data = {'tickets': lista_ticket, 
                'user_group': 'otro',
                'lista_productos':producto_lista,
                'lista_categoria':categoria_lista,
                'status_lista':status_lista,
                'prioridad_lista':prioridad_lista,
                'perfiles_activos':perfiles_activos}
     
    return render(request, 'tabla_ticket.html', data)




# FORMULARIO PARA VER Y EDITAR INFORMACION DEL TICKET / FORMULARIO PARA AÑADIR NOTAS PRIVADAS O RESPONDER A CLIENTES  
@login_required
@never_cache
def view_formulario_ticket(request, id):

    ticket = get_object_or_404(Ticket, id=id)
    user = request.user
    # Verificar si ya existe un registro de vista para este ticket por este usuario
    vista, created = TicketVisto.objects.get_or_create(usuario=user, ticket=ticket)
    if not created:
        # Si la vista ya existía, actualiza la fecha de visualización
        vista.fecha_vista = timezone.now()
        vista.save()

    lista_notas = Notas.objects.filter(ticket=id).order_by('-fecha_nota')
    ticket_data = get_object_or_404(Ticket.objects.select_related('categoria', 'contacto', 'status', 'origen_ticket', 'usuario', 'departamento'), id=id)

    # Obtener el perfil del usuario relacionado con el ticket

    
    if ticket_data.usuario is not None:
        # Obtener el perfil del usuario relacionado con el ticket
        perfil_usuario = get_object_or_404(Perfil_Usuario, user_id=ticket_data.usuario.id)

        # Concatenar el puesto del usuario con otros datos (si es necesario)
        puesto_usuario = perfil_usuario.nombre_puesto

        contexto_perfil = f"{puesto_usuario}"
    else:
        contexto_perfil = None


    perfil_departamento= ticket_data.departamento


    categoria_lista = Categoria.objects.all()
    producto_lista = Producto.objects.all()
    status_lista = Status.objects.all()
    prioridad_lista = Prioridad.objects.all()
    perfiles_lista = Perfil_Usuario.objects.filter(departamento_id=perfil_departamento, user__is_active=True,)
    departamentos_lista = Departamento.objects.all()

    # Obtén todos los grupos del usuario
    grupos = user.groups.all()
    
    grupo_nombre = None
    if grupos.exists():
        grupo = grupos.first()  # Obtén el primer grupo del usuario
        grupo_nombre = grupo.name



    data = {'notas': lista_notas, 
            'ticket': ticket_data, 
            'categorias' : categoria_lista, 
            'productos' : producto_lista,
            'lista_status' : status_lista,
            'lista_prioridad' : prioridad_lista,
            'perfiles_lista':perfiles_lista,
            'departamentos_lista':departamentos_lista,
            'user_group':grupo_nombre,
            'contexto_perfil':contexto_perfil,
            }

    return render(request, 'formulario_ticket.html', data)



#Pendiente
@login_required
def crear_ticket_usuario_ajax(request):
    if request.method == 'POST':

        usuario=request.user
        user_perfil = get_object_or_404(Perfil_Usuario.objects.select_related('departamento'), user=usuario)


        nombres = usuario.first_name
        apellidos = usuario.last_name
        nombre_puesto = user_perfil.nombre_puesto

        email = usuario.email
        telefono = user_perfil.telefono_usuario
        producto_id = request.POST.get('select_producto')
        categoria_id = request.POST.get('select_categoria')
        status_id = request.POST.get('select_status')
        prioridad_id = request.POST.get('select_prioridad')
        form_descripcion_notas = request.POST.get('descripcion_incidente')
        nombre_empresa = "Grupo ASICA"
        
        if usuario.groups.filter(name='Supervisor').exists():
            print ("SUPERVISOR")
            usuario_select_id = request.POST.get('select_usuario') 
            departamento_id = request.POST.get('select_departamento') 

            
        else:
            print ("PERSONAL")
            departamento_id = user_perfil.departamento_id
            usuario_select_id = request.POST.get('select_usuario_personal') 



        print (usuario_select_id)

        
       
        # Buscar un contacto existente que coincida en email
        contacto_existente = Contacto.objects.filter(email_contacto=email).first()

        if contacto_existente:
            # Si se encuentra un contacto con el mismo email, actualizarlo si hay datos nuevos
            contacto_datos = contacto_existente
            if contacto_datos.telefono_contacto != telefono:
                contacto_datos.telefono_contacto = telefono
            if contacto_datos.nombre_contacto != nombres:
                contacto_datos.nombre_contacto = nombres
            if contacto_datos.apellido_contacto != apellidos:
                contacto_datos.apellido_contacto = apellidos
            contacto_datos.save()
        else:
            # Crear un nuevo contacto si no hay coincidencia en el email
            contacto_datos = Contacto.objects.create(
                nombre_contacto=nombres,
                apellido_contacto=apellidos,
                email_contacto=email,
                telefono_contacto=telefono,
                empresa_contacto = nombre_empresa

            )

        # Crear el ticket asociado al contacto
        ticket_datos = Ticket.objects.create(
            contacto=contacto_datos,
            producto_id=producto_id,
            categoria_id=categoria_id,
            status_id=status_id,  # Asumimos que hay un status inicial por defecto
            origen_ticket_id = 3,
            departamento_id = departamento_id,
            prioridad_id = prioridad_id,
            usuario_id = usuario_select_id

        )

        # Crear la nota asociada al ticket
        nota_datos = Notas.objects.create(
            ticket=ticket_datos,
            descripcion_notas=form_descripcion_notas,
            tipo_nota_id=1,
            autor = f"{nombres} {apellidos} (Usuario: {usuario.username} | {nombre_puesto})"
        )



        return JsonResponse({
            'success': True,

        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def view_cargar_usuarios_ajax(request, id):
    # Filtrar los perfiles de usuarios activos en el departamento específico
    perfiles_activos = Perfil_Usuario.objects.filter(
        user__is_active=True,
        departamento_id=id
    )
    


    # Serializar los usuarios manualmente, extrayendo los campos necesarios
    usuarios_lista = [
        {
            'id': perfil.user_id,
            'nombre_puesto': perfil.nombre_puesto,
            'first_name': perfil.user.first_name,
            'last_name': perfil.user.last_name,
            'username': perfil.user.username
            
        }
        for perfil in perfiles_activos
    ]
    
    return JsonResponse({'usuarios': usuarios_lista})
