# Generated by Django 5.0.6 on 2024-08-06 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0010_rename_ano_lectivo_cartaaceptacion_ano_lectivo_carta_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartaaceptacion',
            name='fecha_subida_carta',
            field=models.DateField(auto_now_add=True),
        ),
    ]
