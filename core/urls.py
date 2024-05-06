from django.urls import path

from .views import *

# Sin slash
urlpatterns = [
  path('', index, name='index'),
  path('register', register, name='register'),
  path('lista_categorias', lista_categorias, name='lista_categorias'),
  path('lista_periodistas', lista_periodistas, name='lista_periodistas'),
  path('noticia/<id>/', noticia, name='noticia'),
  path('periodista/<id>/', periodista, name='periodista'),
  path('contacto', contacto, name='contacto'),

  # Periodista
  path('crear_noticia', crear_noticia, name='crear_noticia'),
  path('editar_noticia/<id>/', editar_noticia, name='editar_noticia'),
  path('eliminar_noticia/<id>/', eliminar_noticia, name='eliminar_noticia'),
  path('lista_noticias_publicadas', lista_noticias_publicadas, name='lista_noticias_publicadas'),
  path('noticia_rechazada/<id>/', noticia_rechazada, name='noticia_rechazada'),

  # Administrador
  path('crear_periodista', crear_periodista, name='crear_periodista'),
  path('editar_periodista/<id>/', editar_periodista, name='editar_periodista'),
  path('eliminar_periodista/<id>/', eliminar_periodista, name='eliminar_periodista'),


  path('lista_noticias_en_espera', lista_noticias_en_espera, name='lista_noticias_en_espera'),
  path('lista_periodistas_admin', lista_periodistas_admin, name='lista_periodistas_admin'),
  path('noticia_en_espera/<id>/', noticia_en_espera, name='noticia_en_espera'),

  path('aceptar_noticia/<id>/', aceptar_noticia, name='aceptar_noticia'),

  path('lista_mensajes', lista_mensajes, name='lista_mensajes'),
  path('mensaje/<id>/', mensaje, name='mensaje'),
]
