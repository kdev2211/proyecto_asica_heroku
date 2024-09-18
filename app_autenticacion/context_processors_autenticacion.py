from django.contrib.auth.models import Group
from app_autenticacion.models import Perfil_Usuario


def group_context(request):
    return {
        'es_supervisor': request.user.groups.filter(name='Supervisor').exists(),
        'es__otro': request.user.groups.filter(name='Personal').exists(),
        # Puedes agregar otros grupos si es necesario
    }


def perfil_usuario(request):
    if request.user.is_authenticated:
        perfil = Perfil_Usuario.objects.filter(user=request.user).first()
        return {'perfil_usuario': perfil}
    return {}

