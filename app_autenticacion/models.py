from datetime import timedelta
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string


#TABLA PERFIL DE USUARIO (Guarda informacion adicional del usuario extendiendo el modelo Django Auth para usuarios)
class Perfil_Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=40, null=True)
    departamento = models.ForeignKey('app_tickets.Departamento', on_delete=models.PROTECT)
    nombre_puesto = models.CharField(max_length=40, null=True)
    telefono_usuario = models.CharField(max_length=20, null=True)

    def __str__(self):
        return "{}--{}--{}--{}".format(self.nombre_completo, self.departamento, self.nombre_puesto, self.telefono_usuario)
    

class Invitacion_Usuario(models.Model):
    email = models.EmailField(unique=True, max_length=60)
    creado_en = models.DateTimeField(auto_now_add=True)
    contrasena_temporal = models.CharField(max_length=20, default=get_random_string(10))
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token_expira_en = models.DateTimeField(default=timezone.now() + timedelta(hours=24))
    token_usado = models.BooleanField(default=False)

    def actualizar_token(self):
        self.token = uuid.uuid4()
        while Invitacion_Usuario.objects.filter(token=self.token).exists():
            self.token = uuid.uuid4()
        self.token_expira_en = timezone.now() + timedelta(hours=24)
        self.token_usado = False
        self.save()

    def es_token_valido(self):
        return timezone.now() < self.token_expira_en and not self.token_usado
    

class Solicitud_Forgot_Password (models.Model):
    email = models.EmailField(max_length=60)
    creado_en = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token_expira_en = models.DateTimeField(default=timezone.now() + timedelta(hours=24))
    token_usado = models.BooleanField(default=False)

    def actualizar_token(self):
        self.token = uuid.uuid4()
        while Invitacion_Usuario.objects.filter(token=self.token).exists():
            self.token = uuid.uuid4()
        self.token_expira_en = timezone.now() + timedelta(hours=24)
        self.token_usado = False
        self.save()

    def es_token_valido(self):
        return timezone.now() < self.token_expira_en and not self.token_usado
    