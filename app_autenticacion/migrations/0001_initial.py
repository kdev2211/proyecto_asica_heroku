# Generated by Django 5.0.3 on 2024-09-17 17:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_tickets', '0003_email_notificacion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Perfil_Usuario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_completo', models.CharField(max_length=40, null=True)),
                ('nombre_puesto', models.CharField(max_length=40, null=True)),
                ('telefono_usuario', models.CharField(max_length=20, null=True)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_tickets.departamento')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]