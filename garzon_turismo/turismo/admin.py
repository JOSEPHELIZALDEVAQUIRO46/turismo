# turismo/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, PuntoRuta, Establecimiento, Evento,
    Transporte, Artesania, ActividadFisica, ImagenArtesania, ImagenActividadFisica,
    CategoriaArtesania, CategoriaActividadFisica
)

# ========== INLINES ==========

class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1
    fields = ('imagen', 'titulo', 'es_portada', 'orden')
    readonly_fields = ('vista_previa',)
    
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.imagen.url)
        return "Sin imagen"
    vista_previa.short_description = "Vista previa"

class PuntoRutaInline(admin.TabularInline):
    model = PuntoRuta
    extra = 1
    fields = ('orden', 'lugar_turistico', 'nombre', 'latitud', 'longitud', 'tiempo_estancia', 'mostrar_en_mapa')
    ordering = ('orden',)

class ImagenArtesaniaInline(admin.TabularInline):
    model = ImagenArtesania
    extra = 1
    fields = ('imagen', 'titulo', 'orden')
    readonly_fields = ('vista_previa',)
    
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.imagen.url)
        return "Sin imagen"
    vista_previa.short_description = "Vista previa"

class ImagenActividadFisicaInline(admin.TabularInline):
    model = ImagenActividadFisica
    extra = 1
    fields = ('imagen', 'titulo', 'orden')
    readonly_fields = ('vista_previa',)
    
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.imagen.url)
        return "Sin imagen"
    vista_previa.short_description = "Vista previa"

# ========== ADMINISTRADORES PRINCIPALES ==========

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'total_lugares')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre', 'descripcion')
    
    def total_lugares(self, obj):
        return obj.lugares.count()
    total_lugares.short_description = "Total lugares"

@admin.register(LugarTuristico)
class LugarTuristicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'destacado', 'tiene_coordenadas_display', 'vista_previa_imagen')
    list_filter = ('categoria', 'destacado')  # Agrega 'created' si existe en tu TimeStampedModel
    search_fields = ('nombre', 'descripcion', 'direccion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenInline]
    readonly_fields = ('vista_previa_imagen', 'url_absoluta')
    
    # Si tu TimeStampedModel tiene campo 'created', descomenta la siguiente línea:
    # date_hierarchy = 'created'
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'categoria', 'descripcion', 'direccion')
        }),
        ('Multimedia', {
            'fields': ('imagen_principal', 'vista_previa_imagen')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud'),
            'description': 'Coordenadas geográficas para mostrar en el mapa'
        }),
        ('Información adicional', {
            'fields': ('horario', 'costo_entrada', 'destacado')
        }),
        ('Enlaces', {
            'fields': ('url_absoluta',),
            'classes': ('collapse',)
        }),
    )
    
    def tiene_coordenadas_display(self, obj):
        if obj.tiene_coordenadas():
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    tiene_coordenadas_display.short_description = "Tiene coordenadas"
    
    def vista_previa_imagen(self, obj):
        if obj.imagen_principal:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.imagen_principal.url)
        return "Sin imagen"
    vista_previa_imagen.short_description = "Vista previa"
    
    def url_absoluta(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "Guarda primero para ver la URL"
    url_absoluta.short_description = "URL del lugar"

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_estimada', 'distancia', 'dificultad', 'total_puntos', 'tiene_mapa')
    list_filter = ('dificultad',)  # Removido 'created_at'
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [PuntoRutaInline]
    readonly_fields = ('vista_mapa', 'estadisticas_puntos', 'url_absoluta')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Características', {
            'fields': ('duracion_estimada', 'distancia', 'dificultad')
        }),
        ('Multimedia', {
            'fields': ('imagen_principal',)
        }),
        ('Configuración del mapa', {
            'fields': ('mapa_configuracion',),
            'classes': ('collapse',),
            'description': 'Configuración avanzada del mapa en formato JSON'
        }),
        ('Información adicional', {
            'fields': ('recomendaciones',)
        }),
        ('Estadísticas', {
            'fields': ('estadisticas_puntos', 'vista_mapa'),
            'classes': ('collapse',)
        }),
        ('Enlaces', {
            'fields': ('url_absoluta',),
            'classes': ('collapse',)
        }),
    )
    
    def total_puntos(self, obj):
        return obj.puntos.count()
    total_puntos.short_description = "Puntos"
    
    def tiene_mapa(self, obj):
        if obj.tiene_puntos():
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    tiene_mapa.short_description = "Tiene mapa"
    
    def acciones(self, obj):
        if obj.pk and obj.tiene_puntos():
            mapa_url = reverse('admin:turismo_ruta_change', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button">Ver mapa</a>',
                reverse('turismo:ruta_mapa', kwargs={'slug': obj.slug})
            )
        return "Sin puntos"
    acciones.short_description = "Acciones"
    
    def estadisticas_puntos(self, obj):
        stats = f"""
        <strong>Total puntos:</strong> {obj.puntos.count()}<br>
        <strong>Con lugares turísticos:</strong> {obj.puntos.filter(lugar_turistico__isnull=False).count()}<br>
        <strong>Mostrados en mapa:</strong> {obj.puntos.filter(mostrar_en_mapa=True).count()}
        """
        return format_html(stats)
    estadisticas_puntos.short_description = "Estadísticas de puntos"
    
    def vista_mapa(self, obj):
        if obj.pk and obj.tiene_puntos():
            return format_html(
                '<iframe src="{}" width="300" height="200" style="border:1px solid #ccc;"></iframe>',
                reverse('turismo:ruta_mapa', kwargs={'slug': obj.slug})
            )
        return "Sin puntos para mostrar mapa"
    vista_mapa.short_description = "Vista previa del mapa"
    
    def url_absoluta(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "Guarda primero para ver la URL"
    url_absoluta.short_description = "URL de la ruta"

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'direccion', 'telefono', 'destacado', 'valoracion_promedio_display')
    list_filter = ('tipo', 'destacado', 'rango_precios')
    search_fields = ('nombre', 'descripcion', 'direccion', 'servicios')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('valoracion_promedio_display', 'url_absoluta')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'tipo', 'descripcion', 'direccion')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'sitio_web')
        }),
        ('Multimedia', {
            'fields': ('imagen',)
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud')
        }),
        ('Información comercial', {
            'fields': ('rango_precios', 'servicios', 'horario')
        }),
        ('Estado', {
            'fields': ('destacado', 'valoracion_promedio_display')
        }),
        ('Enlaces', {
            'fields': ('url_absoluta',),
            'classes': ('collapse',)
        }),
    )
    
    def valoracion_promedio_display(self, obj):
        promedio = obj.get_valoracion_promedio()
        if promedio > 0:
            stars = '★' * int(promedio) + '☆' * (5 - int(promedio))
            return format_html(f'{stars} ({promedio:.1f})')
        return "Sin valoraciones"
    valoracion_promedio_display.short_description = "Valoración promedio"
    
    def url_absoluta(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "Guarda primero para ver la URL"
    url_absoluta.short_description = "URL del establecimiento"

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'lugar', 'destacado', 'estado_display')
    list_filter = ('destacado', 'fecha_inicio')
    search_fields = ('titulo', 'descripcion', 'lugar', 'organizador')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('estado_display', 'dias_faltantes_display', 'url_absoluta')
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'slug', 'descripcion')
        }),
        ('Fechas y lugar', {
            'fields': ('fecha_inicio', 'fecha_fin', 'lugar')
        }),
        ('Multimedia', {
            'fields': ('imagen',)
        }),
        ('Organización', {
            'fields': ('organizador', 'contacto', 'programa')
        }),
        ('Estado', {
            'fields': ('destacado', 'estado_display', 'dias_faltantes_display')
        }),
        ('Enlaces', {
            'fields': ('url_absoluta',),
            'classes': ('collapse',)
        }),
    )
    
    def estado_display(self, obj):
        estado = obj.get_estado_display()
        color = {'Finalizado': 'red', 'En curso': 'green', 'Próximamente': 'blue'}.get(estado, 'black')
        return format_html(f'<span style="color: {color};">{estado}</span>')
    estado_display.short_description = "Estado"
    
    def dias_faltantes_display(self, obj):
        dias = obj.get_dias_faltantes()
        if dias > 0:
            return f"{dias} días"
        return "Ya comenzó o finalizó"
    dias_faltantes_display.short_description = "Días faltantes"
    
    def url_absoluta(self, obj):
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "Guarda primero para ver la URL"
    url_absoluta.short_description = "URL del evento"

# ========== ADMINISTRADORES PARA NUEVOS MODELOS ==========

@admin.register(CategoriaArtesania)
class CategoriaArtesaniaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'orden', 'total_artesanias', 'icono_display')
    list_editable = ('orden',)
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    
    def total_artesanias(self, obj):
        return obj.artesanias.filter(disponible_venta=True).count()
    total_artesanias.short_description = "Total artesanías"
    
    def icono_display(self, obj):
        if obj.icono:
            return format_html(f'<i class="{obj.icono}"></i> {obj.icono}')
        return "Sin icono"
    icono_display.short_description = "Icono"

@admin.register(CategoriaActividadFisica)
class CategoriaActividadFisicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'orden', 'total_actividades', 'icono_display', 'color_display')
    list_editable = ('orden',)
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    
    def total_actividades(self, obj):
        return obj.actividades.filter(disponible=True).count()
    total_actividades.short_description = "Total actividades"
    
    def icono_display(self, obj):
        if obj.icono:
            return format_html(f'<i class="{obj.icono}"></i> {obj.icono}')
        return "Sin icono"
    icono_display.short_description = "Icono"
    
    def color_display(self, obj):
        if obj.color_tema:
            return format_html(
                f'<div style="width: 20px; height: 20px; background-color: {obj.color_tema}; '
                f'display: inline-block; border: 1px solid #ccc;"></div> {obj.color_tema}'
            )
        return "Sin color"
    color_display.short_description = "Color"

@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'origen', 'destino', 'destacado', 'disponible')
    list_filter = ('tipo', 'destacado', 'disponible')
    search_fields = ('nombre', 'descripcion', 'origen', 'destino')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('destacado', 'disponible')
    
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
    list_filter = ('categoria', 'destacado', 'disponible_venta', 'lugar_origen')
    search_fields = ('nombre', 'descripcion', 'artesano', 'lugar_origen')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenArtesaniaInline]
    list_editable = ('destacado', 'disponible_venta')
    
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
    list_display = ('nombre', 'categoria', 'dificultad', 'ubicacion', 'edad_minima', 'destacado', 'disponible')
    list_filter = ('categoria', 'dificultad', 'destacado', 'disponible', 'nivel_riesgo')
    search_fields = ('nombre', 'descripcion', 'ubicacion', 'instructor_guia')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenActividadFisicaInline]
    list_editable = ('destacado', 'disponible')
    readonly_fields = ('coordenadas_display',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'categoria', 'descripcion', 'ubicacion')
        }),
        ('Características de la actividad', {
            'fields': ('dificultad', 'duracion', 'edad_minima', 'capacidad_maxima', 'nivel_riesgo')
        }),
        ('Disponibilidad', {
            'fields': ('requiere_reserva', 'disponible_todo_año')
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
            'fields': ('latitud', 'longitud', 'coordenadas_display'),
            'description': 'Coordenadas para mostrar en el mapa'
        }),
        ('Multimedia y estado', {
            'fields': ('imagen_principal', 'destacado', 'disponible')
        }),
        ('Recomendaciones', {
            'fields': ('recomendaciones_salud',)
        }),
    )
    
    def coordenadas_display(self, obj):
        if obj.tiene_coordenadas():
            return format_html(f'Lat: {obj.latitud}, Lng: {obj.longitud}<br><small>✓ Válidas para mapa</small>')
        return "Sin coordenadas"
    coordenadas_display.short_description = "Coordenadas"

# ========== CONFIGURACIÓN GLOBAL DEL ADMIN ==========

# Personalizar el título del admin
admin.site.site_header = "Administración - Garzón Turismo"
admin.site.site_title = "Garzón Turismo Admin"
admin.site.index_title = "Panel de Administración"

# Registrar modelos adicionales si es necesario
# admin.site.register(Imagen)  # Ya se maneja como inline
# admin.site.register(PuntoRuta)  # Ya se maneja como inline