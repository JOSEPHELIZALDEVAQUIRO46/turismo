from django import forms

class PostSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en el blog...',
        })
    )
    
from .models import ComentarioBlog

class ComentarioBlogForm(forms.ModelForm):
    class Meta:
        model = ComentarioBlog
        fields = ['nombre', 'email', 'contenido']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tu comentario', 'rows': 4}),
        }