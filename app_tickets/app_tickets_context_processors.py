from app_tickets.models import Notificacion, Ticket
from app_autenticacion.models import Perfil_Usuario

def notificaciones_usuario(request):
    if request.user.is_authenticated:
        try:
            perfil = Perfil_Usuario.objects.get(user=request.user)
            departamento = perfil.departamento

            # Diccionario para mapear tipos de notificación a íconos de Bootstrap
            tipos_notificacion_iconos = {
                'ticket_asignado': 'bi bi-journal-plus text-primary',
                'ticket_urgente': 'bi bi-exclamation-triangle text-danger',
                'ticket_cerrado': 'bi bi-check-circle text-success',
                'ticket_creado': 'bi bi-exclamation-circle text-warning'
            }

            # Verificar si el usuario pertenece al grupo "Supervisor"
            if request.user.groups.filter(name='Supervisor').exists():
                # Obtener tickets del mismo departamento
                tickets_del_departamento = Ticket.objects.filter(departamento=departamento)

                # Obtener notificaciones visibles para supervisores
                notificaciones_supervisor = Notificacion.objects.filter(
                    ticket__in=tickets_del_departamento,
                    tipo_notificacion__in=['ticket_creado', 'ticket_cerrado'],
                    ignorado=False,
                    solo_supervisores=True
                )

                # Obtener notificaciones urgentes o asignadas específicamente al supervisor
                notificaciones_personales = Notificacion.objects.filter(
                    usuario_asignado=request.user,
                    tipo_notificacion__in=['ticket_asignado', 'ticket_urgente'],
                    ignorado=False
                )

                # Combinar ambas notificaciones para supervisores
                notificaciones = notificaciones_supervisor | notificaciones_personales

            else:
                # Usuarios regulares solo ven sus notificaciones asignadas y urgentes
                notificaciones = Notificacion.objects.filter(
                    usuario_asignado=request.user,
                    tipo_notificacion__in=['ticket_asignado', 'ticket_urgente'],
                    ignorado=False,
                    solo_supervisores=False
                )

            # Lista para almacenar notificaciones con su valor personalizado y su ícono
            notificaciones_lista = []
            for notificacion in notificaciones.distinct():
                icono = tipos_notificacion_iconos.get(notificacion.tipo_notificacion, 'bi bi-info-circle text-info')
                notificaciones_lista.append({
                    'notificacion': notificacion,
                    'icono': icono
                })

            # Conteo de notificaciones no vistas
            notificaciones_conteo = notificaciones.filter(visto=False).count()

            return {
                'notificaciones_lista': notificaciones_lista,
                'notificaciones_conteo': notificaciones_conteo,
            }

        except Perfil_Usuario.DoesNotExist:
            # Manejar el caso en el que no se encuentra el perfil de usuario
            return {
                'notificaciones_lista': [],
                'notificaciones_conteo': 0,
            }

    # Si el usuario no está autenticado, devolvemos un diccionario vacío
    return {
        'notificaciones_lista': [],
        'notificaciones_conteo': 0,
    }