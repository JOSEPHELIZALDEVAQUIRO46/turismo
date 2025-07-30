# turismo/admin.py

from django.contrib import admin
from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, PuntoRuta, Establecimiento, Evento,
    Transporte, Artesania, ActividadFisica, ImagenArtesania, ImagenActividadFisica
)

class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1

class PuntoRutaInline(admin.TabularInline):
    model = PuntoRuta
    extra = 1

class ImagenArtesaniaInline(admin.TabularInline):
    model = ImagenArtesania
    extra = 1

class ImagenActividadFisicaInline(admin.TabularInline):
    model = ImagenActividadFisica
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(LugarTuristico)
class LugarTuristicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'destacado')
    list_filter = ('categoria', 'destacado')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenInline]
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'categoria', 'descripcion', 'direccion')
        }),
        ('Multimedia', {
            'fields': ('imagen_principal',)
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud')
        }),
        ('Información adicional', {
            'fields': ('horario', 'costo_entrada', 'destacado')
        }),
    )

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_estimada', 'distancia', 'dificultad')
    list_filter = ('dificultad',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [PuntoRutaInline]

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'direccion', 'telefono', 'destacado')
    list_filter = ('tipo', 'destacado', 'rango_precios')
    search_fields = ('nombre', 'descripcion', 'direccion')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'lugar', 'destacado')
    list_filter = ('destacado',)
    search_fields = ('titulo', 'descripcion', 'lugar')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_inicio'

# ========== ADMINISTRADORES PARA LOS NUEVOS MODELOS ==========

@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'origen', 'destino', 'destacado', 'disponible')
    list_filter = ('tipo', 'destacado', 'disponible')
    search_fields = ('nombre', 'descripcion', 'origen', 'destino')
    prepopulated_fields = {'slug': ('nombre',)}
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'tipo', 'descripcion')
        }),
        ('Rutas', {
            'fields': ('origen', 'destino', 'duracion_estimada')
        }),
        ('Información comercial', {
            'fields': ('costo_aproximado', 'contacto', 'telefono', 'horarios')
        }),
        ('Multimedia y estado', {
            'fields': ('imagen', 'destacado', 'disponible')
        }),
        ('Información adicional', {
            'fields': ('recomendaciones',)
        }),
    )

@admin.register(Artesania)
class ArtesaniaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'artesano', 'lugar_origen', 'destacado', 'disponible_venta')
    list_filter = ('categoria', 'destacado', 'disponible_venta')
    search_fields = ('nombre', 'descripcion', 'artesano', 'lugar_origen')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenArtesaniaInline]
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'categoria', 'descripcion')
        }),
        ('Artesano', {
            'fields': ('artesano', 'lugar_origen', 'contacto_artesano')
        }),
        ('Proceso de elaboración', {
            'fields': ('tecnica_elaboracion', 'materiales', 'tiempo_elaboracion')
        }),
        ('Información comercial', {
            'fields': ('precio_referencia', 'disponible_venta')
        }),
        ('Multimedia y destacados', {
            'fields': ('imagen_principal', 'destacado')
        }),
        ('Historia y tradición', {
            'fields': ('historia',)
        }),
    )

@admin.register(ActividadFisica)
class ActividadFisicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_actividad', 'dificultad', 'ubicacion', 'destacado', 'disponible')
    list_filter = ('tipo_actividad', 'dificultad', 'destacado', 'disponible')
    search_fields = ('nombre', 'descripcion', 'ubicacion', 'instructor_guia')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenActividadFisicaInline]
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'tipo_actividad', 'descripcion', 'ubicacion')
        }),
        ('Características de la actividad', {
            'fields': ('dificultad', 'duracion', 'edad_minima', 'capacidad_maxima')
        }),
        ('Equipamiento', {
            'fields': ('equipamiento_incluido', 'equipamiento_requerido')
        }),
        ('Información práctica', {
            'fields': ('costo', 'horarios_disponibles', 'mejor_epoca')
        }),
        ('Contacto y guía', {
            'fields': ('instructor_guia', 'contacto', 'telefono', 'email')
        }),
        ('Ubicación geográfica', {
            'fields': ('latitud', 'longitud')
        }),
        ('Multimedia y estado', {
            'fields': ('imagen_principal', 'destacado', 'disponible')
        }),
        ('Recomendaciones', {
            'fields': ('recomendaciones_salud',)
        }),
    )