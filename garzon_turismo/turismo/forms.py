# turismo/forms.py

from django import forms
from core.models import Comentario, Valoracion
from .models import (
    Establecimiento, Transporte, Artesania, ActividadFisica, 
    CategoriaArtesania, CategoriaActividadFisica, Ruta, PuntoRuta
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
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Búsqueda general'
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar categorías dinámicamente desde la base de datos
        categoria_choices = [('', 'Todas las categorías')]
        categoria_choices.extend([(cat.pk, cat.nombre) for cat in CategoriaArtesania.objects.all()])
        self.fields['categoria'].choices = categoria_choices
    
    categoria = forms.ChoiceField(
        choices=[],  # Se cargan dinámicamente en __init__
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
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Búsqueda general'
        })
    )

class ActividadFisicaForm(forms.ModelForm):
    class Meta:
        model = ActividadFisica
        fields = [
            'nombre', 'categoria', 'descripcion', 'ubicacion', 'dificultad',
            'duracion', 'costo', 'edad_minima', 'capacidad_maxima',
            'equipamiento_incluido', 'equipamiento_requerido', 'recomendaciones_salud',
            'mejor_epoca', 'horarios_disponibles', 'instructor_guia', 'contacto',
            'telefono', 'email', 'imagen_principal', 'latitud', 'longitud',
            'nivel_riesgo', 'requiere_reserva', 'disponible_todo_año'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
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
            'nivel_riesgo': forms.Select(attrs={'class': 'form-control'}),
            'requiere_reserva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponible_todo_año': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ActividadFisicaFiltroForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar categorías dinámicamente desde la base de datos
        categoria_choices = [('', 'Todas las categorías')]
        categoria_choices.extend([(cat.pk, cat.nombre) for cat in CategoriaActividadFisica.objects.all()])
        self.fields['categoria'].choices = categoria_choices
    
    categoria = forms.ChoiceField(
        choices=[],  # Se cargan dinámicamente en __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dificultad = forms.ChoiceField(
        choices=[('', 'Todas las dificultades')] + list(ActividadFisica.DIFICULTAD_CHOICES),
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
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Búsqueda general'
        })
    )

# ========== FORMULARIOS PARA ADMINISTRACIÓN DE MAPAS ==========

class RutaMapaConfigForm(forms.ModelForm):
    """Formulario para configurar el mapa de una ruta"""
    class Meta:
        model = Ruta
        fields = ['mapa_configuracion']
        widgets = {
            'mapa_configuracion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Configuración JSON del mapa'
            })
        }

class PuntoRutaForm(forms.ModelForm):
    """Formulario para crear/editar puntos de ruta"""
    class Meta:
        model = PuntoRuta
        fields = [
            'lugar_turistico', 'nombre', 'descripcion', 'orden',
            'latitud', 'longitud', 'tiempo_estancia', 
            'icono_personalizado', 'color_marcador', 'mostrar_en_mapa'
        ]
        widgets = {
            'lugar_turistico': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
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
            'tiempo_estancia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 30 min, 2 horas'
            }),
            'icono_personalizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del icono'
            }),
            'color_marcador': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'mostrar_en_mapa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== FORMULARIOS PARA CATEGORÍAS DINÁMICAS ==========

class CategoriaArtesaniaForm(forms.ModelForm):
    """Formulario para crear categorías de artesanías"""
    class Meta:
        model = CategoriaArtesania
        fields = ['nombre', 'descripcion', 'icono', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: fas fa-pottery'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class CategoriaActividadFisicaForm(forms.ModelForm):
    """Formulario para crear categorías de actividades físicas"""
    class Meta:
        model = CategoriaActividadFisica
        fields = ['nombre', 'descripcion', 'icono', 'color_tema', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: fas fa-hiking'
            }),
            'color_tema': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

# ========== FORMULARIOS DE BÚSQUEDA AVANZADA ==========

class BusquedaAvanzadaForm(forms.Form):
    """Formulario para búsqueda avanzada en todo el sitio"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en todo el sitio...'
        })
    )
    
    # Filtros por tipo de contenido
    incluir_lugares = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_establecimientos = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_rutas = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_eventos = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_transportes = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_artesanias = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    incluir_actividades = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Filtros adicionales
    solo_destacados = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    orden = forms.ChoiceField(
        choices=[
            ('relevancia', 'Relevancia'),
            ('nombre', 'Nombre A-Z'),
            ('nombre_desc', 'Nombre Z-A'),
            ('fecha_desc', 'Más recientes'),
            ('fecha_asc', 'Más antiguos'),
        ],
        required=False,
        initial='relevancia',
        widget=forms.Select(attrs={'class': 'form-control'})
    )