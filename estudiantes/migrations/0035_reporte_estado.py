# Generated by Django 5.0.6 on 2024-09-04 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0034_empresa_ruc'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporte',
            name='estado',
            field=models.CharField(default='Espera', max_length=10),
        ),
    ]
