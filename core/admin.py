from django.contrib import admin

from .models import *

admin.site.register(TipoUsuario)
admin.site.register(Usuario)
admin.site.register(PerfilPeriodista)
admin.site.register(CategoriaNoticia)
admin.site.register(EstadoNoticia)
admin.site.register(Noticia)
admin.site.register(GaleriaImagenes)
admin.site.register(MensajeRechazoNoticia)
admin.site.register(Mensaje)

