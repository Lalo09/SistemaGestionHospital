from django.db import models
from mainapp.models import Doctor,Paciente,Metodos_pago
from django.contrib.auth.models import User

# Create your models here.
class Deposito (models.Model):
    doctor = models.ForeignKey(Doctor,verbose_name='Doctor',on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente,verbose_name='Paciente',on_delete=models.CASCADE)
    Metodo_pago = models.ForeignKey(Metodos_pago,verbose_name='Metodo de pago',on_delete=models.CASCADE)
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True,verbose_name='Fecha')
    estatus = models.CharField(max_length=200,verbose_name='Estatus')
    cantidad = models.FloatField(verbose_name='Cantidad')
    diagnostico = models.CharField(max_length=200,verbose_name='Diagnostico')
    institucion = models.CharField(max_length=200,verbose_name='Institucion')

    class Meta:
        verbose_name='Deposito'
        verbose_name_plural = 'Depositos'

    def __str__(self):
        return str(self.id) + "-" + str(self.diagnostico) + " " + str(self.cantidad)