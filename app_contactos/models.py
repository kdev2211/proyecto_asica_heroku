from django.db import models


# TABLA CONTACTO
class Contacto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_contacto = models.CharField(max_length=30)
    apellido_contacto = models.CharField(max_length=30)
    telefono_contacto = models.CharField(max_length=20, null=True)
    empresa_contacto = models.CharField(max_length=20, null=True)
    email_contacto = models.CharField(max_length=30)
    
    def __str__(self):
        return "{} -- {} -- {} -- {} -- {}".format(
            self.nombre_contacto,
            self.apellido_contacto,
            self.telefono_contacto,
            self.email_contacto,
			self.empresa_contacto,
        )

