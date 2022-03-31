from django.contrib import admin
from django.urls import path
from depositos import views

urlpatterns = [
    path('deposito/',views.deposito,name='deposito'),
    path('realizar-deposito/',views.realizar_deposito,name='realizar-deposito'),
    path('imprimir-deposito/',views.imprimir_deposito,name='imprimir-deposito'),
    path('ticket-deposito',views.GeneratePdf.as_view(),name='ticket-deposito'),
    path('reimprimir-deposito',views.reimprimir_deposito,name='reimprimir-deposito'),
    path('reimprimir-ticket-deposito',views.GeneratePdf_reimprimir.as_view(),name='reimprimir-ticket-deposito'),
    path('mostrar-depositos',views.mostrar_depositos,name='mostrar-depositos'),
    path('reporte-deposito',views.reporte,name='reporte-deposito'),
    path('exportar-reporte-deposito',views.exportar,name='exportar-reporte-deposito')
]