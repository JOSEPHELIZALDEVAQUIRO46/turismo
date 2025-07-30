# turismo/models.py

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from core.models import TimeStampedModel

class Categoria(TimeStampedModel):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('turismo:lugares_categoria', kwargs={'slug': self.slug})
    
    class Meta:
        verbose_name_plural = "Categorías"

class LugarTuristico(TimeStampedModel):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='lugares')
    imagen_principal = models.ImageField(upload_to='lugares')
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    destacado = models.BooleanField(default=False)
    horario = models.TextField(blank=True)
    costo_entrada = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('turismo:lugar_detail', kwargs={'slug': self.slug})
    
    def get_imagen_principal_url(self):
        """Retorna la URL de la imagen principal o una imagen predeterminada"""
        if self.imagen_principal:
            return self.imagen_principal.url
        return '/static/img/placeholder.jpg'
    
    def tiene_coordenadas(self):
        """Verifica si el lugar tiene coordenadas para mostrar en mapa"""
        return self.latitud is not None and self.longitud is not None
    
    def get_rutas(self):
        """Obtener las rutas que incluyen este lugar"""
        return Ruta.objects.filter(puntos__lugar_turistico=self).distinct()
    
    class Meta:
        verbose_name_plural = "Lugares Turísticos"

class Imagen(models.Model):
    lugar_turistico = models.ForeignKey(LugarTuristico, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='lugares/galerias')
    titulo = models.CharField(max_length=100, blank=True)
    es_portada = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0, help_text="Orden de visualización")
    
    def __str__(self):
        return f"Imagen de {self.lugar_turistico.nombre}: {self.titulo or 'Sin título'}"
    
    def save(self, *args, **kwargs):
        """Si es portada, quita es_portada de otras imágenes"""
        if self.es_portada:
            Imagen.objects.filter(
                lugar_turistico=self.lugar_turistico, 
                es_portada=True
            ).exclude(pk=self.pk).update(es_portada=False)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['orden', 'id']

class Ruta(TimeStampedModel):
    DIFICULTAD_CHOICES = (
        ('facil', 'Fácil'),
        ('media', 'Media'),
        ('dificil', 'Difícil'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    duracion_estimada = models.CharField(max_length=50)  # Ej: "3 horas", "2 días"
    distancia = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distancia en kilómetros")
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES, default='facil')
    recomendaciones = models.TextField(blank=True)
    imagen_principal = models.ImageField(upload_to='rutas')
    mapa_ruta = models.JSONField(blank=True, null=True, help_text="Coordenadas del trazado para Google Maps")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('turismo:ruta_detail', kwargs={'slug': self.slug})
    
    def get_color_dificultad(self):
        """Retorna color CSS basado en la dificultad"""
        colors = {
            'facil': 'success',
            'media': 'warning',
            'dificil': 'danger'
        }
        return colors.get(self.dificultad, 'primary')
    
    def get_puntos_ordenados(self):
        """Obtiene los puntos ordenados por el atributo orden"""
        return self.puntos.all().order_by('orden')
    
    def get_primer_punto(self):
        """Obtiene el primer punto de la ruta para mostrar como inicio"""
        return self.puntos.order_by('orden').first()
    
    def get_ultimo_punto(self):
        """Obtiene el último punto de la ruta para mostrar como fin"""
        return self.puntos.order_by('orden').last()
    
    def get_lugares_turisticos(self):
        """Obtiene los lugares turísticos asociados a esta ruta"""
        return LugarTuristico.objects.filter(
            puntos_ruta__ruta=self
        ).distinct()

class PuntoRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='puntos')
    lugar_turistico = models.ForeignKey(LugarTuristico, on_delete=models.SET_NULL, null=True, blank=True, related_name='puntos_ruta')
    nombre = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(help_text="Posición en la secuencia de la ruta")
    latitud = models.FloatField()
    longitud = models.FloatField()
    tiempo_estancia = models.CharField(max_length=50, blank=True, help_text="Tiempo recomendado de parada")
    
    def __str__(self):
        if self.lugar_turistico:
            return f"{self.orden}. {self.lugar_turistico.nombre} - {self.ruta.nombre}"
        return f"{self.orden}. {self.nombre or 'Punto sin nombre'} - {self.ruta.nombre}"
    
    def get_nombre_display(self):
        """Retorna el nombre del punto o del lugar turístico si existe"""
        if self.lugar_turistico:
            return self.lugar_turistico.nombre
        return self.nombre or f"Punto {self.orden}"
    
    def get_descripcion_display(self):
        """Retorna la descripción del punto o del lugar turístico si existe"""
        if self.descripcion:
            return self.descripcion
        if self.lugar_turistico and self.lugar_turistico.descripcion:
            return self.lugar_turistico.descripcion
        return ""
    
    def get_imagen(self):
        """Retorna la imagen del lugar turístico o None"""
        if self.lugar_turistico and self.lugar_turistico.imagen_principal:
            return self.lugar_turistico.imagen_principal
        return None
    
    class Meta:
        ordering = ['orden']
        unique_together = ['ruta', 'orden']

class Establecimiento(TimeStampedModel):
    TIPO_CHOICES = (
        ('hotel', 'Hotel'),
        ('restaurante', 'Restaurante'),
        ('cafe', 'Café'),
        ('bar', 'Bar'),
        ('otro', 'Otro'),
    )
    
    RANGO_PRECIOS_CHOICES = (
        ('$', 'Económico'),
        ('$$', 'Moderado'),
        ('$$$', 'Costoso'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    imagen = models.ImageField(upload_to='establecimientos')
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    destacado = models.BooleanField(default=False)
    rango_precios = models.CharField(max_length=3, choices=RANGO_PRECIOS_CHOICES, default='$$')
    servicios = models.TextField(blank=True, help_text="Servicios ofrecidos separados por comas")
    horario = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def get_absolute_url(self):
        return reverse('turismo:establecimiento_detail', kwargs={'slug': self.slug})
    
    def get_servicios_list(self):
        """Convierte el campo servicios en una lista de servicios"""
        if not self.servicios:
            return []
        return [s.strip() for s in self.servicios.split(',') if s.strip()]
    
    def get_valoracion_promedio(self):
        """Calcula la valoración promedio del establecimiento"""
        from django.db.models import Avg
        from core.models import Valoracion
        
        valoraciones = Valoracion.objects.filter(
            establecimiento=self, 
            aprobado=True
        )
        
        if valoraciones.exists():
            promedio = valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            return round(promedio, 1)
        return 0
    
    def tiene_coordenadas(self):
        """Verifica si el establecimiento tiene coordenadas para mostrar en mapa"""
        return self.latitud is not None and self.longitud is not None
    
    def get_lugares_cercanos(self, limite=3):
        """
        Obtiene lugares turísticos cercanos (si tiene coordenadas)
        Para implementación real, se requeriría un cálculo de distancia geoespacial
        """
        if not self.tiene_coordenadas():
            return LugarTuristico.objects.filter(destacado=True)[:limite]
        
        # Esta es una implementación simplificada. Para producción,
        # habría que usar una consulta geoespacial como:
        # from django.contrib.gis.db.models.functions import Distance
        # from django.contrib.gis.geos import Point
        # point = Point(self.longitud, self.latitud, srid=4326)
        # return LugarTuristico.objects.filter(punto__isnull=False)
        #    .annotate(distance=Distance('punto', point))
        #    .order_by('distance')[:limite]
        
        return LugarTuristico.objects.filter(destacado=True)[:limite]

class Evento(TimeStampedModel):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    lugar = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='eventos')
    destacado = models.BooleanField(default=False)
    organizador = models.CharField(max_length=200, blank=True)
    contacto = models.TextField(blank=True)
    programa = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.titulo
    
    def get_absolute_url(self):
        return reverse('turismo:evento_detail', kwargs={'slug': self.slug})
    
    def ha_pasado(self):
        """Verifica si el evento ya ha pasado"""
        return timezone.now() > self.fecha_fin
    
    def esta_activo(self):
        """Verifica si el evento está activo actualmente"""
        now = timezone.now()
        return self.fecha_inicio <= now <= self.fecha_fin
    
    def get_estado_display(self):
        """Obtiene el estado del evento para mostrar"""
        if self.ha_pasado():
            return "Finalizado"
        elif self.esta_activo():
            return "En curso"
        else:
            return "Próximamente"
    
    def get_dias_faltantes(self):
        """Calcula los días faltantes para el evento"""
        if self.ha_pasado():
            return 0
        elif self.esta_activo():
            return 0
        
        from datetime import datetime
        dias = (self.fecha_inicio - timezone.now()).days
        return max(0, dias)  # Asegurarse de que no sea negativo
    
    def get_duracion_dias(self):
        """Calcula la duración del evento en días"""
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
    class Meta:
        ordering = ['fecha_inicio']

        # Nuevos models

class Transporte(TimeStampedModel):
    TIPO_TRANSPORTE_CHOICES = (
        ('bus', 'Autobús'),
        ('taxi', 'Taxi'),
        ('moto', 'Mototaxi'),
        ('bicicleta', 'Bicicleta'),
        ('caminata', 'Caminata'),
        ('vehiculo_propio', 'Vehículo Propio'),
        ('tour', 'Tour Organizado'),
        ('otro', 'Otro'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_TRANSPORTE_CHOICES)
    descripcion = models.TextField()
    origen = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    duracion_estimada = models.CharField(max_length=50, help_text="Ej: '30 minutos', '2 horas'")
    costo_aproximado = models.CharField(max_length=100, blank=True)
    contacto = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    horarios = models.TextField(blank=True, help_text="Horarios de operación")
    recomendaciones = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='transporte', blank=True)
    destacado = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def get_absolute_url(self):
        return reverse('turismo:transporte_detail', kwargs={'slug': self.slug})
    
    class Meta:
        verbose_name_plural = "Transportes"


class Artesania(TimeStampedModel):
    CATEGORIA_CHOICES = (
        ('ceramica', 'Cerámica'),
        ('textil', 'Textil'),
        ('madera', 'Madera'),
        ('cuero', 'Cuero'),
        ('metal', 'Metal'),
        ('piedra', 'Piedra'),
        ('fibra', 'Fibra Natural'),
        ('joyeria', 'Joyería'),
        ('otro', 'Otro'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.TextField()
    artesano = models.CharField(max_length=200, help_text="Nombre del artesano o taller")
    lugar_origen = models.CharField(max_length=255)
    tecnica_elaboracion = models.TextField(blank=True)
    materiales = models.TextField(help_text="Materiales utilizados separados por comas")
    precio_referencia = models.CharField(max_length=100, blank=True)
    tiempo_elaboracion = models.CharField(max_length=100, blank=True)
    imagen_principal = models.ImageField(upload_to='artesanias')
    destacado = models.BooleanField(default=False)
    disponible_venta = models.BooleanField(default=True)
    contacto_artesano = models.TextField(blank=True)
    historia = models.TextField(blank=True, help_text="Historia o tradición detrás de la artesanía")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} - {self.artesano}"
    
    def get_absolute_url(self):
        return reverse('turismo:artesania_detail', kwargs={'slug': self.slug})
    
    def get_materiales_list(self):
        """Convierte el campo materiales en una lista"""
        if not self.materiales:
            return []
        return [m.strip() for m in self.materiales.split(',') if m.strip()]
    
    class Meta:
        verbose_name_plural = "Artesanías"


class ActividadFisica(TimeStampedModel):
    TIPO_ACTIVIDAD_CHOICES = (
        ('senderismo', 'Senderismo'),
        ('escalada', 'Escalada'),
        ('ciclismo', 'Ciclismo'),
        ('natacion', 'Natación'),
        ('kayak', 'Kayak'),
        ('rafting', 'Rafting'),
        ('parapente', 'Parapente'),
        ('cabalgata', 'Cabalgata'),
        ('canopy', 'Canopy'),
        ('rappel', 'Rappel'),
        ('camping', 'Camping'),
        ('avistamiento', 'Avistamiento de Aves'),
        ('otro', 'Otra'),
    )
    
    DIFICULTAD_CHOICES = (
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    tipo_actividad = models.CharField(max_length=20, choices=TIPO_ACTIVIDAD_CHOICES)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    dificultad = models.CharField(max_length=15, choices=DIFICULTAD_CHOICES, default='principiante')
    duracion = models.CharField(max_length=50, help_text="Ej: '2 horas', 'Día completo'")
    costo = models.CharField(max_length=100, blank=True)
    edad_minima = models.PositiveSmallIntegerField(default=0, help_text="Edad mínima recomendada")
    capacidad_maxima = models.PositiveSmallIntegerField(blank=True, null=True)
    equipamiento_incluido = models.TextField(blank=True, help_text="Equipamiento proporcionado")
    equipamiento_requerido = models.TextField(blank=True, help_text="Equipamiento que debe traer el participante")
    recomendaciones_salud = models.TextField(blank=True)
    mejor_epoca = models.CharField(max_length=200, blank=True, help_text="Mejor época del año para la actividad")
    horarios_disponibles = models.TextField(blank=True)
    instructor_guia = models.CharField(max_length=200, blank=True)
    contacto = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, null=True)
    imagen_principal = models.ImageField(upload_to='actividades_fisicas')
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    destacado = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_actividad_display()})"
    
    def get_absolute_url(self):
        return reverse('turismo:actividad_fisica_detail', kwargs={'slug': self.slug})
    
    def get_color_dificultad(self):
        """Retorna color CSS basado en la dificultad"""
        colors = {
            'principiante': 'success',
            'intermedio': 'warning',
            'avanzado': 'danger',
            'experto': 'dark'
        }
        return colors.get(self.dificultad, 'primary')
    
    def get_equipamiento_incluido_list(self):
        """Convierte el equipamiento incluido en una lista"""
        if not self.equipamiento_incluido:
            return []
        return [e.strip() for e in self.equipamiento_incluido.split(',') if e.strip()]
    
    def get_equipamiento_requerido_list(self):
        """Convierte el equipamiento requerido en una lista"""
        if not self.equipamiento_requerido:
            return []
        return [e.strip() for e in self.equipamiento_requerido.split(',') if e.strip()]
    
    def tiene_coordenadas(self):
        """Verifica si la actividad tiene coordenadas para mostrar en mapa"""
        return self.latitud is not None and self.longitud is not None
    
    def es_apta_para_edad(self, edad):
        """Verifica si una persona de cierta edad puede realizar la actividad"""
        return edad >= self.edad_minima
    
    class Meta:
        verbose_name_plural = "Actividades Físicas"


class ImagenArtesania(models.Model):
    artesania = models.ForeignKey(Artesania, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='artesanias/galerias')
    titulo = models.CharField(max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(default=0, help_text="Orden de visualización")
    
    def __str__(self):
        return f"Imagen de {self.artesania.nombre}: {self.titulo or 'Sin título'}"
    
    class Meta:
        ordering = ['orden', 'id']


class ImagenActividadFisica(models.Model):
    actividad = models.ForeignKey(ActividadFisica, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='actividades_fisicas/galerias')
    titulo = models.CharField(max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(default=0, help_text="Orden de visualización")
    
    def __str__(self):
        return f"Imagen de {self.actividad.nombre}: {self.titulo or 'Sin título'}"
    
    class Meta:
        ordering = ['orden', 'id']
