from django.shortcuts import render, redirect
from .models import *


# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def login(request):
    return render(request, 'core/paginas/comun/login.html')

def register(request):
    aux = {}

    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['email']
        contrasenia = request.POST['contrasenia']

        existe_usuario = Usuario.objects.filter(correo=correo).exists()

        if not(existe_usuario) :
            Usuario.objects.create(nombre_completo=nombre, correo=correo, contrasenia=contrasenia, 
                                id_tipo_usuario=TipoUsuario.objects.get(pk=1))
            aux['mensaje'] = 'Usuario creado con éxito'
            return render(request, 'core/paginas/comun/login.html', aux)
        else:
            aux['mensaje'] = 'Ya existe un usuario con ese correo'

    return render(request, 'core/paginas/comun/registro.html', aux)


def lista_categorias(request):
    return render(request, 'core/paginas/comun/lista_categorias.html')


def lista_periodistas(request):
    return render(request, 'core/paginas/comun/lista_periodistas.html')


def noticia(request):
    return render(request, 'core/paginas/comun/noticia.html')


def periodista(request):
    return render(request, 'core/paginas/comun/periodista.html')


def contacto(request):
    aux = {}

    if request.method == 'POST':
        nombre_completo = request.POST['nombre_completo']
        correo = request.POST['correo']
        asunto = request.POST['asunto']
        mensaje = request.POST.get('mensaje')

        Mensaje.objects.create(nombre_completo=nombre_completo, correo=correo, asunto=asunto, mensaje=mensaje)
            
        aux['mensaje'] = 'Mensaje enviado con éxito'
    return render(request, 'core/paginas/comun/contacto.html', aux)


def crear_noticia(request):
    lista_categorias = CategoriaNoticia.objects.all()
    aux = {
        "categorias": lista_categorias
    }

    if request.method == 'POST':
        titulo = request.POST['titulo']
        ubicacion = request.POST['ubicacion']
        categoria = request.POST['categoria']
        cuerpo = request.POST.get('cuerpo')
        portada = request.FILES.getlist('portada')[0]
        carrusel = request.FILES.getlist('carrusel')

        existe_noticia = Noticia.objects.filter(titulo=titulo).exists()

        if existe_noticia:
            aux['mensaje'] = 'Ya existe una noticia con ese título'
        elif categoria == "0":
            aux['mensaje'] = 'Debe seleccionar una categoría válida'
        else:
            categoria = CategoriaNoticia.objects.get(id=categoria)
            autor = Usuario.objects.get(id=1)
            estado_noticia = EstadoNoticia.objects.get(id=1)

            nvaNoticia = Noticia.objects.create(titulo=titulo, ubicacion=ubicacion, portada= portada, cuerpo=cuerpo,
                                                id_categoria=categoria, id_autor=autor, id_estado_noticia=estado_noticia)
            
            for imagen in carrusel:
                GaleriaImagenes.objects.create(imagen=imagen, id_noticia=nvaNoticia)
            
            aux['mensaje'] = 'Noticia creada con éxito'

            

    return render(request, 'core/paginas/periodista/crear_noticia.html', aux)


def editar_noticia(request):
    return render(request, 'core/paginas/periodista/editar_noticia.html')


def lista_noticias_publicadas(request):
    return render(request, 'core/paginas/periodista/lista_noticias_publicadas.html')


def noticia_rechazada(request):
    return render(request, 'core/paginas/periodista/noticia_rechazada.html')


def crear_periodista(request):
    aux = {}

    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        correo = request.POST['email']
        contrasenia = request.POST['contrasenia']
        foto_perfil = request.FILES['foto_perfil']

        existe_usuario = Usuario.objects.filter(correo=correo).exists()

        if not(existe_usuario) :
            nvo_periodista = Usuario.objects.create(nombre_completo=nombre, correo=correo, contrasenia=contrasenia, 
                                id_tipo_usuario=TipoUsuario.objects.get(pk=2))
            PerfilPeriodista.objects.create(descripcion=descripcion, id_usuario=nvo_periodista, foto_perfil=foto_perfil)
            
            aux['mensaje'] = 'Periodista creado con éxito'
        else:
            aux['mensaje'] = 'Ya existe un usuario con ese correo'

    return render(request, 'core/paginas/admin/crear_periodista.html',aux)


def editar_periodista(request, id):
    periodista = Usuario.objects.get(id=id)
    perfil_periodista = PerfilPeriodista.objects.get(id_usuario=periodista.id)
    aux = {
        'periodista': periodista,
        'perfil_periodista': perfil_periodista
    }

    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        correo = request.POST['email']
        contrasenia = request.POST['contrasenia']
        foto_perfil = request.FILES['foto_perfil']

        

        if periodista.correo != correo:
            existe_usuario = Usuario.objects.filter(correo=correo).exists()
            if existe_usuario:
                aux['mensaje'] = 'Ya existe un usuario con ese correo'
                return render(request, 'core/paginas/admin/editar_periodista.html', aux)
            
        periodista.nombre_completo = nombre
        periodista.correo = correo
        periodista.contrasenia = contrasenia
        perfil_periodista.descripcion = descripcion
        perfil_periodista.foto_perfil = foto_perfil
        periodista.save()
        perfil_periodista.save()
        aux['mensaje'] = 'Periodista modificado con éxito'

    return render(request, 'core/paginas/admin/editar_periodista.html', aux)


def eliminar_periodista(request, id):
    periodista = Usuario.objects.get(id=id)
    periodista.delete()
    return redirect(to='lista_periodistas_admin')

def lista_noticias_en_espera(request):
    list_noticias = Noticia.objects.filter(id_estado_noticia=1)
    aux = {
        'lista_noticias': list_noticias
    }
    return render(request, 'core/paginas/admin/lista_noticias_en_espera.html', aux)


def lista_periodistas_admin(request):
    list_periodistas = Usuario.objects.filter(id_tipo_usuario=2)
    aux = {
        'lista_periodistas' : list_periodistas
    }

    return render(request, 'core/paginas/admin/lista_periodistas.html', aux)


def noticia_en_espera(request, id):
    aux = {}
    noticia = Noticia.objects.get(id=id)
    existe_galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id).exists()

    if existe_galeria:
        galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id)
        aux ['galeria'] = galeria

    aux ['noticia'] = noticia

    if request.method == 'POST':
        noticia.id_estado_noticia = EstadoNoticia.objects.get(id=3)
        noticia.save()
        mensaje = request.POST.get('mensaje')
        MensajeRechazoNoticia.objects.create(mensaje_rechazo=mensaje, id_noticia=noticia)
        return redirect(to='lista_noticias_en_espera')

    return render(request, 'core/paginas/admin/noticia_en_espera.html', aux)

def aceptar_noticia(request, id):
    aux = {}
    noticia = Noticia.objects.get(id=id)
    noticia.id_estado_noticia = EstadoNoticia.objects.get(id=2)
    noticia.save()

    aux ['mensaje'] = 'Noticia aceptada con éxito'

    return redirect(to='lista_noticias_en_espera')
