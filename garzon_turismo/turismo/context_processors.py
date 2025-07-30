# turismo/context_processors.py

from django.utils import timezone
from .models import (
    LugarTuristico, Ruta, Establecimiento, Evento,
    Transporte, Artesania, ActividadFisica, Categoria
)

def contadores_turismo(request):
    """
    Context processor que proporciona contadores dinámicos para usar en templates
    """
    try:
        return {
            'contadores': {
                # Contadores principales para la sección de rutas turísticas
                'rutas': Ruta.objects.count(),
                'destinos': LugarTuristico.objects.count(),
                'experiencias': ActividadFisica.objects.filter(disponible=True).count(),
                
                # Contadores adicionales
                'lugares_turisticos': LugarTuristico.objects.count(),
                'lugares_destacados': LugarTuristico.objects.filter(destacado=True).count(),
                'establecimientos': Establecimiento.objects.count(),
                'eventos': Evento.objects.count(),
                'eventos_activos': Evento.objects.filter(
                    fecha_fin__gte=timezone.now()
                ).count(),
                'transportes': Transporte.objects.filter(disponible=True).count(),
                'artesanias': Artesania.objects.filter(disponible_venta=True).count(),
                'actividades_fisicas': ActividadFisica.objects.filter(disponible=True).count(),
                'categorias': Categoria.objects.count(),
                
                # Contadores por tipo de establecimiento
                'hoteles': Establecimiento.objects.filter(tipo='hotel').count(),
                'restaurantes': Establecimiento.objects.filter(tipo='restaurante').count(),
                'cafeterias': Establecimiento.objects.filter(tipo='cafe').count(),
                'bares': Establecimiento.objects.filter(tipo='bar').count(),
                
                # Contadores por tipo de transporte
                'buses': Transporte.objects.filter(tipo='bus', disponible=True).count(),
                'taxis': Transporte.objects.filter(tipo='taxi', disponible=True).count(),
                'tours': Transporte.objects.filter(tipo='tour', disponible=True).count(),
                
                # Contadores por categoría de artesanías
                'ceramicas': Artesania.objects.filter(categoria='ceramica', disponible_venta=True).count(),
                'textiles': Artesania.objects.filter(categoria='textil', disponible_venta=True).count(),
                'maderas': Artesania.objects.filter(categoria='madera', disponible_venta=True).count(),
                
                # Contadores por tipo de actividad física
                'senderismo': ActividadFisica.objects.filter(tipo_actividad='senderismo', disponible=True).count(),
                'ciclismo': ActividadFisica.objects.filter(tipo_actividad='ciclismo', disponible=True).count(),
                'escalada': ActividadFisica.objects.filter(tipo_actividad='escalada', disponible=True).count(),
                
                # Contadores por dificultad de rutas
                'rutas_faciles': Ruta.objects.filter(dificultad='facil').count(),
                'rutas_medias': Ruta.objects.filter(dificultad='media').count(),
                'rutas_dificiles': Ruta.objects.filter(dificultad='dificil').count(),
            }
        }
    except Exception as e:
        # En caso de error, devolver contadores en 0
        return {
            'contadores': {
                'rutas': 0,
                'destinos': 0,
                'experiencias': 0,
                'lugares_turisticos': 0,
                'establecimientos': 0,
                'eventos': 0,
                'transportes': 0,
                'artesanias': 0,
                'actividades_fisicas': 0,
            }
        }