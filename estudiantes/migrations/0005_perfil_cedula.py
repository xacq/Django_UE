# Generated by Django 5.0.6 on 2024-08-02 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0004_perfil'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='cedula',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]