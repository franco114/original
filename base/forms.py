from django import forms 
from django.contrib.auth.forms import AuthenticationForm
from .models import Tarea

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Nombre de usuario o contraseña incorrecta",
        "inactive": "Esta cuenta está inactiva",
    }



class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['completo', 'medicion_completa', 'fecha_medicion', 'integrantes', 'justificacion',"medicion_gamma","fecha_medicion_gamma"]
        widgets = {
            'integrantes': forms.TextInput(attrs={'class': 'short-input'}),
            'justificacion': forms.TextInput(attrs={'class': 'short-input2'}),
            'fecha_medicion': forms.DateInput(attrs={'readonly': 'readonly'}),
        }
