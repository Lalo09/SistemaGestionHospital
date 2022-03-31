from django.contrib import admin
from .models import *
from depositos.models import Deposito

class PagoAdmin(admin.ModelAdmin):
    readonly_fields=('fecha',)

class DepositoAdmin(admin.ModelAdmin):
    readonly_fields=('fecha',)

#Registro de modelos en panel
admin.site.register(Paciente)
admin.site.register(Doctor)
admin.site.register(Metodos_pago)
admin.site.register(Pago_honorarios, PagoAdmin)
admin.site.register(Modulo)
admin.site.register(Deposito, DepositoAdmin)
#admin.site.register(Seccion)
admin.site.register(Permiso)

#Cambiar titulos y subtitulos de panel
title = "Panel de administracion"
subtitle = "Gestion de la aplicacion"

admin.site.site_header = title
admin.site.site_title = title
admin.site.index_title = subtitle