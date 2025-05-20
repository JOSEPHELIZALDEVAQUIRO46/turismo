from django.contrib import admin
from .models import CategoriaBlog, Post, ComentarioBlog

@admin.register(CategoriaBlog)
class CategoriaBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_publicacion', 'publicado')
    list_filter = ('publicado', 'categorias')
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ('categorias',)
    date_hierarchy = 'fecha_publicacion'
    fieldsets = (
        (None, {
            'fields': ('titulo', 'slug', 'autor', 'contenido')
        }),
        ('Categorización', {
            'fields': ('categorias',)
        }),
        ('Multimedia', {
            'fields': ('imagen_destacada',)
        }),
        ('Estado', {
            'fields': ('publicado',)
        }),
    )

# Comentamos temporalmente el registro de ComentarioBlog
# @admin.register(ComentarioBlog)
# class ComentarioBlogAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'post', 'created', 'aprobado')  
#     list_filter = ('aprobado', 'created')
#     search_fields = ('nombre', 'email', 'contenido')
#     actions = ['aprobar_comentarios']
   
#     def aprobar_comentarios(self, request, queryset):
#         queryset.update(aprobado=True)
#     aprobar_comentarios.short_description = "Aprobar comentarios seleccionados"