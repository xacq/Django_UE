# Generated by Django 5.0.6 on 2024-08-02 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0006_remove_perfil_cedula'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='estado_ingreso',
            field=models.CharField(default='Espera', max_length=20),
        ),
    ]
