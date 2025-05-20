# turismo/forms.py

from django import forms
from core.models import Comentario, Valoracion
from .models import Establecimiento

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['nombre', 'email', 'contenido']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tu comentario', 'rows': 4}),
        }

class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Valoracion
        fields = ['nombre', 'email', 'puntuacion', 'comentario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'puntuacion': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tu opinión', 'rows': 4}),
        }

class FiltroEstablecimientoForm(forms.Form):
    TIPO_CHOICES = [('', 'Todos los tipos')] + list(Establecimiento.TIPO_CHOICES)
    RANGO_PRECIOS_CHOICES = [('', 'Todos los precios')] + list(Establecimiento.RANGO_PRECIOS_CHOICES)
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    rango_precios = forms.ChoiceField(
        choices=RANGO_PRECIOS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    servicios = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Servicios (ej: wifi, piscina)'
        })
    )

class FiltroEventoForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'Desde',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'Hasta',
            'type': 'date'
        })
    )