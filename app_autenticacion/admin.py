from django.contrib import admin
from app_autenticacion.models import Perfil_Usuario, Invitacion_Usuario

# Register your models here.


@admin.register(Perfil_Usuario)
class Perfil_UsuarioAdmin(admin.ModelAdmin):
    list_display= ('nombre_completo', 'nombre_puesto', 'telefono_usuario')  # Campos que se mostrarán en la lista
    search_fields = ('nombre_contacto',)



@admin.register(Invitacion_Usuario)
class Invitacion_UsuarioAdmin(admin.ModelAdmin):
    list_display= ('email',)  # Campos que se mostrarán en la lista
    search_fields = ('email',)


