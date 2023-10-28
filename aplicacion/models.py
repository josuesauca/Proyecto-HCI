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
    horaTraduccion = models.DateTimeField(null=True)
    textoTraduccion = models.CharField(max_length=500,null=True) 
    idiomaImagen = models.CharField(max_length=10,null=True) 
   
    def __str__(self):
        return f"Traduccion : {self.idTraduccion}"

class TraduccionObtenido(models.Model):
    idTraduccionObtenida = models.AutoField(primary_key=True)
    idTraduccion = models.ForeignKey(Traduccion,null=True,on_delete=models.CASCADE)
    nombreTraduccionObtenida = models.CharField(max_length=50,null=True) 
    textoTraducido = models.CharField(max_length=500,null=True) 
    idiomaTraduccion = models.CharField(max_length=500,null=True) 

    def __str__(self):
        return f"Traduccion Obtenida: {self.idTraduccion}"

