from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Ticket, Notificacion
from django.contrib.auth.models import Group
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


old_instance = None

@receiver(post_save, sender=Notificacion)
def enviar_notificacion_via_websocket(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()

        # Asegurarse de que la fecha está en la zona horaria local
        fecha_local = timezone.localtime(instance.fecha_creacion)

        mensaje = {
            'titulo': instance.titulo,
            'mensaje': instance.mensaje,
            'fecha': fecha_local.strftime('%d/%m/%Y - %I:%M %p'),
            'icono': funcion_obtener_icono(instance.tipo_notificacion)
        }

        if instance.solo_supervisores:
            if instance.ticket and instance.ticket.departamento:
                try:
                    # Obtener el grupo de supervisores
                    grupo_supervisores = Group.objects.get(name='Supervisor')
                except Group.DoesNotExist:
                    print("Grupo 'supervisores' no encontrado.")
                    return

                # Obtener todos los usuarios del grupo de supervisores
                supervisores = grupo_supervisores.user_set.filter(perfil_usuario__departamento=instance.ticket.departamento)
                
                for supervisor in supervisores:
                    group_name = f"notificaciones_{supervisor.id}"
                    print(f"Enviando notificación a supervisor {supervisor.id}: {mensaje}")
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "notificacion_message",
                            "message": mensaje
                        }
                    )
            else:
                print("No se puede enviar notificación a supervisores: Ticket o departamento no especificado.")
        elif instance.usuario_asignado is not None:
            print(f"Enviando notificación a usuario {instance.usuario_asignado.id}: {mensaje}")
            async_to_sync(channel_layer.group_send)(
                f"notificaciones_{instance.usuario_asignado.id}",
                {
                    "type": "notificacion_message",
                    "message": mensaje
                }
            )
        else:
            print(f"Enviando notificación general: {mensaje}")
            async_to_sync(channel_layer.group_send)(
                "notificaciones_generales",
                {
                    "type": "notificacion_message",
                    "message": {
                        "titulo": "Notificación general",
                        "mensaje": "Se ha creado una nueva notificación sin usuario asignado.",
                        'fecha': fecha_local.strftime('%d/%m/%Y - %I:%M %p'),
                        "icono": "bi bi-bell"
                    }
                }
            )

def funcion_obtener_icono(tipo_notificacion):
    if tipo_notificacion == 'ticket_creado':
        return 'bi bi-exclamation-circle text-warning'
    elif tipo_notificacion == 'ticket_cerrado':
        return 'bi bi-check-circle text-success'
    elif tipo_notificacion == 'ticket_asignado':
        return 'bi bi-journal-plus text-primary'
    elif tipo_notificacion == 'ticket_urgente':
        return 'bi bi-exclamation-triangle text-danger'
    return 'bi bi-bell'

@receiver(pre_save, sender=Ticket)
def guardar_estado_previo(sender, instance, **kwargs):
    global old_instance
    try:
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        old_instance = None

@receiver(post_save, sender=Ticket)
def notificar_ticket(sender, instance, created, **kwargs):

    global old_instance


    
    if created and instance.usuario is None:
        Notificacion.objects.create(
            titulo="Ticket entrante.",
            mensaje=f"Se ha generado un nuevo ticket con el número {instance.numero_ticket}. Haz click aquí para mas detalles.",
            tipo_notificacion='ticket_creado',
            ticket=instance,
            usuario_asignado=instance.usuario,  # Usuario asignado al ticket
            solo_supervisores=True
        )
    else:
        notificar_urgente = False
        if old_instance and old_instance.usuario != instance.usuario:
            if instance.prioridad.descripcion_prioridad == "Urgente":
                notificar_urgente = True

        notificar_cerrado = False
        if old_instance and old_instance.status != instance.status:
            if instance.status.descripcion_status == "Cerrado":
                notificar_cerrado = True

        notificar_asignado = False
        if old_instance and old_instance.usuario != instance.usuario:
            if instance.prioridad.descripcion_prioridad == "Normal":
                notificar_asignado = True

        if notificar_urgente:
            Notificacion.objects.create(
                titulo="Ticket urgente.",
                mensaje=f"Se te ha asignado el ticket #: {instance.numero_ticket}, el cual ha sido marcado como urgente. Haz click aquí para mas detalles.",
                tipo_notificacion='ticket_urgente',
                ticket=instance,
                usuario_asignado=instance.usuario
            )
        elif notificar_cerrado:
            Notificacion.objects.create(
                titulo="Ticket cerrado.",
                mensaje=f"El ticket {instance.numero_ticket} ha sido cerrado.",
                tipo_notificacion='ticket_cerrado',
                ticket=instance,
                usuario_asignado=instance.usuario,
                solo_supervisores=True
            )
        elif notificar_asignado:
            Notificacion.objects.create(
                titulo="Ticket asignado.",
                mensaje=f"Se te ha asignado el ticket #: {instance.numero_ticket}. Haz click aquí para mas detalles.",
                tipo_notificacion='ticket_asignado',
                ticket=instance,
                usuario_asignado=instance.usuario
            )