from os import write
from django.shortcuts import redirect, render, HttpResponse
from reportlab.lib import pagesizes
from .models import *
from django.views.generic import View
from django.views.generic import ListView
from django.contrib import messages
from django.http import FileResponse, response, HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import csv
from .utils import render_to_pdf
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from depositos import views
from datetime import datetime

#pagina para loguearse
def pagina_login(request):    

    if request.user.is_authenticated:
        return redirect('pago')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return redirect('pago')
            else:
                messages.warning(request,"Error en el usuario o contraseña")

        return render(request,'mainapp/login.html',{
            'title':'Ingresar a sistema',
            'titleheader':'Login'
        })

#funcion para desloguearse
def pagina_deslogueo(request):
    logout(request)
    return redirect('login')

#Generar ticket
@login_required(login_url="login")
def generar_ticket(request):
    buf = io.BytesIO()
    c =canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica",14)

    pagos = Pago_honorarios.objects.last()

    lines= [str(pagos.id),str(pagos.doctor.nombre),str(pagos.doctor.ap_paterno),str(pagos.doctor.ap_materno),str(pagos.paciente.nombre),str(pagos.paciente.ap_paterno),str(pagos.paciente.ap_materno),str(pagos.Metodo_pago),str(pagos.fecha),str(pagos.cantidad)]

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename="reporte.pdf")
    
#Reimprimir ticket
@login_required(login_url="login")
def reimprimir_ticket(request,id):
    buf = io.BytesIO()
    c =canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica",14)

    pagos = Pago_honorarios.objects.get(id=id)

    lines= [str(pagos.id),str(pagos.doctor.nombre),str(pagos.doctor.ap_paterno),str(pagos.doctor.ap_materno),str(pagos.paciente.nombre),str(pagos.paciente.ap_paterno),str(pagos.paciente.ap_materno),str(pagos.Metodo_pago),str(pagos.fecha),str(pagos.cantidad)]

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename="reporte.pdf")

#Exportar a cvs
@login_required(login_url="login")
def exportar(request):

    if request.method == 'POST':
        codigo = request.POST['doctor']        
        desde = request.POST['desde']
        hasta = request.POST['hasta']
        est = request.POST['estatus']

        #return HttpResponse(hasta)
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=honorarios.csv'

        writer = csv.writer(response)
        
        if codigo != "":
            doctor = Doctor.objects.get(codigo=codigo)
            if est == "todos":               
                pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.doctor_id='{doctor.id}' and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
            else:
                pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.doctor_id='{doctor.id}' and estatus = '{est}' and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")

        elif est == "todos":
            pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
        else:
            pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where estatus = '{est}'and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
        #pagos = Pago_honorarios.objects.all()

        writer.writerow(['Folio','Doctor','Paciente','Metodo de pago','Fecha','Cantidad','Estatus'])

        for pago in pagos:
            fecha = pago.fecha
            nueva_fecha = datetime.strftime(fecha,'%d/%m/%Y %H:%M')
            writer.writerow([pago.id,pago.doctor.nombre +" "+ pago.doctor.ap_paterno +" "+ pago.doctor.ap_materno,pago.paciente,pago.Metodo_pago,nueva_fecha,pago.cantidad,pago.estatus])

        return response
        #return HttpResponse("hello")

#Muestra la ventana principal de pago
@login_required(login_url="login")
def pago (request):
    #permisos = Permiso.objects.filter(user = request.user.id)
    metodos = Metodos_pago.objects.all()
    
    return render(request,'mainapp/index.html',{
        'title':'Pago de honorarios',
        'titleheader':'Pago de honorarios',
        'metodos':metodos,
        #'permisos':permisos
    })

#Registra primero el paciente y despues el pago
@login_required(login_url="login")
def guardar_paciente(request):

    if request.method =='POST':
        #get data paciente
        nombre = request.POST['nombre']
        ap_paterno = request.POST['ap_paterno']
        ap_materno = request.POST['ap_materno']

        #save paciente
        paciente = Paciente(
            nombre=nombre,
            ap_paterno=ap_paterno,
            ap_materno=ap_materno
        )

        paciente.save()

        #get id last paciente
        nuevopaciente = Paciente.objects.last()

        #get data cobro
        doctor = Doctor.objects.get(codigo=request.POST['doctor'])
        cantidad = request.POST['cobro']
        metodo_pago = Metodos_pago.objects.get(id=request.POST['metodo']) 

        #save pago
        pago = Pago_honorarios(
            doctor = doctor,
            paciente = nuevopaciente,
            Metodo_pago = metodo_pago,
            estatus = 'No pagada',
            cantidad = cantidad
        )

        pago.save()
        messages.success(request,f"Pago con el folio {pago.id} registrado correctamente")

        return redirect('imprimir-pago')
    else:
        return HttpResponse("Error")

#Pagina para imprimir el pago, recibe un mensaje flash
@login_required(login_url="login")
def imprimir_pago(request):    
    return render(request,'mainapp/imprimir-pago.html')

#Muestra la pagina para reimprimir los pagos
@login_required(login_url="login")
def reimprimir (request):

    pagos = Pago_honorarios.objects.all().order_by('-id')

    return render(request,'mainapp/reimpresion.html',{
        'title':'Reimpresion de pago',
        'titleheader':'Reimpresion de pago',
        'pagos':pagos
    })

#Muestra los estatus de pagos
@login_required(login_url="login")
def estatus_pago (request):
    pagos = Pago_honorarios.objects.all().order_by('-id')
    return render(request,'mainapp/estatus-pago.html',{
        'title':'Estatus de pagos',
        'titleheader':'Estatus de pagos',
        'pagos':pagos
    })

#Muestra la pagina para mostrar los reportes
@login_required(login_url="login")
def reporte (request):
    return render(request,'mainapp/reporte.html',{
        'title':'Reportes de honorarios',
        'titleheader':'Reportes'
    })

#Muestra la opcion de cambiar el estatus de un pago
@login_required(login_url="login")
def cambiar_estatus (request,id):
    pago = Pago_honorarios.objects.filter(pk=id)
    return render(request,'mainapp/cambiar-estatus.html',{
        'title':'Estatus de pago',
        'titleheader':'Estatus de pago',
        'pago': pago
    })

#Actualiza el estatus de un pago
@login_required(login_url="login")
def actualizar_estatus(request):
    if request.method == 'POST':
        folio = request.POST['folio']
        metodo = request.POST['metodo']

        pago = Pago_honorarios.objects.filter(id=folio).update(estatus=metodo)
        
        messages.success(request,f"Estatus de folio {folio} actualizado correctamente")

        return redirect('estatus-pago')
    else:
        return HttpResponse("Error")
        
#Muestra los datos de un doctor
@login_required(login_url="login")
def mostrar_doctor(request):
    if request.method == 'POST':
        doctor = Doctor.objects.get(codigo=request.POST['name'])
        return HttpResponse(f'{doctor.nombre} {doctor.ap_paterno} {doctor.ap_materno}')

#Muestra los cobros
@login_required(login_url="login")
def mostrar_cobros(request):
    if request.method == 'POST':
        pago = Pago_honorarios.objects.get(id=request.POST['name'])
        return HttpResponse(f"""
        <table class="table table-hover table-responsive">
            <thead>
            <tr>
                <th scope="col">Folio</th>
                <th scope="col">Medico</th>
                <th scope="col">Paciente</th>
                <th scope="col">Cantidad</th>
                <th scope="col">Fecha</th>
                <th scope="col">Metodo de pago</th>
            </tr>
            </thead>
            <tbody>                    
            <tr><th scope="row">{pago.id}</th> <td>{pago.doctor.nombre} {pago.doctor.ap_paterno} {pago.doctor.ap_materno}</td> <td>{pago.paciente.nombre} {pago.paciente.ap_paterno} {pago.paciente.ap_materno}</td><td>{pago.cantidad}</td> <td>{pago.fecha}</td><td>{pago.Metodo_pago}</td><td><div class="text-center"><a href="/pdf-reimprimir/?lang={pago.id} "><button type="submit" class="btn btn-primary">Reimprimir</button></a></div></td></tr>           
            </tbody>                  
        </table>
        """)

#Muestra los pagos de honorarios
@login_required(login_url="login")
def mostrar_pagos(request):
    if request.method == 'POST':
        pago = Pago_honorarios.objects.get(id=request.POST['name'])
        return HttpResponse(f"""
        <table class="table table-hover table-responsive">
            <thead>
            <tr>
                <th scope="col">Folio</th>
                <th scope="col">Medico</th>
                <th scope="col">Cantidad</th>
                <th scope="col">Fecha</th>
                <th scope="col">Metodo de pago</th>
                <th scope="col">Estatus</th>
                <th scope="col">Acciones</th>
              </tr>
            </thead>
            <tbody>                    
            <tr><th scope="row">{pago.id}</th> <td>{pago.doctor.nombre} {pago.doctor.ap_paterno} {pago.doctor.ap_materno}</td> <td>{pago.cantidad}</td><td>{pago.fecha}</td> <td>{pago.Metodo_pago}</td><td>{pago.estatus}</td><td><a href="/cambiar-estatus/{pago.id}"><button type="button" class="btn btn-info" data-toggle="modal" data-target="#exampleModal">Cambiar estatus
                  </button></a></td></tr>           
            </tbody>                  
        </table>
        """)

#Muestra datos de doctor
@login_required(login_url="login")
def filtrar_reporte(request):
    if request.method == 'POST':
        doctor = Doctor.objects.get(codigo=request.POST['doctor'])
        return HttpResponse(f'{doctor.nombre} {doctor.ap_paterno} {doctor.ap_materno}')

#Muestra los datos de reporte
@login_required(login_url="login")
def imprimir_reporte_filtro(request):
    if request.method == 'POST':
        codigo = request.POST['doctor']        
        desde = request.POST['desde']
        hasta = request.POST['hasta']
        est = request.POST['estatus']
        
        if codigo != "":
            doctor = Doctor.objects.get(codigo=codigo)
            if est == "todos":               
                pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.doctor_id='{doctor.id}' and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
            else:
                pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.doctor_id='{doctor.id}' and estatus = '{est}' and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")

        elif est == "todos":
            pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
        else:
            pagos = Pago_honorarios.objects.raw(f"select * from mainapp_pago_honorarios where estatus = '{est}'and mainapp_pago_honorarios.fecha >= '{desde}' and mainapp_pago_honorarios.fecha <= '{hasta}' ")
        
        return redirect('exportar-reporte')  
        #return render(request,'mainapp/imprimir-reporte.html',{ 
        #    'pagos':pagos
        #})

#Version obsoleta de ticket
class TicketPago(ListView):
    model = Pago_honorarios
    template_name = 'mainapp/pago.html'
    context_object_name = 'pago'

#Generar comrpobante de pago
class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        pago = Pago_honorarios.objects.last()
        data = {
            'folio':pago.id,
            'doctor_nombre': pago.doctor.nombre,
            'doctor_ap_paterno': pago.doctor.ap_paterno,
            'doctor_ap_materno': pago.doctor.ap_materno,
            'paciente_nombre': pago.paciente.nombre,
            'paciente_ap_paterno': pago.paciente.ap_paterno,
            'paciente_ap_materno': pago.paciente.ap_materno, 
            'fecha': pago.fecha,
            'metodo_pago': pago.Metodo_pago,
            'cantidad': pago.cantidad,
        }
        pdf = render_to_pdf('mainapp/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

#Generar reimpresion de comprobante de pago
class GeneratePdf_reimprimir(View):
    def get(self, request, *args, **kwargs):
        pago = Pago_honorarios.objects.get(id=self.request.GET.get('lang'))
        data = {
           'folio':pago.id,
            'doctor_nombre': pago.doctor.nombre,
            'doctor_ap_paterno': pago.doctor.ap_paterno,
            'doctor_ap_materno': pago.doctor.ap_materno,
            'paciente_nombre': pago.paciente.nombre,
            'paciente_ap_paterno': pago.paciente.ap_paterno,
            'paciente_ap_materno': pago.paciente.ap_materno, 
            'fecha': pago.fecha,
            'metodo_pago': pago.Metodo_pago,
            'cantidad': pago.cantidad,
        }
        pdf = render_to_pdf('mainapp/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')