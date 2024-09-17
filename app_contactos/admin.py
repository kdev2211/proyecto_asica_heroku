from django.contrib import admin
from app_contactos.models import Contacto
# Register your models here.

@admin.register(Contacto)
class ContactosAdmin(admin.ModelAdmin):

    list_display= ('nombre_contacto', 'apellido_contacto')  # Campos que se mostrarán en la lista
    search_fields = ('nombre_contacto',)
