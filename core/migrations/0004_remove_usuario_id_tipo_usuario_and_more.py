# Generated by Django 5.0.4 on 2024-05-10 13:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_mensaje_alter_noticia_titulo_alter_usuario_correo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='id_tipo_usuario',
        ),
        migrations.AlterField(
            model_name='noticia',
            name='id_autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='perfilperiodista',
            name='id_usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='perfilperiodista',
            name='descripcion',
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name='TipoUsuario',
        ),
        migrations.DeleteModel(
            name='Usuario',
        ),
    ]
