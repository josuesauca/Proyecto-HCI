# Generated by Django 4.2.6 on 2023-10-18 05:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Traduccion',
            fields=[
                ('idTraduccion', models.AutoField(primary_key=True, serialize=False)),
                ('imagenTraduccion', models.ImageField(null=True, upload_to='imagenes/')),
                ('horaTraduccion', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('textoTraduccion', models.CharField(max_length=500, null=True)),
                ('idioma', models.CharField(max_length=10, null=True)),
                ('idUsuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TraduccionObtenido',
            fields=[
                ('idTraduccionObtenida', models.AutoField(primary_key=True, serialize=False)),
                ('nombreTraduccionObtenida', models.CharField(max_length=50, null=True)),
                ('textoTraducido', models.CharField(max_length=500, null=True)),
                ('calificacionTraduccion', models.IntegerField(null=True)),
                ('idTraduccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='aplicacion.traduccion')),
            ],
        ),
    ]