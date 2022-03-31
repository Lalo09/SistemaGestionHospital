from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.utils import tree
import datetime
from django.contrib.auth.models import User

class Doctor(models.Model):
    codigo = models.CharField(max_length=100,verbose_name='Codigo')
    nombre = models.CharField(max_length=200,verbose_name='Nombre')
    ap_paterno = models.CharField(max_length=200,verbose_name='Apellido paterno')
    ap_materno = models.CharField(max_length=200,verbose_name='Apellido materno')

    class Meta:
        verbose_name='Doctor'
        verbose_name_plural = 'Doctores'

    def __str__(self):
        return self.codigo + "-" + self.nombre + " " + self.ap_paterno + " " + self.ap_materno

class Paciente(models.Model):
    nombre = models.CharField(max_length=200,verbose_name='Nombre')
    ap_paterno = models.CharField(max_length=200,verbose_name='Apellido paterno')
    ap_materno = models.CharField(max_length=200,verbose_name='Apellido materno')

    class Meta:
        verbose_name='Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return self.nombre + " " + self.ap_paterno + " " + self.ap_materno

class Metodos_pago(models.Model):
    codigo = models.CharField(max_length=100,verbose_name='Codigo')
    concepto = models.CharField(max_length=200,verbose_name='Concepto')

    class Meta:
        verbose_name='Metodo de pago'
        verbose_name_plural = 'Metodos de pago'

    def __str__(self):
        return self.concepto

class Pago_honorarios(models.Model):
    doctor = models.ForeignKey(Doctor,verbose_name='Doctor',on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente,verbose_name='Paciente',on_delete=models.CASCADE)
    Metodo_pago = models.ForeignKey(Metodos_pago,verbose_name='Metodo de pago',on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True,verbose_name='Fecha')
    estatus = models.CharField(max_length=200,verbose_name='Estatus')
    cantidad = models.FloatField(verbose_name='Cantidad')

    class Meta:
        verbose_name='Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return  str(self.id) + "-" + str(self.doctor) + "-" + str(self.paciente)

##Modulos y permisos
class Modulo(models.Model):
    titulo = models.CharField(max_length=200,verbose_name='Titulo')

    class Meta:
        verbose_name='Modulo'
        verbose_name_plural = 'Modulos'

    def __str__(self):
        return  str(self.id) + "-" + str(self.titulo)

class Seccion(models.Model):
    modulo = models.ForeignKey(Modulo,verbose_name='modulo',on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200,verbose_name='Titulo') 

    class Meta:
        verbose_name='Seccion'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return  str(self.id) + "-" + str(self.modulo) + "-" + str(self.nombre)

class Permiso(models.Model):
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    modulo = models.ManyToManyField(Modulo,verbose_name='Modulo',null=True,blank=True)

    class Meta:
        verbose_name='Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return  str(self.id) + "-" + str(self.user)

