from django.shortcuts import render
from app_tickets.models import Producto, Contacto, Ticket, Notas, Categoria
from django.http import JsonResponse


# Formulario de contacto, usado para enviar consultas directamente a la base de datos, estas crearan los tickets que podran ser visualizados
# en la template "tabla_tickets.html".
def view_formulario_contacto(request):
    categoria_lista = Categoria.objects.all()
    producto_lista = Producto.objects.all()
    
    data = {'productos': producto_lista, 'categorias': categoria_lista}
    
    return render(request, 'formulario_contacto.html', data)


# Maneja los datos enviados por el formulario anterior mediante una solicitud AJAX para guardarlos como tickets en la base de datos.
def view_enviar_consulta_ajax(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email').lower()
        telefono = request.POST.get('telefono')
        producto_id = request.POST.get('producto')
        categoria_id = request.POST.get('categoria_consulta')
        descripcion_notas = request.POST.get('descripcion_incidente')
        nombre_empresa = request.POST.get('empresa')

        # Condicion que define el departamento al que un ticket será enviado basado en la categoria o tipo de consulta que un cliente haga. 
        if categoria_id in ["1", "2"]:
            departamento = 1
        elif categoria_id == "3":
            departamento = 2
        
       
        # Buscar un contacto existente que coincida en email
        contacto_existente = Contacto.objects.filter(email_contacto=email).first()

        if contacto_existente:
            # Si se encuentra un contacto con el mismo email, actualizarlo si hay datos nuevos
            contacto_datos = contacto_existente
            if contacto_datos.telefono_contacto != telefono:
                contacto_datos.telefono_contacto = telefono
            if contacto_datos.nombre_contacto != nombre:
                contacto_datos.nombre_contacto = nombre
            if contacto_datos.apellido_contacto != apellido:
                contacto_datos.apellido_contacto = apellido
            contacto_datos.save()
        else:
            # Crear un nuevo contacto si no hay coincidencia en el email
            contacto_datos = Contacto.objects.create(
                nombre_contacto=nombre,
                apellido_contacto=apellido,
                email_contacto=email,
                telefono_contacto=telefono,
                empresa_contacto = nombre_empresa

            )

        # Crear el ticket asociado al contacto
        ticket_datos = Ticket.objects.create(
            contacto=contacto_datos,
            producto_id=producto_id,
            categoria_id=categoria_id,
            status_id=1,  # Asumimos que hay un status inicial por defecto
            origen_ticket_id = 1,
            departamento_id = departamento,
            prioridad_id = 1

        )

        # Crear la nota asociada al ticket
        nota_datos = Notas.objects.create(
            ticket=ticket_datos,
            descripcion_notas=descripcion_notas,
            tipo_nota_id=1,
            autor = f"{nombre} {apellido}"
        )

        return JsonResponse({
            'success': True,
            'contacto_id': contacto_datos.id,
            'ticket_id': ticket_datos.id,
            'nota_id': nota_datos.id
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def view_tabla_contactos(request):
    lista_contactos = Contacto.objects.all()
    
    data = {'lista_contactos': lista_contactos}
    
    return render(request, 'tabla_contactos.html', data)
