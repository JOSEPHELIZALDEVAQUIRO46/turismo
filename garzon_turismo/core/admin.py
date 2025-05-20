from django.contrib import admin
from .models import ConfiguracionSitio, PaginaEstatica, Testimonio, Banner, Comentario, Valoracion

@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_sitio', 'slogan', 'descripcion_sitio')
        }),
        ('Contacto', {
            'fields': ('email_contacto', 'telefono_contacto', 'direccion', 'horario_atencion')
        }),
        ('Redes Sociales', {
            'fields': ('facebook', 'instagram', 'twitter', 'youtube', 'whatsapp')
        }),
        ('Identidad Visual', {
            'fields': ('logo', 'favicon', 'logo_footer')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords', 'google_analytics')
        }),
        ('Textos Legales', {
            'fields': ('texto_footer', 'texto_cookies', 'texto_privacidad', 'texto_terminos')
        }),
    )
   
    def has_add_permission(self, request):
        # Limitar a una sola instancia de configuración
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(PaginaEstatica)
class PaginaEstaticaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'en_menu', 'orden_menu')
    list_filter = ('en_menu',)
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cargo', 'valoracion', 'activo')
    list_filter = ('activo', 'valoracion')
    search_fields = ('nombre', 'cargo', 'contenido')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'orden')
    list_filter = ('activo',)
    search_fields = ('titulo', 'subtitulo')
    list_editable = ('activo', 'orden')

# Nuevos modelos a registrar

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_entidad', 'created', 'aprobado')
    list_filter = ('aprobado', 'created')
    search_fields = ('nombre', 'email', 'contenido')
    actions = ['aprobar_comentarios']
    
    def get_entidad(self, obj):
        if obj.lugar_turistico:
            return f"Lugar: {obj.lugar_turistico.nombre}"
        elif obj.establecimiento:
            return f"Estab: {obj.establecimiento.nombre}"
        elif obj.post:
            return f"Post: {obj.post.titulo}"
        return "N/A"
    get_entidad.short_description = "Entidad"
    
    def aprobar_comentarios(self, request, queryset):
        queryset.update(aprobado=True)
    aprobar_comentarios.short_description = "Aprobar comentarios seleccionados"

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'establecimiento', 'puntuacion', 'created', 'aprobado')
    list_filter = ('aprobado', 'puntuacion', 'created')
    search_fields = ('nombre', 'email', 'comentario', 'establecimiento__nombre')
    actions = ['aprobar_valoraciones']
    
    def aprobar_valoraciones(self, request, queryset):
        queryset.update(aprobado=True)
    aprobar_valoraciones.short_description = "Aprobar valoraciones seleccionadas"