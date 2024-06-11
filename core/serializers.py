from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group

class MensajeSerializers(serializers.ModelSerializer):
  class Meta:
    model = Mensaje
    fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username','first_name','last_name','email','password')
    extra_kwargs = {'password':{'write_only':True}} 


class PerfilPeriodistaSerializers(serializers.ModelSerializer):
  id_usuario = UserSerializer()
  class Meta:
    model = PerfilPeriodista
    fields = '__all__'

class PerfilPeriodistaSerializers2(serializers.ModelSerializer):
  class Meta:
    model = PerfilPeriodista
    fields = '__all__'


class CategoriaNoticiaSerializers(serializers.ModelSerializer):
  class Meta:
    model = CategoriaNoticia
    fields = '__all__'


class EstadoNoticiaSerializers(serializers.ModelSerializer):
  class Meta:
    model = EstadoNoticia
    fields = '__all__'


class NoticiaSerializers(serializers.ModelSerializer):
  id_autor = UserSerializer(read_only=True)
  id_categoria = CategoriaNoticiaSerializers(read_only=True)
  id_estado_noticia = EstadoNoticiaSerializers(read_only=True)
  class Meta:
    model = Noticia
    fields = '__all__'

class GaleriaImagenesSerializers(serializers.ModelSerializer):
  class Meta:
    model = GaleriaImagenes
    fields = '__all__'

class MensajeRechazoNoticiaSerializers(serializers.ModelSerializer):
  class Meta:
    model = MensajeRechazoNoticia
    fields = '__all__'

class NoticiaSerializer2(serializers.ModelSerializer):
  class Meta:
    model = Noticia
    fields = '__all__'

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'groups']