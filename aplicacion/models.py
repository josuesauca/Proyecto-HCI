from django.db import models
from django.contrib.auth.models import User

class Imagen(models.Model):
    idImagen = models.AutoField(primary_key=True)
    imagenTraduccion = models.ImageField(null=True)
    def __str__(self):
        return f"{self.imagenTraduccion}"

# Create your models here.
class Traduccion(models.Model):
    idTraduccion = models.AutoField(primary_key=True)
    idUsuario = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    idImagen = models.ForeignKey(Imagen,null=True,on_delete=models.CASCADE)
    horaTraduccion = models.DecimalField(max_digits= 6,decimal_places=2,null=True) 
    textoTraduccion = models.CharField(max_length=500,null=True) 
    idiomaImagen = models.CharField(max_length=10,null=True) 

    """
    def __str__(self):
        return f"Tarjeta : {self.idTarjeta}  , {self.numTarjeta} , {self.saldoTarjeta} "
    """

class TraduccionObtenido(models.Model):
    idTraduccion = models.ForeignKey(Traduccion,null=True,on_delete=models.CASCADE)
    idTraduccionObtenida = models.AutoField(primary_key=True)
    nombreTraduccionObtenida = models.CharField(max_length=50,null=True) 
    textoTraducido = models.CharField(max_length=500,null=True) 
    idiomaTraduccion = models.CharField(max_length=500,null=True) 

    calificacion = (
        (1, "Una Estrella"),
        (2, "Dos Estrellas"),
        (3, "Tres Estrellas"),
        (4, "Cuatro Estrellas"),
        (5, "Cinco Estrellas")
    )
    calificacionTraduccion = models.IntegerField(null=True)

