from django.contrib import admin
from app_tickets.models import *
# Register your models here.

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('descripcion_status',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_status',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('descripcion_categoria',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_categoria',)

@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    list_display = ('descripcion_prioridad',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_prioridad',)

