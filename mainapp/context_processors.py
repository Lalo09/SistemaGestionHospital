from mainapp.models import Permiso

def permisos(request):
    permisos = Permiso.objects.filter(user = request.user.id)
    return {'permisos':permisos}