from django.contrib import admin
from app_tickets.models import *
# Register your models here.

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('descripcion_status',)
    search_fields = ('descripcion_status',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('descripcion_categoria',) 
    search_fields = ('descripcion_categoria',)

@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    list_display = ('descripcion_prioridad',)  
    search_fields = ('descripcion_prioridad',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('descripcion_producto',)  
    search_fields = ('descripcion_producto',)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('descripcion_departamento',)  
    search_fields = ('descripcion_departamento',)



@admin.register(Tipo_Nota)
class Tipo_NotaAdmin(admin.ModelAdmin):
    list_display = ('descripcion_tipo_nota',)  
    search_fields = ('descripcion_tipo_nota',)


@admin.register(Origen_Ticket)
class Origen_TicketAdmin(admin.ModelAdmin):
    list_display = ('descripcion_origen_ticket',)  
    search_fields = ('descripcion_origen_ticket',)



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('numero_ticket',)
    search_fields = ('numero_ticket',)



@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo',)  
    search_fields = ('titulo',)


@admin.register(Notas)
class NotasAdmin(admin.ModelAdmin):
    list_display = ('id', 'autor') 
    search_fields = ('id',)

