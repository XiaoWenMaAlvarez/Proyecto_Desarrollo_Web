from django.contrib import admin
from .models import *

from django.contrib.admin import ModelAdmin
from admin_confirm import AdminConfirmMixin

class NoticiaAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['titulo','ubicacion','fecha','portada','id_estado_noticia','cuerpo','id_autor','id_categoria']

class PerfilPeriodistaAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['descripcion','foto_perfil','id_usuario']

class CategoriaNoticiaAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['descripcion']

class EstadoNoticiaAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['descripcion']

class GaleriaImagenesAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['imagen', 'id_noticia']

class MensajeRechazoNoticiaAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['mensaje_rechazo', 'id_noticia']

class MensajeAdmin(AdminConfirmMixin,ModelAdmin):
  confirm_change = True
  confirmation_fields = ['nombre_completo','correo','fecha','asunto','mensaje']

admin.site.register(PerfilPeriodista, PerfilPeriodistaAdmin)
admin.site.register(CategoriaNoticia, CategoriaNoticiaAdmin)
admin.site.register(EstadoNoticia, EstadoNoticiaAdmin)
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(GaleriaImagenes, GaleriaImagenesAdmin)
admin.site.register(MensajeRechazoNoticia, MensajeRechazoNoticiaAdmin)
admin.site.register(Mensaje, MensajeAdmin)
