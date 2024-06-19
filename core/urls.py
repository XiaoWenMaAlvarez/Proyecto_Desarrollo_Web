from django.urls import path, include

from .views import *

from rest_framework import routers
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register('mensaje', MensajeViewset)
router.register('user', UserViewset)
router.register('perfil_periodista', PerfilPeriodistaViewset)
router.register('categoria_noticia', CategoriaNoticiaViewset)
router.register('estado_noticia', EstadoNoticiaViewset)
router.register('noticia', NoticiaViewset)
router.register('galeria_imagenes', GaleriaImagenesViewset)
router.register('mensaje_rechazo_noticia', MensajeRechazoNoticiaViewset)
router.register('donacion', DonacionViewSet)


urlpatterns = [
  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
  path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

  path('register', register, name='register'),
  path('account_locked', account_locked, name='account_locked'),

  # Lector
  path('', index, name='index'),
  path('busqueda/<int:page>/<str:busqueda>', busqueda, name='busqueda'),
  path('lista_categorias', lista_categorias, name='lista_categorias'),
  path('lista_periodistas', lista_periodistas, name='lista_periodistas'),
  path('noticia/<id>/', noticia, name='noticia'),
  path('periodista/<id>/', periodista, name='periodista'),
  path('contacto', contacto, name='contacto'),
  path('donaciones', donaciones, name='donaciones'),
  path('agradecimiento', agradecimiento, name='agradecimiento'),
  path('lista_donaciones', lista_donaciones, name='lista_donaciones'),
  path('donacion_detalle/<id>/', donacion_detalle, name='donacion_detalle'),
  path('descargar_donacion/<id>/', descargar_donacion, name='descargar_donacion'),

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

  # APIs
  path('api/', include(router.urls)),
  path('api/editar_noticia_api/<int:id>/', NoticiaDetailView.as_view()),
  path('api/crear_noticia_api', NoticiaListView.as_view()),
  path('api/crear_perfil_periodista_api', PerfilPeriodistaListView.as_view()),
  path('api/crear_perfil_periodista_api/<id>/', PerfilPeriodistaDetailView.as_view()),
  path('api/usuario_grupos', UserGroupListView.as_view()),
  path('api/usuario_grupos/<id>/', UserGroupDetailView.as_view()),

  # Lector APIs
  path('index_api', index_api, name='index_api'),
  path('busqueda_api/<int:page>/<str:busqueda>', busqueda_api, name='busqueda_api'),
  path('lista_categorias_api', lista_categorias_api, name='lista_categorias_api'),
  path('lista_periodistas_api', lista_periodistas_api, name='lista_periodistas_api'),
  path('noticia_api/<id>/', noticia_api, name='noticia_api'),
  path('periodista_api/<id>/', periodista_api, name='periodista_api'),
  path('contacto_api', contacto_api, name='contacto_api'),

  # Periodista APIs
  path('crear_noticia_api', crear_noticia_api, name='crear_noticia_api'),
  path('editar_noticia_api/<id>/', editar_noticia_api, name='editar_noticia_api'),
  path('eliminar_noticia_api/<id>/', eliminar_noticia_api, name='eliminar_noticia_api'),
  path('lista_noticias_publicadas_api', lista_noticias_publicadas_api, name='lista_noticias_publicadas_api'),
  path('noticia_rechazada_api/<id>/', noticia_rechazada_api, name='noticia_rechazada_api'),

  # Administrador APIs
  path('lista_noticias_en_espera_api', lista_noticias_en_espera_api, name='lista_noticias_en_espera_api'),
  path('lista_periodistas_admin_api', lista_periodistas_admin_api, name='lista_periodistas_admin_api'),
  path('noticia_en_espera_api/<id>/', noticia_en_espera_api, name='noticia_en_espera_api'),
  path('crear_periodista_api', crear_periodista_api, name='crear_periodista_api'),
  path('editar_periodista_api/<id>/', editar_periodista_api, name='editar_periodista_api'),
  path('eliminar_periodista_api/<id>/', eliminar_periodista_api, name='eliminar_periodista_api'),
  path('lista_mensajes_api', lista_mensajes_api, name="lista_mensajes_api"),
  path('mensaje_api/<id>/', mensaje_api, name='mensaje_api'),
  path('aceptar_noticia_api/<id>/', aceptar_noticia_api, name='aceptar_noticia_api'),
]
