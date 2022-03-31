import depositos
from mainapp.models import Modulo
from django.shortcuts import redirect, render, HttpResponse
from .models import Deposito
from mainapp.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mainapp.utils import render_to_pdf
from django.views.generic import View
import csv
from datetime import datetime

#Mostrar pagina para realizar deposito
@login_required(login_url="login")
def deposito(request):
    metodos = Metodos_pago.objects.all()
    return render(request,'realizar-deposito.html',{
            'title':'Realizar deposito',
            'titleheader':'Realizar deposito',
            'metodos':metodos,
        })

#Registrar deposito
@login_required(login_url="login")
def realizar_deposito(request):
    if request.method =='POST':

        nombre = request.POST['nombre']
        ap_paterno = request.POST['ap_paterno']
        ap_materno = request.POST['ap_materno']

        paciente = Paciente(
            nombre=nombre,
            ap_paterno=ap_paterno,
            ap_materno=ap_materno
        )

        paciente.save()

        doctor = Doctor.objects.get(codigo=request.POST['doctor'])
        nuevopaciente = Paciente.objects.last()
        metodo_pago = Metodos_pago.objects.get(id=request.POST['metodo'])
        user = User.objects.get(id=request.user.id)
        estatus = 'Pagado'
        diagnostico = request.POST['diagnostico']
        cantidad = request.POST['cantidad']
        institucion = request.POST['institucion']

        deposito = Deposito(
            doctor = doctor,
            paciente = nuevopaciente,
            Metodo_pago = metodo_pago,
            user = user,
            estatus = estatus,
            cantidad = cantidad,
            diagnostico = diagnostico,
            institucion = institucion
        )

        deposito.save()
        messages.success(request,f"Deposito con el folio {deposito.id} registrado correctamente")

        return redirect('imprimir-deposito')
    else:
        return HttpResponse("Error")

#Pagina que da la opcion de imprimir deposito
@login_required(login_url="login")
def imprimir_deposito(request):    
    return render(request,'imprimir-deposito.html')

#Pagina que muestra la rempresion
@login_required(login_url="login")
def reimprimir_deposito (request):

    deposito = Deposito.objects.all().order_by('-id')

    return render(request,'reimpresion.html',{
        'title':'Reimpresion de depositos',
        'titleheader':'Reimpresion de depositos',
        'depositos':deposito
    })

#Generar ticket de deposito
class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        deposito = Deposito.objects.last()
        data = {
            'folio':deposito.id,
            'doctor_nombre': deposito.doctor.nombre,
            'doctor_ap_paterno': deposito.doctor.ap_paterno,
            'doctor_ap_materno': deposito.doctor.ap_materno,
            'paciente_nombre': deposito.paciente.nombre,
            'paciente_ap_paterno': deposito.paciente.ap_paterno,
            'paciente_ap_materno': deposito.paciente.ap_materno, 
            'fecha': deposito.fecha,
            'metodo_pago': deposito.Metodo_pago,
            'cantidad': deposito.cantidad,
            'institucion':deposito.institucion,
            'diagnostico':deposito.diagnostico
        }
        pdf = render_to_pdf('invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

#Reimprimir ticket de deposito
class GeneratePdf_reimprimir(View):
    def get(self, request, *args, **kwargs):
        deposito = Deposito.objects.get(id=self.request.GET.get('lang'))
        data = {
            'folio':deposito.id,
            'doctor_nombre': deposito.doctor.nombre,
            'doctor_ap_paterno': deposito.doctor.ap_paterno,
            'doctor_ap_materno': deposito.doctor.ap_materno,
            'paciente_nombre': deposito.paciente.nombre,
            'paciente_ap_paterno': deposito.paciente.ap_paterno,
            'paciente_ap_materno': deposito.paciente.ap_materno, 
            'fecha': deposito.fecha,
            'metodo_pago': deposito.Metodo_pago,
            'cantidad': deposito.cantidad,
            'institucion':deposito.institucion,
            'diagnostico':deposito.diagnostico
        }
        pdf = render_to_pdf('invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

#Mostrar los depositos por folio
@login_required(login_url="login")
def mostrar_depositos(request):
    if request.method == 'POST':
        deposito = Deposito.objects.get(id=request.POST['name'])
        
        return HttpResponse(f"""
        <table class="table table-hover table-responsive">
                  <thead>
                    <tr>
                      <th scope="col">Folio</th>
                      <th scope="col">Paciente</th>
                      <th scope="col">Diagnostico</th>
                      <th scope="col">Cantidad</th>
                      <th scope="col">Fecha</th>
                      <th scope="col">Metodo de pago</th>
                    </tr>
                  </thead>
                  <tbody>      
                      <tr>
                        <th scope="row">{deposito.id}</th>
                        <td>{deposito.paciente.nombre} {deposito.paciente.ap_paterno} {deposito.paciente.ap_materno}</td>
                        <td>{deposito.diagnostico}</td>
                        <td>{deposito.cantidad}</td>
                        <td>{deposito.fecha}</td>
                        <td>{deposito.Metodo_pago}</td>
                        <!--<td><div class="text-center"><a href="/reimprimir-ticket-deposito/?lang=deposito.id"><button type="submit" class="btn btn-primary">Reimprimir</button></a></div></td>-->
                        <td><div class="text-center"><a href="/reimprimir-ticket-deposito?lang={deposito.id}"><button type="submit" class="btn btn-primary">Reimprimir</button></a></div></td>
                      </tr>                 
                  </tbody>                  
              </table>
        """)

#Mostrar pagina para exportar reporte
#Muestra la pagina para mostrar los reportes
@login_required(login_url="login")
def reporte (request):
    return render(request,'reporte.html',{
        'title':'Reportes de depositos',
        'titleheader':'Reportes'
    })

#Exportar a cvs
@login_required(login_url="login")
def exportar(request):

    if request.method == 'POST':
        desde = request.POST['desde']
        hasta = request.POST['hasta']
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=honorarios.csv'

        writer = csv.writer(response)
        
        depositos = Deposito.objects.raw(f"select * from depositos_deposito where depositos_deposito.fecha >= '{desde}' and depositos_deposito.fecha <= '{hasta}' ")

        writer.writerow(['Folio','Nombre del paciente','Diagnostico','Medico','Institucion','Fecha','Metodo de pago','Cantidad','Estatus'])

        for deposito in depositos:
            fecha = deposito.fecha
            nueva_fecha = datetime.strftime(fecha,'%d/%m/%Y %H:%M')
            writer.writerow([deposito.id,deposito.paciente.nombre +" "+ deposito.paciente.ap_paterno +" "+ deposito.paciente.ap_materno, deposito.diagnostico, deposito.doctor.nombre +" "+ deposito.doctor.ap_paterno +" "+deposito.doctor.ap_materno,deposito.institucion,nueva_fecha,deposito.Metodo_pago,deposito.cantidad,deposito.estatus])

        return response