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

    path('admin/', admin.site.urls),
    #path('prueba/', vistas.Inicio,name='prueba'),
    #path('imagenes/', vistas.AccionesUsuario.traducir_texto,name='imagenes'),

    path('', vistas.PaginaInicio,name='index'),

    path('traducirTexto/', vistas.AccionesUsuario.traducir_texto,name='traducirTexto'),
    path('guardarImagen/',vistas.guardarImagen,name = 'guardarImagen'),

    #URLs Usuario
    path('login/', vistas.AccionesUsuario.log_in ,name='login'),
    path('registrarUsuario/', vistas.AccionesUsuario.registro_usuario ,name='registrarUsuario'),
    path('logout/', vistas.AccionesUsuario.log_out ,name='logout'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)