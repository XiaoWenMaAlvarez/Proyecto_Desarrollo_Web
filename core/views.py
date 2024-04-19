from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def login(request):
    return render(request, 'core/paginas/comun/login.html')


def register(request):
    return render(request, 'core/paginas/comun/registro.html')


def lista_categorias(request):
    return render(request, 'core/paginas/comun/lista_categorias.html')


def lista_periodistas(request):
    return render(request, 'core/paginas/comun/lista_periodistas.html')


def noticia(request):
    return render(request, 'core/paginas/comun/noticia.html')


def periodista(request):
    return render(request, 'core/paginas/comun/periodista.html')


def contacto(request):
    return render(request, 'core/paginas/comun/contacto.html')


def crear_noticia(request):
    return render(request, 'core/paginas/periodista/crear_noticia.html')


def editar_noticia(request):
    return render(request, 'core/paginas/periodista/editar_noticia.html')


def lista_noticias_publicadas(request):
    return render(request, 'core/paginas/periodista/lista_noticias_publicadas.html')


def noticia_rechazada(request):
    return render(request, 'core/paginas/periodista/noticia_rechazada.html')


def crear_periodista(request):
    return render(request, 'core/paginas/admin/crear_periodista.html')


def editar_periodista(request):
    return render(request, 'core/paginas/admin/editar_periodista.html')


def lista_noticias_en_espera(request):
    return render(request, 'core/paginas/admin/lista_noticias_en_espera.html')


def lista_periodistas_admin(request):
    return render(request, 'core/paginas/admin/lista_periodistas.html')


def noticia_en_espera(request):
    return render(request, 'core/paginas/admin/noticia_en_espera.html')

