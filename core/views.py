from django.shortcuts import render, redirect

from core.forms import CustomUserCreationForm
from django.contrib.auth.models import Group, User
from .models import *

from django.contrib.auth.decorators import login_required, permission_required


# Create your views here.

def register(request):
    aux = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save()
        aux['mensaje'] = "Registro exitoso"
        group = Group.objects.get(name='Lector')
        user.groups.add(group)


    return render(request,"registration/register.html", aux)


def index(request):
    ultimas_noticias = Noticia.objects.filter(id_estado_noticia=2).order_by('-fecha')[:5]
    aux = {
        'lista_noticias': ultimas_noticias
    }

    if request.method == 'POST':
        busqueda = request.POST['busqueda']
        noticias_encontradas = Noticia.objects.raw("""
        SELECT * 
        FROM core_noticia n INNER JOIN core_categorianoticia c ON c.id = n.id_categoria_id INNER JOIN auth_user u ON u.id = n.id_autor_id 
        WHERE ( 
        INSTR(n.titulo, %s) != 0  OR  INSTR(u.first_name || ' ' || u.last_name, %s) != 0 OR  INSTR(c.descripcion, %s) != 0
        ) 
        AND n.id_estado_noticia_id = 2
        """
        , [busqueda, busqueda, busqueda])
    
        aux ['noticias_encontradas'] = noticias_encontradas
        
        
        if len(noticias_encontradas) == 0:
            aux['mensaje'] = 'No se encontraron resultados'

    return render(request, 'core/index.html', aux)


def lista_categorias(request):
    lista_categorias = CategoriaNoticia.objects.all()

    noticias = {}
    for categoria in lista_categorias:
        noticias[categoria.descripcion] = Noticia.objects.filter(id_categoria=categoria.id).filter(id_estado_noticia=2)

    aux = {
        "categorias": noticias.items()
    }

    return render(request, 'core/paginas/comun/lista_categorias.html', aux)


def lista_periodistas(request):
    lista_perfil_periodistas = PerfilPeriodista.objects.all()
    aux = {
        'lista_perfil_periodistas': lista_perfil_periodistas
    }
    return render(request, 'core/paginas/comun/lista_periodistas.html', aux)


def noticia(request, id):
    noticia = Noticia.objects.get(id=id)
    aux = {
        'noticia': noticia,
    }
    existe_galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id).exists()

    if existe_galeria:
        galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id)
        aux ['galeria'] = galeria

    return render(request, 'core/paginas/comun/noticia.html', aux)


def periodista(request, id):
    perfil_periodista = PerfilPeriodista.objects.get(id_usuario=id)
    cantidad_noticias = Noticia.objects.filter(id_autor=id).filter(id_estado_noticia=2).count()
    lista_noticias = Noticia.objects.filter(id_autor=id).filter(id_estado_noticia=2)

    aux = {
        'perfil_periodista': perfil_periodista,
        'cantidad_noticias': cantidad_noticias,
        'lista_noticias': lista_noticias
    }
    
    return render(request, 'core/paginas/comun/periodista.html', aux)


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


@login_required
@permission_required('core.add_noticia')
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

            id_autor = request.user.id
            autor = User.objects.get(id=id_autor)

            estado_noticia = EstadoNoticia.objects.get(id=1)

            nvaNoticia = Noticia.objects.create(titulo=titulo, ubicacion=ubicacion, portada= portada, cuerpo=cuerpo,
                                                id_categoria=categoria, id_autor=autor, id_estado_noticia=estado_noticia)
            
            for imagen in carrusel:
                GaleriaImagenes.objects.create(imagen=imagen, id_noticia=nvaNoticia)
            
            aux['mensaje'] = 'Noticia creada con éxito'

            

    return render(request, 'core/paginas/periodista/crear_noticia.html', aux)

@login_required
@permission_required('core.change_noticia')
def editar_noticia(request, id):
    noticia = Noticia.objects.get(id=id)
    id_usuario = request.user.id
    if(noticia.id_autor.id != id_usuario):
        return redirect(to='lista_noticias_publicadas')

    lista_categorias = CategoriaNoticia.objects.all()
    aux = {
        'noticia': noticia,
        "categorias": lista_categorias
    }

    if request.method == 'POST':
        titulo = request.POST['titulo']
        ubicacion = request.POST['ubicacion']
        categoria = request.POST['categoria']
        cuerpo = request.POST.get('cuerpo')
        portada = request.FILES.getlist('portada')[0]
        carrusel = request.FILES.getlist('carrusel')

        if noticia.titulo != titulo:
            existe_noticia = Noticia.objects.filter(titulo=titulo).exists()
            if existe_noticia:
                aux['mensaje'] = 'Ya existe una noticia con ese título'
                return render(request, 'core/paginas/admin/editar_periodista.html', aux)
        if categoria == "0":
            aux['mensaje'] = 'Debe seleccionar una categoría válida'
            return render(request, 'core/paginas/admin/editar_periodista.html', aux)
            
        categoria = CategoriaNoticia.objects.get(id=categoria)
        noticia.titulo = titulo
        noticia.ubicacion = ubicacion
        noticia.id_categoria = categoria
        noticia.portada = portada
        noticia.cuerpo = cuerpo
        noticia.id_estado_noticia = EstadoNoticia.objects.get(id=1)

        noticia.save()

        galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id).delete()
        for imagen in carrusel:
            GaleriaImagenes.objects.create(imagen=imagen, id_noticia=noticia)

        aux['mensaje'] = 'Noticia modificada con éxito'

    return render(request, 'core/paginas/periodista/editar_noticia.html', aux)

@login_required
@permission_required('core.delete_noticia')
def eliminar_noticia(request,id):
    noticia = Noticia.objects.get(id=id)
    id_usuario = request.user.id
    if(noticia.id_autor.id != id_usuario):
        return redirect(to='lista_noticias_publicadas')
    noticia.delete()
    return redirect(to='lista_noticias_publicadas')


@login_required
@permission_required('core.change_noticia')
def lista_noticias_publicadas(request):
    id = request.user.id
    list_noticias = Noticia.objects.filter(id_autor=id)
    aux = {
        'lista_noticias' : list_noticias
    }

    
    aux['mensaje'] = id

    return render(request, 'core/paginas/periodista/lista_noticias_publicadas.html', aux)

@login_required
@permission_required('core.change_noticia')
def noticia_rechazada(request, id):
    aux = {}
    noticia = Noticia.objects.get(id=id)
    id_usuario = request.user.id
    if(noticia.id_autor.id != id_usuario):
        return redirect(to='lista_noticias_publicadas')
    
    existe_galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id).exists()

    if existe_galeria:
        galeria = GaleriaImagenes.objects.filter(id_noticia=noticia.id)
        aux ['galeria'] = galeria

    aux ['noticia'] = noticia

    mensaje_rechazo = MensajeRechazoNoticia.objects.get(id_noticia=noticia.id)
    aux ['mensaje_rechazo'] = mensaje_rechazo

    return render(request, 'core/paginas/periodista/noticia_rechazada.html', aux)


from django.contrib.auth.hashers import make_password

@login_required
@permission_required('auth.change_user')
def crear_periodista(request):
    aux = {}

    if request.method == 'POST':
        username = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        descripcion = request.POST['descripcion']
        correo = request.POST['email']
        contrasenia = make_password(request.POST['contrasenia'])
        foto_perfil = request.FILES['foto_perfil']

        existe_usuario = User.objects.filter(email=correo).exists()

        if not(existe_usuario) :
            nvo_periodista = User.objects.create(username=username, first_name=nombre, last_name=apellido, email=correo,
                                                password=contrasenia)
            group = Group.objects.get(name='Periodista')
            nvo_periodista.groups.add(group)
            PerfilPeriodista.objects.create(descripcion=descripcion, id_usuario=nvo_periodista, foto_perfil=foto_perfil)
            
            aux['mensaje'] = 'Periodista creado con éxito'
        else:
            aux['mensaje'] = 'Ya existe un usuario con ese correo'

    return render(request, 'core/paginas/admin/crear_periodista.html',aux)


@login_required
@permission_required('auth.change_user')
def editar_periodista(request, id):
    periodista = User.objects.get(id=id)
    perfil_periodista = PerfilPeriodista.objects.get(id_usuario=periodista.id)
    aux = {
        'periodista': periodista,
        'perfil_periodista': perfil_periodista
    }

    if request.method == 'POST':
        username = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        descripcion = request.POST['descripcion']
        correo = request.POST['email']
        contrasenia = make_password(request.POST['contrasenia'])
        foto_perfil = request.FILES['foto_perfil']

        

        if periodista.email != correo:
            existe_usuario = User.objects.filter(email=correo).exists()
            if existe_usuario:
                aux['mensaje'] = 'Ya existe un usuario con ese correo'
                return render(request, 'core/paginas/admin/editar_periodista.html', aux)
            
        periodista.username = username
        periodista.first_name = nombre
        periodista.last_name = apellido
        periodista.email = correo
        periodista.password = contrasenia
        perfil_periodista.descripcion = descripcion
        perfil_periodista.foto_perfil = foto_perfil
        periodista.save()
        perfil_periodista.save()
        aux['mensaje'] = 'Periodista modificado con éxito'

    return render(request, 'core/paginas/admin/editar_periodista.html', aux)

@login_required
@permission_required('auth.delete_user')
def eliminar_periodista(request, id):
    periodista = User.objects.get(id=id)
    periodista.delete()
    return redirect(to='lista_periodistas_admin')

def lista_noticias_en_espera(request):
    list_noticias = Noticia.objects.filter(id_estado_noticia=1)
    aux = {
        'lista_noticias': list_noticias
    }
    return render(request, 'core/paginas/admin/lista_noticias_en_espera.html', aux)

@login_required
@permission_required('auth.change_user')
def lista_periodistas_admin(request):
    list_periodistas = User.objects.raw("""
        SELECT * 
        FROM auth_user u INNER JOIN auth_user_groups g ON u.id = g.user_id
        WHERE g.group_id = 2
        """
        )
    
    aux = {
        'lista_periodistas' : list_periodistas
    }

    return render(request, 'core/paginas/admin/lista_periodistas.html', aux)

@login_required
@permission_required('auth.change_user')
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

@login_required
@permission_required('auth.change_user')
def aceptar_noticia(request, id):
    aux = {}
    noticia = Noticia.objects.get(id=id)
    noticia.id_estado_noticia = EstadoNoticia.objects.get(id=2)
    noticia.save()

    aux ['mensaje'] = 'Noticia aceptada con éxito'

    return redirect(to='lista_noticias_en_espera')

@login_required
@permission_required('auth.change_user')
def lista_mensajes(request):
    lista_mensajes = Mensaje.objects.all()
    aux = {
        'lista_mensajes' : lista_mensajes
    }

    return render(request, 'core/paginas/admin/lista_mensajes.html', aux)

@login_required
@permission_required('auth.change_user')
def mensaje(request, id):
    mensaje = Mensaje.objects.get(id=id)
    aux = {
        "mensaje": mensaje
    }
    return render(request, 'core/paginas/admin/mensaje.html', aux)
