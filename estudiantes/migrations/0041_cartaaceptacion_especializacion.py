# Generated by Django 5.0.6 on 2024-09-05 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0040_perfil_reporte_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartaaceptacion',
            name='especializacion',
            field=models.CharField(default='Especializacion', max_length=50),
        ),
    ]