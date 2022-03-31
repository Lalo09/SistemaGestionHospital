"""gestionHospital URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from django.urls.conf import include
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.pagina_login,name='login'),
    path('logout',views.pagina_deslogueo,name='logout'),
    path('pago/',views.pago,name='pago'),
    path('guardar-paciente/',views.guardar_paciente,name='guardar-paciente'),
    path('imprimir-pago/',views.imprimir_pago,name='imprimir-pago'),
    path('reimpresion/',views.reimprimir,name='reimprimir'),
    path('estatus-pago/',views.estatus_pago,name='estatus-pago'),
    path('reporte/',views.reporte,name='reporte'),
    path('mostrar-doctor',views.mostrar_doctor,name='mostrar-doctor'),
    path('mostrar-cobros',views.mostrar_cobros,name='mostrar-cobros'),
    path('mostrar-pagos',views.mostrar_pagos,name='mostrar-pagos'),
    path('cambiar-estatus/<int:id>',views.cambiar_estatus,name='cambiar-estatus'),
    path('actualizar-estatus',views.actualizar_estatus,name='actualizar-estatus'),
    path('filtrar-reporte',views.filtrar_reporte,name='filtrar-reporte'),
    path('imprimir-reporte-filtro',views.imprimir_reporte_filtro,name='imprimir-reporte-filtro'),
    #path('imprimir-reporte-filtro',views.imprimir_reporte_filtro,name='imprimir-reporte-filtro'),
    path('generar-ticket/',views.generar_ticket,name='generar-ticket'),
    path('reimprimir-ticket/<int:id>',views.reimprimir_ticket,name='reimprimir-ticket'),
    path('exportar-reporte/',views.exportar,name='exportar-reporte'),
    path('pdf',views.GeneratePdf.as_view(),name='pdf'),
    path('pdf-reimprimir/',views.GeneratePdf_reimprimir.as_view(),name='pdf-reimprimir'),
    path('',include('depositos.urls'))
]