import random
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User
from app_contactos.models import Contacto
# MODELOS O TABLAS CATALOGOS 

#TABLA STATUS 
class Status(models.Model):
	descripcion_status = models.CharField(max_length=30)

	def __str__(self):
		return self.descripcion_status
	
#TABLA CATEGORIA	
class Categoria(models.Model):
	descripcion_categoria = models.CharField(max_length=50)

	def __str__(self):
		return self.descripcion_categoria
	
#TABLA PRIORIDAD
class Prioridad(models.Model):
	descripcion_prioridad = models.CharField(max_length=50)

	def __str__(self):
		return self.descripcion_prioridad
	
	
#TABLA PRODUCTO    
class Producto(models.Model):
	descripcion_producto = models.CharField(max_length=50)
	def __str__(self):
		return self.descripcion_producto	
	

#TABLA DEPARTAMENTO
class Departamento(models.Model):
	descripcion_departamento = models.CharField(max_length=50)
	def __str__(self):
		return self.descripcion_departamento
	

#TABLA TIPO NOTAS
class Tipo_Nota(models.Model):
	descripcion_tipo_nota = models.CharField(max_length=50)
	def __str__(self):
		return self.descripcion_tipo_nota	
	

# TABLA ORIGEN TICKET (Sirve para identificar si un ticket proviene de el formulario de contacto, de un empleado de Grupo ASICA o por medio de un email directo)
class Origen_Ticket(models.Model):
	descripcion_origen_ticket = models.CharField(max_length=50)
	def __str__(self):
		return self.descripcion_origen_ticket	



# FUNCION PARA GENERAR NUMEROS DE TICKETS UNICOS ALEATORIOS
def generate_ticket_number():
    date_part = timezone.now().strftime('%d%m%y')
    while True:
        random_part = f'{random.randint(0, 999999):06}'  # 6 dígitos numéricos
        ticket_number = f'{random_part}-{date_part}'
        if not Ticket.objects.filter(numero_ticket=ticket_number).exists():
            return ticket_number

# TABLA TICKETS (Guarda toda la información relacionada con los tickets)
class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    contacto = models.ForeignKey('app_contactos.Contacto', on_delete=models.PROTECT)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT, null=True)
    status = models.ForeignKey('Status', on_delete=models.PROTECT)
    prioridad = models.ForeignKey('Prioridad', on_delete=models.PROTECT, null=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, null=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    departamento = models.ForeignKey('Departamento', on_delete=models.PROTECT, null=True)
    numero_ticket = models.CharField(max_length=13, unique=True, default=generate_ticket_number)
    fecha_creacion = models.DateTimeField(default=timezone.now, blank=True)
    origen_ticket = models.ForeignKey('Origen_Ticket', on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        if not self.numero_ticket:
            self.numero_ticket = generate_ticket_number()
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return "{}--{}--{}--{}--{}--{}--{}--{}".format(
            self.contacto, self.producto, self.status, self.prioridad, self.categoria, self.fecha_creacion, self.numero_ticket, self.usuario
        )
	   


#TABLA NOTAS (Guarda las notas o mensajes de cada ticket)
class Notas(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion_notas = models.TextField(max_length=350, null=False, blank=False)
    ticket = models.ForeignKey('Ticket', on_delete=models.PROTECT)
    tipo_nota = models.ForeignKey('Tipo_Nota', on_delete=models.PROTECT)
    fecha_nota = models.DateTimeField(default=timezone.now, blank=True)
    message_id = models.CharField(max_length=255, null=True, blank=True)  
    autor = models.CharField(max_length=50, null=True, blank=True)  

    def __str__(self):
        return "{}--{}--{}".format(self.descripcion_notas, self.fecha_nota, self.autor)
	



class TicketVisto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    fecha_vista = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.usuario} viewed {self.ticket} on {self.fecha_vista}'
	

    

# Modelo de Notificación
class Notificacion(models.Model):
    NOTIFICACION_TIPOS = [
        ('ticket_creado', 'Ticket Creado'),
        ('ticket_asignado', 'Ticket Asignado'),
        ('ticket_cerrado', 'Ticket Cerrado'),
        ('ticket_urgente', 'Ticket Urgente'),
    ]

    titulo = models.CharField(max_length=50, blank=True)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    visto = models.BooleanField(default=False)
    ignorado = models.BooleanField(default=False)
    tipo_notificacion = models.CharField(max_length=20, choices=NOTIFICACION_TIPOS, default='ticket_creado')
    ticket = models.ForeignKey('Ticket', on_delete=models.PROTECT, null=True, blank=True)
    usuario_asignado = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones_asignado')
    solo_supervisores = models.BooleanField(default=False)  # Campo opcional

    def __str__(self):
        return f"{self.tipo_notificacion} - {self.mensaje} - {self.fecha_creacion}"

    class Meta:
        ordering = ['-fecha_creacion']

# TABLA EMAIL    
class Email(models.Model):
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)
    message_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}--{}--{}--{}--{}--{}".format(self.sender, self.recipient, self.subject, self.body, self.received_at, self.message_id)    