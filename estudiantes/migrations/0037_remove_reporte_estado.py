# Generated by Django 5.0.6 on 2024-09-04 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0036_perfil_reporte_estado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reporte',
            name='estado',
        ),
    ]
