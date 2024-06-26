# Generated by Django 5.0.4 on 2024-06-19 16:00

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_donacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galeriaimagenes',
            name='imagen',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='noticia',
            name='portada',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='perfilperiodista',
            name='foto_perfil',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
