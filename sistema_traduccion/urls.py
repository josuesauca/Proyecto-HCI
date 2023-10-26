"""
URL configuration for sistema_traduccion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

import aplicacion.views as vistas

urlpatterns = [
    #URLs Admin
    path('admin/', admin.site.urls),

    #URLs Usuario
    path('', vistas.PaginaInicio,name='index'),
    path('login/', vistas.AccionesUsuario.log_in ,name='login'),
    path('registrarUsuario/', vistas.AccionesUsuario.registro_usuario ,name='registrarUsuario'),
    path('logout/', vistas.AccionesUsuario.log_out ,name='logout'),


    #URLs para generar traduccion
    path('guardarImagen/',vistas.AccionesUsuario.guardar_imagen,name = 'guardarImagen'),

    #URLs para ver traducciones
    path('verTraducciones/',vistas.AccionesUsuario.ver_traducciones_realizadas,name = 'verTraducciones'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)