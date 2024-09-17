from django.shortcuts import render

from django.http import JsonResponse


# Formulario de contacto, usado para enviar consultas directamente a la base de datos, estas crearan los tickets que podran ser visualizados
# en la template "tabla_tickets.html".
def view_formulario_contacto(request):

    
    
    return render(request, 'formulario_contacto.html' )

