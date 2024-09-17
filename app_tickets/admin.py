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

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('descripcion_producto',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_producto',)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('descripcion_departamento',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_departamento',)



@admin.register(Tipo_Nota)
class Tipo_NotaAdmin(admin.ModelAdmin):
    list_display = ('descripcion_tipo_nota',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_tipo_nota',)


@admin.register(Origen_Ticket)
class Origen_TicketAdmin(admin.ModelAdmin):
    list_display = ('descripcion_origen_ticket',)  # Asegúrate de usar una tupla
    search_fields = ('descripcion_origen_ticket',)






