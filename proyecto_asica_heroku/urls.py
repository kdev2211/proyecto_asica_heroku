"""
URL configuration for proyecto_asica_heroku project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include(('app_contactos.urls', 'app_contactos'), namespace='app_contactos')),
    path('', include(('app_autenticacion.urls', 'app_autenticacion'), namespace='app_autenticacion')),
    path('helpdesk/', include(('app_tickets.urls', 'app_tickets'), namespace='app_tickets')),

    
]
