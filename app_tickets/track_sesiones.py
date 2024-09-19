from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.cache import cache
from datetime import timedelta

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Guardar la hora de la última solicitud del usuario
            cache.set(f'last_seen_{request.user.username}', now(), timeout=60*60)  # 1 hora de inactividad
        response = self.get_response(request)
        return response

    @staticmethod
    def get_users_with_status(department=None, timeout_minutes=5):
        User = get_user_model()
        users_with_status = []

        users = User.objects.filter(is_active=True)
        if department:
            users = users.filter(perfil_usuario__departamento=department)  # Filtro por departamento

        for user in users:
            last_seen = cache.get(f'last_seen_{user.username}')
            is_active = last_seen and now() - last_seen < timedelta(minutes=timeout_minutes)
            users_with_status.append({
                'user': user,
                'is_active': is_active
            })

        return users_with_status
    

    @staticmethod
    def get_active_user_count(department=None, timeout_minutes=5):
        User = get_user_model()
        active_user_count = 0

        users = User.objects.filter(is_active=True)
        if department:
            users = users.filter(perfil_usuario__departamento=department)  # Filtro por departamento

        for user in users:
            last_seen = cache.get(f'last_seen_{user.username}')
            is_active = last_seen and now() - last_seen < timedelta(minutes=timeout_minutes)
            if is_active:
                active_user_count += 1

        return active_user_count