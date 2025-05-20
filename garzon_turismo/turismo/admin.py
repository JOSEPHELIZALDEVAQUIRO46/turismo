from django.contrib import admin
from .models import Categoria, LugarTuristico, Imagen, Ruta, PuntoRuta, Establecimiento, Evento

class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1

class PuntoRutaInline(admin.TabularInline):
    model = PuntoRuta
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
