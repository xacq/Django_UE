# Generated by Django 5.0.6 on 2024-09-06 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0043_remove_informediario_fecha_semanal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='habilitado',
            field=models.BooleanField(default=True),
        ),
    ]
