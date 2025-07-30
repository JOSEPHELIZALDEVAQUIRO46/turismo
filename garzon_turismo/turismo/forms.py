# turismo/forms.py - Agregar estos formularios a los existentes

from django import forms
from core.models import Comentario, Valoracion
from .models import (
    Establecimiento, Transporte, Artesania, ActividadFisica
)

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

# ========== FORMULARIOS PARA LOS NUEVOS MODELOS ==========

class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = [
            'nombre', 'tipo', 'descripcion', 'origen', 'destino',
            'duracion_estimada', 'costo_aproximado', 'contacto', 
            'telefono', 'horarios', 'recomendaciones', 'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion_estimada': forms.TextInput(attrs={'class': 'form-control'}),
            'costo_aproximado': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'horarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class TransporteFiltroForm(forms.Form):
    TIPO_CHOICES = [('', 'Todos los tipos')] + list(Transporte.TIPO_TRANSPORTE_CHOICES)
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    origen = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por origen'
        })
    )
    destino = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por destino'
        })
    )

class ArtesaniaForm(forms.ModelForm):
    class Meta:
        model = Artesania
        fields = [
            'nombre', 'categoria', 'descripcion', 'artesano', 'lugar_origen',
            'tecnica_elaboracion', 'materiales', 'precio_referencia',
            'tiempo_elaboracion', 'imagen_principal', 'contacto_artesano', 'historia'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'artesano': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'tecnica_elaboracion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'materiales': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Separar materiales con comas'
            }),
            'precio_referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'tiempo_elaboracion': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'contacto_artesano': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ArtesaniaFiltroForm(forms.Form):
    CATEGORIA_CHOICES = [('', 'Todas las categorías')] + list(Artesania.CATEGORIA_CHOICES)
    
    categoria = forms.ChoiceField(
        choices=CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lugar_origen = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lugar de origen'
        })
    )

class ActividadFisicaForm(forms.ModelForm):
    class Meta:
        model = ActividadFisica
        fields = [
            'nombre', 'tipo_actividad', 'descripcion', 'ubicacion', 'dificultad',
            'duracion', 'costo', 'edad_minima', 'capacidad_maxima',
            'equipamiento_incluido', 'equipamiento_requerido', 'recomendaciones_salud',
            'mejor_epoca', 'horarios_disponibles', 'instructor_guia', 'contacto',
            'telefono', 'email', 'imagen_principal', 'latitud', 'longitud'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_actividad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'dificultad': forms.Select(attrs={'class': 'form-control'}),
            'duracion': forms.TextInput(attrs={'class': 'form-control'}),
            'costo': forms.TextInput(attrs={'class': 'form-control'}),
            'edad_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'capacidad_maxima': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'equipamiento_incluido': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Separar equipamiento con comas'
            }),
            'equipamiento_requerido': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Separar equipamiento con comas'
            }),
            'recomendaciones_salud': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mejor_epoca': forms.TextInput(attrs={'class': 'form-control'}),
            'horarios_disponibles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructor_guia': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: 2.2446'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Ej: -75.5905'
            }),
        }

class ActividadFisicaFiltroForm(forms.Form):
    TIPO_CHOICES = [('', 'Todos los tipos')] + list(ActividadFisica.TIPO_ACTIVIDAD_CHOICES)
    DIFICULTAD_CHOICES = [('', 'Todas las dificultades')] + list(ActividadFisica.DIFICULTAD_CHOICES)
    
    tipo_actividad = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dificultad = forms.ChoiceField(
        choices=DIFICULTAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    edad_minima = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Edad mínima',
            'min': 0
        })
    )