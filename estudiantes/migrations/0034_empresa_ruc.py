# Generated by Django 5.0.6 on 2024-09-04 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0033_perfil_apellidos_perfil_cedula_perfil_nombres'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='ruc',
            field=models.CharField(default='', max_length=13),
        ),
    ]
