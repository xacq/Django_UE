# Generated by Django 5.0.6 on 2024-07-24 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0002_rol'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_formato', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('prioridad', models.CharField(max_length=50)),
                ('archivo_formato', models.CharField(max_length=255)),
            ],
        ),
    ]
