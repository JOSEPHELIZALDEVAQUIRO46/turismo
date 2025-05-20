# core/models.py

from django.db import models
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ConfiguracionSitio(TimeStampedModel):
    """
    Configuración general del sitio web
    """
    nombre_sitio = models.CharField(max_length=100, default="Alma del Huila")
    slogan = models.CharField(max_length=200, blank=True)
    descripcion_sitio = models.TextField()
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    horario_atencion = models.CharField(max_length=200, blank=True)
    
    # Redes sociales
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    
    # Archivos
    logo = models.ImageField(upload_to='site', null=True, blank=True)
    favicon = models.ImageField(upload_to='site', null=True, blank=True)
    logo_footer = models.ImageField(upload_to='site', null=True, blank=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True, 
                                      help_text="Descripción para motores de búsqueda (máx. 160 caracteres)")
    meta_keywords = models.CharField(max_length=255, blank=True,
                                  help_text="Palabras clave separadas por comas")
    google_analytics = models.TextField(blank=True, 
                                     help_text="Código de seguimiento de Google Analytics")
    
    # Contenidos adicionales
    texto_footer = models.TextField(blank=True)
    texto_cookies = models.TextField(blank=True)
    texto_privacidad = models.TextField(blank=True)
    texto_terminos = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre_sitio
    
    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuración del Sitio"

class PaginaEstatica(TimeStampedModel):
    """
    Modelo para páginas estáticas como Acerca de, Términos, etc.
    """
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    contenido = models.TextField()
    imagen_cabecera = models.ImageField(upload_to='paginas', blank=True, null=True)
    en_menu = models.BooleanField(default=False)
    orden_menu = models.PositiveSmallIntegerField(default=0)
    meta_description = models.CharField(max_length=160, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['orden_menu']
        verbose_name = "Página Estática"
        verbose_name_plural = "Páginas Estáticas"

class Testimonio(TimeStampedModel):
    """
    Testimonios para mostrar en la página principal
    """
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='testimonios', blank=True, null=True)
    contenido = models.TextField()
    valoracion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Testimonio de {self.nombre}"
    
    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"

class Banner(TimeStampedModel):
    """
    Banners para mostrar en la página principal
    """
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True)
    imagen = models.ImageField(upload_to='banners')
    url = models.URLField(blank=True)
    texto_boton = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

# Nuevos modelos a añadir

class Comentario(TimeStampedModel):
    """
    Modelo para comentarios en diferentes entidades del sistema
    """
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    contenido = models.TextField()
    aprobado = models.BooleanField(default=False)
    
    # Campos para relaciones polimórficas
    # Estos campos se usarán para vincular el comentario a diferentes modelos
    # Solo uno de ellos debe tener valor
    lugar_turistico = models.ForeignKey(
        'turismo.LugarTuristico', 
        on_delete=models.CASCADE, 
        related_name='comentarios', 
        null=True, 
        blank=True
    )
    establecimiento = models.ForeignKey(
        'turismo.Establecimiento', 
        on_delete=models.CASCADE, 
        related_name='comentarios', 
        null=True, 
        blank=True
    )
    post = models.ForeignKey(
        'blog.Post', 
        on_delete=models.CASCADE, 
        related_name='comentarios', 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"Comentario de {self.nombre} - {self.created.strftime('%d/%m/%Y')}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

class Valoracion(TimeStampedModel):
    """
    Modelo para valoraciones de establecimientos
    """
    establecimiento = models.ForeignKey(
        'turismo.Establecimiento', 
        on_delete=models.CASCADE, 
        related_name='valoraciones'
    )
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    puntuacion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Valoración {self.puntuacion}/5 para {self.establecimiento.nombre}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"