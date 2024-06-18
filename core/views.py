from django.shortcuts import render, redirect

from core.forms import CustomUserCreationForm
from django.contrib.auth.models import Group, User

from prueba import settings
from .models import *

from django.contrib.auth.decorators import login_required, permission_required

import requests

from rest_framework import generics
from django.core.paginator import Paginator



# Create your views here.

def account_locked(request):
    return render(request,"registration/account_locked.html")

def agradecimiento(request):
    return render(request,"core/paginas/comun/agradecimiento.html")

def donaciones(request):
    aux = {}
    response = requests.get('https://mindicador.cl/api')
    indicadores = response.json()
    del indicadores["version"]
    del indicadores["autor"]
    del indicadores["fecha"]

    aux["dolar"] = indicadores["dolar"]
    aux["defensor"] = "{:,}".format(round(indicadores["dolar"]["valor"] * 5)).replace(",", ".")
    aux["guerrero"] = "{:,}".format(round(indicadores["dolar"]["valor"] * 10)).replace(",", ".")
    aux["paladin"] = "{:,}".format(round(indicadores["dolar"]["valor"] * 20)).replace(",", ".")

    
    return render(request,"core/paginas/comun/donaciones.html", aux)

def register(request):
    aux = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request,"registration/register.html", aux)

        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save()
        aux['mensaje'] = "Registro exitoso"
        group = Group.objects.get(name='Lector')
        user.groups.add(group)
    return render(request,"registration/register.html", aux)


def busqueda(request, page, busqueda):
    ultimas_noticias = Noticia.objects.filter(id_estado_noticia=2).order_by('-fecha')[:5]
    aux = {
        'lista_noticias': ultimas_noticias
    }

    noticias_encontradas = []

    if request.method == 'POST':
        busqueda = request.POST['busqueda']

    aux["busqueda"] = busqueda
    noticias_encontradas = Noticia.objects.raw("""
            SELECT * 
            FROM core_noticia n INNER JOIN core_categorianoticia c ON c.id = n.id_categoria_id INNER JOIN auth_user u ON u.id = n.id_autor_id 
            WHERE ( 
            POSITION(%s IN n.titulo ) != 0  OR  POSITION(%s IN u.first_name || ' ' || u.last_name) != 0 OR POSITION(%s IN c.descripcion ) != 0
            ) 
            AND n.id_estado_noticia_id = 2 ORDER BY n.fecha DESC
            """
            , [busqueda, busqueda, busqueda])

    if len(noticias_encontradas) == 0:
        aux['mensaje'] = 'No se encontraron resultados para ' + busqueda
        return render(request, 'core/index.html', aux)
    
    paginator = Paginator(noticias_encontradas, 2)
    page_number = page
    if request.method == 'POST':
        page_number = 1
    page_obj = paginator.get_page(page_number)

    aux ['noticias_encontradas'] = page_obj

    return render(request, 'core/index.html', aux)
    

def index(request):
    ultimas_noticias = Noticia.objects.filter(id_estado_noticia=2).order_by('-fecha')[:5]
    aux = {
        'lista_noticias': ultimas_noticias
    }

    response = requests.get('https://mindicador.cl/api')
    indicadores = response.json()
    del indicadores["version"]
    del indicadores["autor"]
    del indicadores["fecha"]

    lista_monedas = []

    for llave in indicadores:
        lista_monedas.append(indicadores[llave])
    
    for i in range(len(lista_monedas)):
        if lista_monedas[i]["unidad_medida"] == "Porcentaje":
            lista_monedas[i]["valor"] = "{:,}".format(lista_monedas[i]["valor"]).replace(".", ",") + "%"
            lista_monedas[i]["unidad_medida"] = ""
        else:
            lista_monedas[i]["valor"] = "{:,}".format(round(lista_monedas[i]["valor"])).replace(",", ".")
        
        if lista_monedas[i]["unidad_medida"] == "Dólar":
            lista_monedas[i]["unidad_medida"] = "Dólares"
    
    response = requests.get('https://api.coincap.io/v2/assets/ethereum')
    response = response.json()
    nvaMoneda = {
        "nombre": response["data"]["name"],
        "valor": "{:,}".format(round(float(response["data"]["priceUsd"]))).replace(",", "."),
        "unidad_medida": "Dólares"
    }

    lista_monedas.append(nvaMoneda)
    aux["indicadores"] = lista_monedas

    noticias_encontradas = []

    if request.method == 'POST':
        busqueda = request.POST['busqueda']
        aux["busqueda"] = busqueda
    
        noticias_encontradas = Noticia.objects.raw("""
            SELECT * 
            FROM core_noticia n INNER JOIN core_categorianoticia c ON c.id = n.id_categoria_id INNER JOIN auth_user u ON u.id = n.id_autor_id 
            WHERE ( 
            POSITION(%s IN n.titulo ) != 0  OR  POSITION(%s IN u.first_name || ' ' || u.last_name) != 0 OR POSITION(%s IN c.descripcion ) != 0
            ) 
            AND n.id_estado_noticia_id = 2 ORDER BY n.fecha DESC
            """
            , [busqueda, busqueda, busqueda])
        
        aux ['busqueda'] = busqueda
        
        if len(noticias_encontradas) == 0:
            aux['mensaje'] = 'No se encontraron resultados para ' + busqueda
            return render(request, 'core/index.html', aux)

        paginator = Paginator(noticias_encontradas, 2)
        page_number = 1
        page_obj = paginator.get_page(page_number)

        aux ['noticias_encontradas'] = page_obj

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
    paginator = Paginator(lista_perfil_periodistas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_perfil_periodistas': page_obj
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

    paginator = Paginator(lista_noticias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'perfil_periodista': perfil_periodista,
        'cantidad_noticias': cantidad_noticias,
        'lista_noticias': page_obj
    }
    
    return render(request, 'core/paginas/comun/periodista.html', aux)


def contacto(request):
    aux = {}

    if request.method == 'POST':
        nombre_completo = request.POST['nombre_completo']
        correo = request.POST['correo']
        asunto = request.POST['asunto']
        mensaje = request.POST.get('mensaje')

        aux['nombre_completo'] = nombre_completo
        aux['correo'] = correo
        aux['asunto'] = asunto
        aux['contenido_mensaje'] = mensaje

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/paginas/comun/contacto.html', aux)

        Mensaje.objects.create(nombre_completo=nombre_completo, correo=correo, asunto=asunto, mensaje=mensaje)
            
        aux['mensaje'] = 'Mensaje enviado con éxito'
        aux['nombre_completo'] = ""
        aux['correo'] = ""
        aux['asunto'] = ""
        aux['contenido_mensaje'] = ""
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
        aux['titulo'] = titulo
        aux['ubicacion'] = ubicacion
        aux['categoriaSeleccionada'] = categoria
        aux['cuerpo'] = cuerpo

        if len(titulo) > 150:
            aux['mensaje'] = 'El título de la noticia excede el máximo (150 caracteres)'
            return render(request, 'core/paginas/periodista/crear_noticia.html', aux)

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/paginas/periodista/crear_noticia.html', aux)
        
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
            aux['titulo'] = ""
            aux['ubicacion'] = ""
            aux['categoriaSeleccionada'] = ""
            aux['cuerpo'] = ""

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

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/paginas/periodista/editar_noticia.html', aux)

        if len(titulo) > 150:
            aux['mensaje'] = 'El título de la noticia excede el máximo (150 caracteres)'
            return render(request, 'core/paginas/periodista/editar_noticia.html', aux)

        if noticia.titulo != titulo:
            existe_noticia = Noticia.objects.filter(titulo=titulo).exists()
            if existe_noticia:
                aux['mensaje'] = 'Ya existe una noticia con ese título'
                return render(request, 'core/paginas/periodista/editar_noticia.html', aux)
        if categoria == "0":
            aux['mensaje'] = 'Debe seleccionar una categoría válida'
            return render(request, 'core/paginas/periodista/editar_noticia.html', aux)
            
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

    paginator = Paginator(list_noticias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_noticias' : page_obj
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
        aux['username'] = username
        aux['nombre'] = nombre
        aux['apellido'] = apellido
        aux['descripcion'] = descripcion
        aux['correo'] = correo

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/paginas/admin/crear_periodista.html',aux)
        
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
            aux['username'] = ""
            aux['nombre'] = ""
            aux['apellido'] = ""
            aux['descripcion'] = ""
            aux['correo'] = ""
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

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/paginas/admin/editar_periodista.html', aux)

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

@login_required
@permission_required('auth.delete_user')
def lista_noticias_en_espera(request):
    list_noticias = Noticia.objects.filter(id_estado_noticia=1)

    paginator = Paginator(list_noticias, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_noticias': page_obj
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
    
    paginator = Paginator(list_periodistas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_periodistas' : page_obj
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
    lista_mensajes = Mensaje.objects.all().order_by('-fecha')

    paginator = Paginator(lista_mensajes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_mensajes' : page_obj
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


# -------------------------------------------- API Rest --------------------------------------------
from rest_framework import viewsets
from .serializers import *
from rest_framework.renderers import JSONRenderer

class MensajeViewset(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all().order_by("-fecha")
    serializer_class = MensajeSerializers
    renderer_classes = [JSONRenderer]

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer]

class PerfilPeriodistaViewset(viewsets.ModelViewSet):
    queryset = PerfilPeriodista.objects.all()
    serializer_class = PerfilPeriodistaSerializers
    renderer_classes = [JSONRenderer]

class CategoriaNoticiaViewset(viewsets.ModelViewSet):
    queryset = CategoriaNoticia.objects.all()
    serializer_class = CategoriaNoticiaSerializers
    renderer_classes = [JSONRenderer]

class EstadoNoticiaViewset(viewsets.ModelViewSet):
    queryset = EstadoNoticia.objects.all()
    serializer_class = EstadoNoticiaSerializers
    renderer_classes = [JSONRenderer]

from rest_framework.parsers import MultiPartParser, FormParser
class NoticiaViewset(viewsets.ModelViewSet):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializers
    renderer_classes = [JSONRenderer]
    parser_classes = (MultiPartParser, FormParser)

class GaleriaImagenesViewset(viewsets.ModelViewSet):
    queryset = GaleriaImagenes.objects.all()
    serializer_class = GaleriaImagenesSerializers
    renderer_classes = [JSONRenderer]

class MensajeRechazoNoticiaViewset(viewsets.ModelViewSet):
    queryset = MensajeRechazoNoticia.objects.all()
    serializer_class = MensajeRechazoNoticiaSerializers
    renderer_classes = [JSONRenderer]

class UserGroupListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserGroupSerializer
    renderer_classes = [JSONRenderer]

class UserGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    lookup_url_kwarg = 'id'
    serializer_class = UserGroupSerializer
    renderer_classes = [JSONRenderer]


@login_required
@permission_required('auth.change_user')
def lista_mensajes_api(request):
    response = requests.get('http://127.0.0.1:8000/api/mensaje/')
    mensajes = response.json()

    paginator = Paginator(mensajes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
    'lista_mensajes': page_obj
    }

    return render(request, 'core/crudapi/admin/lista_mensajes.html', aux)

@login_required
@permission_required('auth.change_user')
def mensaje_api(request, id):
    response = requests.get(f'http://127.0.0.1:8000/api/mensaje/{id}')
    mensaje = response.json()
    aux = {
        "mensaje": mensaje
    }
    return render(request, 'core/crudapi/admin/mensaje.html', aux)

def lista_periodistas_api(request):
    response = requests.get('http://127.0.0.1:8000/api/perfil_periodista/')
    lista_perfil_periodistas = response.json()

    paginator = Paginator(lista_perfil_periodistas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_perfil_periodistas': page_obj
    }
    return render(request, 'core/crudapi/comun/lista_periodistas.html', aux)

def es_noticia_aprobada(noticia):
    return noticia["id_estado_noticia"]["id"] == 2

from datetime import datetime
def ordenar_noticias_recientes(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if  datetime.strptime(arr[j]["fecha"], "%Y-%m-%d").date() < datetime.strptime(arr[j+1]["fecha"], "%Y-%m-%d").date():
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def aplicar_busqueda(noticias, busqueda):
    noticias_a_borrar = []
    for i in range(len(noticias)):
        if noticias[i]["titulo"].find(busqueda) == -1 and noticias[i]["id_categoria"]["descripcion"].find(busqueda) == -1 \
        and (noticias[i]["id_autor"]["first_name"] + ' ' + noticias[i]["id_autor"]["last_name"]).find(busqueda) == -1:
            noticias_a_borrar.append(i)
    noticias_a_borrar.reverse()
    for i in noticias_a_borrar:
        noticias.pop(i)

def index_api(request):
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    noticias = response.json()
    noticias = list(filter(es_noticia_aprobada, noticias))
    ordenar_noticias_recientes(noticias)
    aux = {
        'lista_noticias': noticias[0:5]
    }

    response = requests.get('https://mindicador.cl/api')
    indicadores = response.json()
    del indicadores["version"]
    del indicadores["autor"]
    del indicadores["fecha"]

    lista_monedas = []

    for llave in indicadores:
        lista_monedas.append(indicadores[llave])
    
    for i in range(len(lista_monedas)):
        if lista_monedas[i]["unidad_medida"] == "Porcentaje":
            lista_monedas[i]["valor"] = "{:,}".format(lista_monedas[i]["valor"]).replace(".", ",") + "%"
            lista_monedas[i]["unidad_medida"] = ""
        else:
            lista_monedas[i]["valor"] = "{:,}".format(round(lista_monedas[i]["valor"])).replace(",", ".")
        
        if lista_monedas[i]["unidad_medida"] == "Dólar":
            lista_monedas[i]["unidad_medida"] = "Dólares"
    
    response = requests.get('https://api.coincap.io/v2/assets/ethereum')
    response = response.json()
    nvaMoneda = {
        "nombre": response["data"]["name"],
        "valor": "{:,}".format(round(float(response["data"]["priceUsd"]))).replace(",", "."),
        "unidad_medida": "Dólares"
    }

    lista_monedas.append(nvaMoneda)
    aux["indicadores"] = lista_monedas

    noticias_encontradas = []
    if request.method == 'POST':
        busqueda = request.POST['busqueda']
        aux['busqueda'] = busqueda
        response = requests.get('http://127.0.0.1:8000/api/noticia/')
        noticias_encontradas = response.json()
        noticias_encontradas = list(filter(es_noticia_aprobada, noticias_encontradas))
        aplicar_busqueda(noticias_encontradas, busqueda)
        ordenar_noticias_recientes(noticias_encontradas)
            
        if len(noticias_encontradas) == 0:
            aux['mensaje'] = 'No se encontraron resultados para ' + busqueda
            return render(request, 'core/crudapi/index.html', aux)
        
        paginator = Paginator(noticias_encontradas, 2)
        page_number = 1
        page_obj = paginator.get_page(page_number)
        
        aux ['noticias_encontradas'] = page_obj

    return render(request, 'core/crudapi/index.html', aux)

def noticia_api(request, id):
    response = requests.get(f'http://127.0.0.1:8000/api/noticia/{id}')
    noticia = response.json()
    aux = {
        'noticia': noticia,
    }

    response = requests.get('http://127.0.0.1:8000/api/galeria_imagenes/')
    galeria = response.json()
    galeria = list(filter(lambda imagen_galeria: imagen_galeria["id_noticia"] == int(id), galeria))
    aux ['galeria'] = galeria

    return render(request, 'core/crudapi/comun/noticia.html', aux)

def lista_categorias_api(request):
    response = requests.get('http://127.0.0.1:8000/api/categoria_noticia/')
    lista_categorias = response.json()

    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    lista_noticias = response.json()
    lista_noticias = list(filter(es_noticia_aprobada, lista_noticias))

    noticias = {}
    for categoria in lista_categorias:
        noticias[categoria['descripcion']] = list(filter(lambda noticia: noticia["id_categoria"]["id"] == categoria['id'], lista_noticias))

    aux = {
        "categorias": noticias.items()
    }

    return render(request, 'core/crudapi/comun/lista_categorias.html', aux)

def obtenerPeriodista(lista_periodistas, id):
    for periodista in lista_periodistas:
        if periodista["id_usuario"]["id"] == id:
            return periodista


def periodista_api(request, id):
    response = requests.get('http://127.0.0.1:8000/api/perfil_periodista/')
    perfil_periodista = response.json()
    perfil_periodista = obtenerPeriodista(perfil_periodista, int(id))

    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    lista_noticias = response.json()
    lista_noticias = list(filter(es_noticia_aprobada, lista_noticias))
    lista_noticias = list(filter(lambda noticia: noticia["id_autor"]["id"] == int(id), lista_noticias))

    paginator = Paginator(lista_noticias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    aux = {
        'perfil_periodista': perfil_periodista,
        'cantidad_noticias': len(lista_noticias),
        'lista_noticias': page_obj
    }
    
    return render(request, 'core/crudapi/comun/periodista.html', aux)

def contacto_api(request):
    aux = {}
    
    if request.method == 'POST':
        nombre_completo = request.POST['nombre_completo']
        correo = request.POST['correo']
        asunto = request.POST['asunto']
        mensaje = request.POST.get('mensaje')

        aux['nombre_completo'] = nombre_completo
        aux['correo'] = correo
        aux['asunto'] = asunto
        aux['contenido_mensaje'] = mensaje

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/crudapi/comun/contacto.html', aux)
        
        data = {
            "nombre_completo": nombre_completo,
            "correo": correo,
            "asunto": asunto,
            "mensaje": mensaje,
        }

        r = requests.post('http://127.0.0.1:8000/api/mensaje/', data=data)
            
        aux['mensaje'] = 'Mensaje enviado con éxito'
        aux['nombre_completo'] = ""
        aux['correo'] = ""
        aux['asunto'] = ""
        aux['contenido_mensaje'] = ""
    return render(request, 'core/crudapi/comun/contacto.html', aux)

def obtener_id_noticia(titulo):
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    noticias = response.json()
    for noticia in noticias:
        if(noticia["titulo"] == titulo):
            return noticia["id"]
    return 0

@login_required
@permission_required('core.change_noticia')
def lista_noticias_publicadas_api(request):
    id = request.user.id
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    lista_noticias = response.json()
    lista_noticias = list(filter(lambda noticia: noticia["id_autor"]["id"] == int(id), lista_noticias))

    paginator = Paginator(lista_noticias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_noticias' : page_obj
    }
    aux['mensaje'] = id
    return render(request, 'core/paginas/periodista/lista_noticias_publicadas.html', aux)

@login_required
@permission_required('core.change_noticia')
def noticia_rechazada_api(request, id):
    response = requests.get(f'http://127.0.0.1:8000/api/noticia/{id}')
    noticia = response.json()
    aux = {
        'noticia': noticia
    }

    response = requests.get('http://127.0.0.1:8000/api/galeria_imagenes/')
    galeria = response.json()
    galeria = list(filter(lambda imagen_galeria: imagen_galeria["id_noticia"] == int(id), galeria))
    aux ['galeria'] = galeria

    id_usuario = request.user.id
    if(noticia["id_autor"]["id"] != id_usuario):
        return redirect(to='lista_noticias_publicadas_api')
    
    response = requests.get('http://127.0.0.1:8000/api/mensaje_rechazo_noticia/')
    mensaje_rechazo = response.json()
    mensaje_rechazo = list(filter(lambda rechazo: rechazo["id_noticia"] == int(id), mensaje_rechazo))
    aux ['mensaje_rechazo'] = mensaje_rechazo[0]

    return render(request, 'core/crudapi/periodista/noticia_rechazada.html', aux)

@login_required
@permission_required('auth.delete_user')
def lista_noticias_en_espera_api(request):

    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    lista_noticias = response.json()
    lista_noticias = list(filter(lambda noticia: noticia["id_estado_noticia"]["id"] == 1, lista_noticias))

    paginator = Paginator(lista_noticias, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    aux = {
        'lista_noticias': page_obj
    }
    return render(request, 'core/crudapi/admin/lista_noticias_en_espera.html', aux)

@login_required
@permission_required('auth.change_user')
def lista_periodistas_admin_api(request):    
    response = requests.get('http://127.0.0.1:8000/api/perfil_periodista/')
    list_periodistas = response.json()
    list_periodistas = list(map(lambda perfil: perfil["id_usuario"], list_periodistas))    

    paginator = Paginator(list_periodistas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    aux = {
        'lista_periodistas' : page_obj
    }

    return render(request, 'core/crudapi/admin/lista_periodistas.html', aux)

class NoticiaDetailView(generics.RetrieveUpdateAPIView):
    queryset = Noticia.objects.all()
    lookup_url_kwarg = 'id'
    serializer_class = NoticiaSerializer2

@login_required
@permission_required('auth.change_user')
def noticia_en_espera_api(request, id):
    aux = {}
    response = requests.get(f'http://127.0.0.1:8000/api/noticia/{id}')
    noticia = response.json()
    aux ['noticia'] = noticia

    response = requests.get('http://127.0.0.1:8000/api/galeria_imagenes/')
    galeria = response.json()
    galeria = list(filter(lambda imagen_galeria: imagen_galeria["id_noticia"] == int(id), galeria))
    aux ['galeria'] = galeria

    if request.method == 'POST':
        file_url = noticia["portada"]
        file_response = requests.get(file_url)
        file_path = 'temp_image.jpeg'

        with open(file_path, 'wb') as f:
            f.write(file_response.content)

        files = {'portada': open(file_path, 'rb')}
        del noticia["portada"]

        noticia["id_autor"] = noticia["id_autor"]["id"]
        noticia["id_categoria"] = noticia["id_categoria"]["id"]
        noticia["id_estado_noticia"] = 3

        r1 = requests.put(f'http://127.0.0.1:8000/api/editar_noticia_api/{id}/', data=noticia, files=files)

        mensaje = request.POST.get('mensaje')
        data = {
            "mensaje_rechazo": mensaje,
            "id_noticia": int(id),
        }
        r2 = requests.post('http://127.0.0.1:8000/api/mensaje_rechazo_noticia/', data=data)

        return redirect(to='lista_noticias_en_espera')

    return render(request, 'core/crudapi/admin/noticia_en_espera.html', aux)

@login_required
@permission_required('auth.change_user')
def aceptar_noticia_api(request, id):
    aux = {}
    response = requests.get(f'http://127.0.0.1:8000/api/noticia/{id}')
    noticia = response.json()

    file_url = noticia["portada"]
    file_response = requests.get(file_url)
    file_path = 'temp_image.jpeg'

    with open(file_path, 'wb') as f:
        f.write(file_response.content)

    files = {'portada': open(file_path, 'rb')}
    del noticia["portada"]

    noticia["id_autor"] = noticia["id_autor"]["id"]
    noticia["id_categoria"] = noticia["id_categoria"]["id"]
    noticia["id_estado_noticia"] = 2

    r1 = requests.put(f'http://127.0.0.1:8000/api/editar_noticia_api/{id}/', data=noticia, files=files)

    aux ['mensaje'] = 'Noticia aceptada con éxito'

    return redirect(to='lista_noticias_en_espera')

class NoticiaListView(generics.ListCreateAPIView):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializer2

def es_titulo_repetido(titulo):
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    noticias = response.json()
    for noticia in noticias:
        if(noticia["titulo"] == titulo):
            return True
    return False

@login_required
@permission_required('core.add_noticia')
def crear_noticia_api(request):
    response = requests.get('http://127.0.0.1:8000/api/categoria_noticia/')
    lista_categorias = response.json()

    aux = {
        "categorias": lista_categorias
    }

    if request.method == 'POST':
        titulo = request.POST['titulo']
        ubicacion = request.POST['ubicacion']
        categoria = request.POST['categoria']
        cuerpo = request.POST.get('cuerpo')
        aux['titulo'] = titulo
        aux['ubicacion'] = ubicacion
        aux['categoriaSeleccionada'] = categoria
        aux['cuerpo'] = cuerpo

        if len(titulo) > 150:
            aux['mensaje'] = 'El título de la noticia excede el máximo (150 caracteres)'
            return render(request, 'core/crudapi/periodista/crear_noticia.html', aux)

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/crudapi/periodista/crear_noticia.html', aux)
        
        portada = request.FILES.getlist('portada')[0]
        carrusel = request.FILES.getlist('carrusel')

        if es_titulo_repetido(titulo):
            aux['mensaje'] = 'Ya existe una noticia con ese título'
        elif categoria == "0":
            aux['mensaje'] = 'Debe seleccionar una categoría válida'
        else:
            autor = request.user.id
            estado_noticia = 1

            noticia = {
                "titulo": titulo,
                "ubicacion": ubicacion,
                "cuerpo": cuerpo,
                "id_categoria": int(categoria),
                "id_autor": autor,
                "id_estado_noticia": estado_noticia,
            }

            files = {'portada': (portada.name, portada.read(), portada.content_type)}

            response = requests.post('http://127.0.0.1:8000/api/crear_noticia_api', data=noticia, files=files)
            response = response.json()
            idNvaNoticia = response["id"]
            
            for imagen in carrusel:
                files = {'imagen': (imagen.name, imagen.read(), imagen.content_type)}
                data = {
                    "id_noticia": idNvaNoticia
                }
                response = requests.post('http://127.0.0.1:8000/api/galeria_imagenes/', data=data, files=files)
            
            aux['mensaje'] = 'Noticia creada con éxito'
            aux['titulo'] = ""
            aux['ubicacion'] = ""
            aux['categoriaSeleccionada'] = ""
            aux['cuerpo'] = ""

    return render(request, 'core/crudapi/periodista/crear_noticia.html', aux)


@login_required
@permission_required('core.change_noticia')
def editar_noticia_api(request, id):
    response = requests.get(f'http://127.0.0.1:8000/api/editar_noticia_api/{id}/')
    noticia = response.json()

    id_usuario = request.user.id

    if(noticia["id_autor"] != id_usuario):
        return redirect(to='lista_noticias_publicadas')

    response = requests.get('http://127.0.0.1:8000/api/categoria_noticia/')
    lista_categorias = response.json()

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

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/crudapi/admin/editar_periodista.html', aux)

        if len(titulo) > 150:
            aux['mensaje'] = 'El título de la noticia excede el máximo (150 caracteres)'
            return render(request, 'core/crudapi/admin/editar_periodista.html', aux)

        if noticia["titulo"] != titulo:
            if es_titulo_repetido(titulo):
                aux['mensaje'] = 'Ya existe una noticia con ese título'
                return render(request, 'core/crudapi/admin/editar_periodista.html', aux)
        if categoria == "0":
            aux['mensaje'] = 'Debe seleccionar una categoría válida'
            return render(request, 'core/crudapi/admin/editar_periodista.html', aux)
            
        noticia["titulo"] = titulo
        noticia["ubicacion"] = ubicacion
        noticia["id_categoria"] = int(categoria)
        noticia["cuerpo"] = cuerpo
        noticia["id_estado_noticia"] = 1
        del noticia["portada"]

        files = {'portada': (portada.name, portada.read(), portada.content_type)}

        response = requests.put(f'http://127.0.0.1:8000/api/editar_noticia_api/{id}/', data=noticia, files=files)

        response = requests.get('http://127.0.0.1:8000/api/galeria_imagenes/')
        lista_galeria = response.json()
        lista_galeria = list(filter(lambda imagen: imagen["id_noticia"] == int(id), lista_galeria))

        for imagen in lista_galeria:
            idImagen= imagen["id"]
            response = requests.delete(f'http://127.0.0.1:8000/api/galeria_imagenes/{idImagen}/')
        
        for imagen in carrusel:
            files = {'imagen': (imagen.name, imagen.read(), imagen.content_type)}
            data = {
                "id_noticia": int(id)
            }
            response = requests.post('http://127.0.0.1:8000/api/galeria_imagenes/', data=data, files=files)

        aux['mensaje'] = 'Noticia modificada con éxito'

    return render(request, 'core/crudapi/periodista/editar_noticia.html', aux)

@login_required
@permission_required('core.delete_noticia')
def eliminar_noticia_api(request,id):
    response = requests.get(f'http://127.0.0.1:8000/api/editar_noticia_api/{id}/')
    noticia = response.json()
    id_usuario = request.user.id

    if(noticia["id_autor"] != id_usuario):
        return redirect(to='lista_noticias_publicadas')
    
    response = requests.delete(f'http://127.0.0.1:8000/api/noticia/{id}/')
    return redirect(to='lista_noticias_publicadas')


def es_username_o_email_repetido(username, email):
    response = requests.get('http://127.0.0.1:8000/api/user/')
    usuarios = response.json()
    for usuario in usuarios:
        if(usuario["username"] == username or usuario["email"] == email ):
            return True
    return False

class PerfilPeriodistaListView(generics.ListCreateAPIView):
    queryset = PerfilPeriodista.objects.all()
    serializer_class = PerfilPeriodistaSerializers2

class PerfilPeriodistaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PerfilPeriodista.objects.all()
    lookup_url_kwarg = 'id'
    serializer_class = PerfilPeriodistaSerializers2


@login_required
@permission_required('auth.change_user')
def crear_periodista_api(request):
    aux = {}

    if request.method == 'POST':
        username = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        descripcion = request.POST['descripcion']
        correo = request.POST['email']
        aux['username'] = username
        aux['nombre'] = nombre
        aux['apellido'] = apellido
        aux['descripcion'] = descripcion
        aux['correo'] = correo

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/crudapi/admin/crear_periodista.html',aux)
        
        contrasenia = make_password(request.POST['contrasenia'])
        foto_perfil = request.FILES['foto_perfil']

        if not(es_username_o_email_repetido(username, correo)) :
            data = {
                "username": username,
                "first_name": nombre,
                "last_name": apellido,
                "email": correo,
                "password": contrasenia,
            }

            response = requests.post('http://127.0.0.1:8000/api/user/', data=data)
            response = response.json()
            idNvoUsuario = response["id"]

            data = {
                "username": username,
                "groups": [2]
            }

            response = requests.put(f'http://127.0.0.1:8000/api/usuario_grupos/{idNvoUsuario}/', data=data)

            data = {
                "id_usuario": idNvoUsuario,
                "descripcion": descripcion
            }

            files = {'foto_perfil': (foto_perfil.name, foto_perfil.read(), foto_perfil.content_type)}

            response = requests.post('http://127.0.0.1:8000/api/crear_perfil_periodista_api', data=data, files=files)
            
            aux['mensaje'] = 'Periodista creado con éxito'
            aux['username'] = ""
            aux['nombre'] = ""
            aux['apellido'] = ""
            aux['descripcion'] = ""
            aux['correo'] = ""
        else:
            aux['mensaje'] = 'Ya existe un usuario con ese correo'

    return render(request, 'core/crudapi/admin/crear_periodista.html',aux)

def obtener_perfil_periodista(id_periodista):
    response = requests.get('http://127.0.0.1:8000/api/perfil_periodista/')
    perfiles = response.json()
    for perfil in perfiles:
        if(perfil["id_usuario"]["id"] == int(id_periodista)):
            return perfil
    return 0


@login_required
@permission_required('auth.change_user')
def editar_periodista_api(request, id):
    response = requests.get(f'http://127.0.0.1:8000/api/user/{id}')
    periodista = response.json()

    perfil_periodista = obtener_perfil_periodista(id)

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

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not(result['success']):
            aux['mensaje'] = "Error en el reCAPTCHA"
            return render(request, 'core/crudapi/admin/editar_periodista.html', aux)      

        if periodista['email'] != correo or periodista['username'] != username:
            if es_username_o_email_repetido(username, correo):
                aux['mensaje'] = 'Ya existe un usuario con ese correo'
                return render(request, 'core/crudapi/admin/editar_periodista.html', aux)
            
        data = {
            "username": username,
            "first_name": nombre,
            "last_name": apellido,
            "email": correo,
            "password": contrasenia,
        }

        response = requests.put(f'http://127.0.0.1:8000/api/user/{id}/', data=data)

        id_perfil_periodista = perfil_periodista["id"]

        data = {
            "id_usuario": periodista["id"],
            "descripcion": descripcion
        }

        files = {'foto_perfil': (foto_perfil.name, foto_perfil.read(), foto_perfil.content_type)}

        response = requests.put(f'http://127.0.0.1:8000/api/crear_perfil_periodista_api/{id_perfil_periodista}/', data=data, files=files)

        aux['mensaje'] = 'Periodista modificado con éxito'

    return render(request, 'core/crudapi/admin/editar_periodista.html', aux)

@login_required
@permission_required('auth.delete_user')
def eliminar_periodista_api(request, id):
    response = requests.delete(f'http://127.0.0.1:8000/api/user/{id}')
    return redirect(to='lista_periodistas_admin')

def busqueda_api(request, page, busqueda):
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    noticias = response.json()
    noticias = list(filter(es_noticia_aprobada, noticias))
    ordenar_noticias_recientes(noticias)
    aux = {
        'lista_noticias': noticias[0:5]
    }

    noticias_encontradas = []
    if request.method == 'POST':
        busqueda = request.POST['busqueda']
    
    aux['busqueda'] = busqueda
    response = requests.get('http://127.0.0.1:8000/api/noticia/')
    noticias_encontradas = response.json()
    noticias_encontradas = list(filter(es_noticia_aprobada, noticias_encontradas))
    aplicar_busqueda(noticias_encontradas, busqueda)
    ordenar_noticias_recientes(noticias_encontradas)
            
    if len(noticias_encontradas) == 0:
        aux['mensaje'] = 'No se encontraron resultados para ' + busqueda
        return render(request, 'core/crudapi/index.html', aux)
        
    paginator = Paginator(noticias_encontradas, 2)
    page_number = page
    if request.method == 'POST':
        page_number = 1
    page_obj = paginator.get_page(page_number)
        
    aux ['noticias_encontradas'] = page_obj

    return render(request, 'core/crudapi/index.html', aux)