from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Traduccion,TraduccionObtenido, Imagen


class FormularioTraduccion(forms.ModelForm):
    class Meta:
        model = Traduccion
        fields = "__all__"

class FormularioTraduccionObtenida(forms.ModelForm):
    class Meta:
        model = TraduccionObtenido
        fields = "__all__"

class FormularioUsuario(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super(FormularioUsuario, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

class FormularioImagen(forms.ModelForm):
    class Meta:
        model = Imagen
        fields = ['imagenTraduccion']
