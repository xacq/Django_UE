# Generated by Django 5.0.6 on 2024-08-06 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0011_alter_cartaaceptacion_fecha_subida_carta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('profesion', models.CharField(max_length=100)),
                ('experiencia', models.CharField(max_length=255)),
            ],
        ),
    ]
