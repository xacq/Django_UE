# Generated by Django 5.0.6 on 2024-09-07 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0050_remove_reporte_empresa_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporte',
            name='rector',
            field=models.CharField(default='rector', max_length=100),
        ),
    ]
