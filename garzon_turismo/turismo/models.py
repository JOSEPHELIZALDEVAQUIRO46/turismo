# turismo/models.py

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel
import json

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
    latitud = models.FloatField(null=True, blank=True, help_text="Latitud en formato decimal")
    longitud = models.FloatField(null=True, blank=True, help_text="Longitud en formato decimal")
    destacado = models.BooleanField(default=False)
    horario = models.TextField(blank=True)
    costo_entrada = models.CharField(max_length=100, blank=True)
    
    def clean(self):
        """Validación personalizada para coordenadas"""
        if self.latitud is not None and (self.latitud < -90 or self.latitud > 90):
            raise ValidationError({'latitud': 'La latitud debe estar entre -90 y 90 grados'})
        if self.longitud is not None and (self.longitud < -180 or self.longitud > 180):
            raise ValidationError({'longitud': 'La longitud debe estar entre -180 y 180 grados'})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        self.clean()
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
    
    def get_coordenadas_dict(self):
        """Retorna las coordenadas como diccionario para usar en mapas"""
        if self.tiene_coordenadas():
            return {
                'lat': float(self.latitud),
                'lng': float(self.longitud),
                'nombre': self.nombre,
                'descripcion': self.descripcion[:100] + '...' if len(self.descripcion) > 100 else self.descripcion,
                'url': self.get_absolute_url(),
                'imagen': self.get_imagen_principal_url()
            }
        return None
    
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
    
    # Campo mejorado para el mapa de la ruta
    mapa_configuracion = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Configuración específica del mapa (centro, zoom, estilo, etc.)"
    )
    
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
    
    def get_coordenadas_puntos(self):
        """Retorna todas las coordenadas de los puntos de esta ruta para el mapa"""
        puntos = self.get_puntos_ordenados()
        coordenadas = []
        
        for punto in puntos:
            coord_data = {
                'lat': float(punto.latitud),
                'lng': float(punto.longitud),
                'orden': punto.orden,
                'nombre': punto.get_nombre_display(),
                'descripcion': punto.get_descripcion_display(),
                'tiempo_estancia': punto.tiempo_estancia,
                'es_lugar_turistico': punto.lugar_turistico is not None,
            }
            
            # Si tiene lugar turístico asociado, agregar información adicional
            if punto.lugar_turistico:
                coord_data.update({
                    'lugar_url': punto.lugar_turistico.get_absolute_url(),
                    'imagen': punto.lugar_turistico.get_imagen_principal_url(),
                    'categoria': punto.lugar_turistico.categoria.nombre,
                })
            elif punto.get_imagen():
                coord_data['imagen'] = punto.get_imagen().url
            
            coordenadas.append(coord_data)
        
        return coordenadas
    
    def get_centro_mapa(self):
        """Calcula el centro del mapa basado en los puntos de la ruta"""
        puntos = self.get_puntos_ordenados()
        if not puntos:
            # Coordenadas por defecto para Garzón, Huila
            return {'lat': 2.1964, 'lng': -75.6472}
        
        latitudes = [punto.latitud for punto in puntos]
        longitudes = [punto.longitud for punto in puntos]
        
        centro_lat = sum(latitudes) / len(latitudes)
        centro_lng = sum(longitudes) / len(longitudes)
        
        return {'lat': centro_lat, 'lng': centro_lng}
    
    def get_configuracion_mapa(self):
        """Retorna la configuración completa del mapa para esta ruta"""
        config_base = {
            'centro': self.get_centro_mapa(),
            'zoom': 13,
            'puntos': self.get_coordenadas_puntos(),
            'estilo_marcador': 'numbered',  # numbered, colored, custom
            'mostrar_ruta': True,
            'color_ruta': self.get_color_dificultad_hex(),
        }
        
        # Si hay configuración personalizada, la fusiona
        if self.mapa_configuracion:
            config_base.update(self.mapa_configuracion)
        
        return config_base
    
    def get_color_dificultad_hex(self):
        """Retorna color hexadecimal basado en la dificultad para usar en mapas"""
        colors = {
            'facil': '#28a745',    # Verde
            'media': '#ffc107',    # Amarillo
            'dificil': '#dc3545'   # Rojo
        }
        return colors.get(self.dificultad, '#007bff')  # Azul por defecto
    
    def tiene_puntos(self):
        """Verifica si la ruta tiene puntos definidos"""
        return self.puntos.exists()
    
    def get_bounds_mapa(self):
        """Calcula los límites del mapa para ajustar automáticamente el zoom"""
        puntos = self.get_puntos_ordenados()
        if not puntos:
            return None
        
        latitudes = [punto.latitud for punto in puntos]
        longitudes = [punto.longitud for punto in puntos]
        
        return {
            'north': max(latitudes),
            'south': min(latitudes),
            'east': max(longitudes),
            'west': min(longitudes)
        }

class PuntoRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='puntos')
    lugar_turistico = models.ForeignKey(
        LugarTuristico, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='puntos_ruta'
    )
    nombre = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(help_text="Posición en la secuencia de la ruta")
    latitud = models.FloatField(help_text="Latitud en formato decimal")
    longitud = models.FloatField(help_text="Longitud en formato decimal")
    tiempo_estancia = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Tiempo recomendado de parada (ej: '30 min', '2 horas')"
    )
    
    # Nuevos campos para mejorar la funcionalidad del mapa
    icono_personalizado = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Nombre del icono personalizado para este punto"
    )
    color_marcador = models.CharField(
        max_length=7, 
        blank=True,
        help_text="Color hexadecimal del marcador (ej: #FF0000)"
    )
    mostrar_en_mapa = models.BooleanField(
        default=True,
        help_text="Si está marcado, este punto se mostrará en el mapa"
    )
    
    def clean(self):
        """Validación personalizada"""
        # Validar coordenadas
        if self.latitud < -90 or self.latitud > 90:
            raise ValidationError({'latitud': 'La latitud debe estar entre -90 y 90 grados'})
        if self.longitud < -180 or self.longitud > 180:
            raise ValidationError({'longitud': 'La longitud debe estar entre -180 y 180 grados'})
        
        # Si no tiene lugar turístico, debe tener al menos un nombre
        if not self.lugar_turistico and not self.nombre:
            raise ValidationError({'nombre': 'Debe proporcionar un nombre si no hay lugar turístico asociado'})
    
    def save(self, *args, **kwargs):
        self.clean()
        # Si está asociado a un lugar turístico y no tiene coordenadas definidas,
        # usar las coordenadas del lugar turístico
        if self.lugar_turistico and self.lugar_turistico.tiene_coordenadas():
            # Solo asignar coordenadas si son None (no definidas)
            if self.latitud is None:
                self.latitud = self.lugar_turistico.latitud
            if self.longitud is None:
                self.longitud = self.lugar_turistico.longitud
        
        # Si después de todo aún hay coordenadas None, asignar valores por defecto
        # (esto evita errores de base de datos si el campo no permite NULL)
        if self.latitud is None:
            self.latitud = 0.0
        if self.longitud is None:
            self.longitud = 0.0
            
        super().save(*args, **kwargs)
    
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
            # Truncar descripción larga para el mapa
            desc = self.lugar_turistico.descripcion
            return desc[:150] + '...' if len(desc) > 150 else desc
        return ""
    
    def get_imagen(self):
        """Retorna la imagen del lugar turístico o None"""
        if self.lugar_turistico and self.lugar_turistico.imagen_principal:
            return self.lugar_turistico.imagen_principal
        return None
    
    def get_coordenadas_dict(self):
        """Retorna las coordenadas como diccionario para JavaScript"""
        return {
            'lat': float(self.latitud),
            'lng': float(self.longitud)
        }
    
    def get_info_marcador(self):
        """Retorna información completa para el marcador del mapa"""
        info = {
            'id': self.id,
            'orden': self.orden,
            'lat': float(self.latitud),
            'lng': float(self.longitud),
            'nombre': self.get_nombre_display(),
            'descripcion': self.get_descripcion_display(),
            'tiempo_estancia': self.tiempo_estancia,
            'mostrar': self.mostrar_en_mapa,
        }
        
        # Agregar información específica del lugar turístico si existe
        if self.lugar_turistico:
            info.update({
                'es_lugar_turistico': True,
                'lugar_url': self.lugar_turistico.get_absolute_url(),
                'categoria': self.lugar_turistico.categoria.nombre,
                'direccion': self.lugar_turistico.direccion,
                'imagen': self.lugar_turistico.get_imagen_principal_url(),
            })
        else:
            info['es_lugar_turistico'] = False
        
        # Personalización del marcador
        if self.color_marcador:
            info['color'] = self.color_marcador
        if self.icono_personalizado:
            info['icono'] = self.icono_personalizado
        
        return info
    
    class Meta:
        ordering = ['orden']
        unique_together = ['ruta', 'orden']
        verbose_name = "Punto de Ruta"
        verbose_name_plural = "Puntos de Ruta"

# Resto de modelos sin cambios significativos...

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
        """Obtiene lugares turísticos cercanos (implementación simplificada)"""
        if not self.tiene_coordenadas():
            return LugarTuristico.objects.filter(destacado=True)[:limite]
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
        return max(0, dias)
    
    def get_duracion_dias(self):
        """Calcula la duración del evento en días"""
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
    class Meta:
        ordering = ['fecha_inicio']

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


# NUEVO: Categoría de Artesanías (también flexible)
class CategoriaArtesania(TimeStampedModel):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase CSS del icono (ej: fas fa-pottery)")
    orden = models.PositiveSmallIntegerField(default=0, help_text="Orden de visualización")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('turismo:artesanias_categoria', kwargs={'slug': self.slug})
    
    class Meta:
        verbose_name = "Categoría de Artesanía"
        verbose_name_plural = "Categorías de Artesanías"
        ordering = ['orden', 'nombre']


class Artesania(TimeStampedModel):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    # CAMBIO: Ahora usa la categoría flexible
    categoria = models.ForeignKey(CategoriaArtesania, on_delete=models.CASCADE, related_name='artesanias')
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


# NUEVO: Categoría de Actividades Físicas (flexible)
class CategoriaActividadFisica(TimeStampedModel):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase CSS del icono (ej: fas fa-hiking)")
    color_tema = models.CharField(max_length=7, blank=True, help_text="Color hexadecimal para esta categoría")
    orden = models.PositiveSmallIntegerField(default=0, help_text="Orden de visualización")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('turismo:actividades_categoria', kwargs={'slug': self.slug})
    
    def get_total_actividades(self):
        """Retorna el total de actividades en esta categoría"""
        return self.actividades.filter(disponible=True).count()
    
    class Meta:
        verbose_name = "Categoría de Actividad Física"
        verbose_name_plural = "Categorías de Actividades Físicas"
        ordering = ['orden', 'nombre']


class ActividadFisica(TimeStampedModel):
    DIFICULTAD_CHOICES = (
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto'),
    )
    
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    # CAMBIO: Ahora usa la categoría flexible
    categoria = models.ForeignKey(CategoriaActividadFisica, on_delete=models.CASCADE, related_name='actividades')
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
    
    # NUEVO: Campos adicionales para flexibilidad
    nivel_riesgo = models.CharField(
        max_length=20,
        choices=(
            ('bajo', 'Bajo'),
            ('medio', 'Medio'),
            ('alto', 'Alto'),
        ),
        default='bajo',
        help_text="Nivel de riesgo de la actividad"
    )
    requiere_reserva = models.BooleanField(default=False)
    disponible_todo_año = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"
    
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
    
    def get_color_riesgo(self):
        """Retorna color CSS basado en el nivel de riesgo"""
        colors = {
            'bajo': 'success',
            'medio': 'warning',
            'alto': 'danger'
        }
        return colors.get(self.nivel_riesgo, 'primary')
    
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
    
    def get_coordenadas_dict(self):
        """Retorna las coordenadas como diccionario para usar en mapas"""
        if self.tiene_coordenadas():
            return {
                'lat': float(self.latitud),
                'lng': float(self.longitud),
                'nombre': self.nombre,
                'categoria': self.categoria.nombre,
                'dificultad': self.get_dificultad_display(),
                'url': self.get_absolute_url(),
                'imagen': self.imagen_principal.url if self.imagen_principal else None
            }
        return None
    
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