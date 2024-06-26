from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


"""
class TipoUsuario(models.Model):
    descripcion = models.CharField(max_length=30)

    def __str__(self):
        return self.descripcion
"""

""" class Usuario(models.Model):
    nombre_completo = models.CharField(max_length=60)
    correo = models.EmailField(max_length=60, unique=True)
    contrasenia = models.CharField(max_length=30)
    id_tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.RESTRICT)

    def __str__(self):
        return self.nombre_completo
"""

class PerfilPeriodista(models.Model):
    descripcion = models.CharField(max_length=100)
    foto_perfil = CloudinaryField('image')
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion


class CategoriaNoticia(models.Model):
    descripcion = models.CharField(max_length=30)

    def __str__(self):
        return self.descripcion


class EstadoNoticia(models.Model):
    descripcion = models.CharField(max_length=30)

    def __str__(self):
        return self.descripcion


class Noticia(models.Model):
    titulo = models.CharField(max_length=150, unique=True)
    ubicacion = models.CharField(max_length=50)
    fecha = models.DateField(auto_now=True)
    portada = CloudinaryField('image')
    cuerpo = models.TextField()

    id_autor = models.ForeignKey(User, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(CategoriaNoticia, on_delete=models.RESTRICT)
    id_estado_noticia = models.ForeignKey(EstadoNoticia, on_delete=models.RESTRICT)

    def __str__(self):
        return self.titulo
    
class Mensaje(models.Model):
    nombre_completo = models.CharField(max_length=60)
    correo = models.EmailField(max_length=60)
    asunto = models.CharField(max_length=50)
    fecha = models.DateField(auto_now=True)
    mensaje = models.TextField()

    def __str__(self):
        return self.asunto


class GaleriaImagenes(models.Model):
    imagen = CloudinaryField('image')
    id_noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)

    def __str__(self):
        return self.id_noticia.titulo


class MensajeRechazoNoticia(models.Model):
    mensaje_rechazo = models.CharField(max_length=200)
    id_noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)

    def __str__(self):
        return self.mensaje_rechazo

class Donacion(models.Model):
    monto = models.CharField(max_length=20)
    moneda = models.CharField(max_length=20)
    id_pago = models.CharField(max_length=100)

    fecha = models.DateField(auto_now=True)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion