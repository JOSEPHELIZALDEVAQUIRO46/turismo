from django.db import models

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class CategoriaBlog(TimeStampedModel):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría del Blog"
        verbose_name_plural = "Categorías del Blog"

class Post(TimeStampedModel):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    contenido = models.TextField()
    imagen_destacada = models.ImageField(upload_to='blog')
    categorias = models.ManyToManyField(CategoriaBlog, related_name='posts')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    publicado = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['-fecha_publicacion']
class ComentarioBlog(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios_blog') 
    email = models.EmailField()
    contenido = models.TextField()
    aprobado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comentario de {self.nombre} en {self.post.titulo}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"