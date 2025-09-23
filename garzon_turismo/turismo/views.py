# turismo/views.py - PARTE 1

from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import json

from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, 
    PuntoRuta, Establecimiento, Evento,
    Transporte, Artesania, ActividadFisica,
    CategoriaArtesania, CategoriaActividadFisica,
    ImagenArtesania, ImagenActividadFisica,  Fotografia, CategoriaFotografia, TagFotografia, FotografiaTag
)
from .forms import (
    ValoracionForm, ComentarioForm, 
    FiltroEstablecimientoForm, FiltroEventoForm,
    TransporteFiltroForm, ArtesaniaFiltroForm, ActividadFisicaFiltroForm,
    BusquedaAvanzadaForm
)

# ========== VISTAS PARA LUGARES TURÍSTICOS ==========

class LugarTuristicoListView(ListView):
    model = LugarTuristico
    template_name = 'turismo/lugar_list.html'
    context_object_name = 'lugares'
    paginate_by = 12
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context

class LugarTuristicoCategoriaListView(ListView):
    model = LugarTuristico
    template_name = 'turismo/lugar_list.html'
    context_object_name = 'lugares'
    paginate_by = 12
    
    def get_queryset(self):
        return LugarTuristico.objects.filter(categoria__slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_actual'] = Categoria.objects.get(slug=self.kwargs['slug'])
        return context

class LugarTuristicoDetailView(DetailView):
    model = LugarTuristico
    template_name = 'turismo/lugar_detail.html'
    context_object_name = 'lugar'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Establecimientos cercanos (podría mejorarse con geolocalización)
        context['establecimientos_cercanos'] = Establecimiento.objects.filter(
            destacado=True
        )[:4]
        
        # Lugares relacionados de la misma categoría
        context['lugares_relacionados'] = LugarTuristico.objects.filter(
            categoria=self.object.categoria
        ).exclude(id=self.object.id)[:4]
        
        # Rutas que incluyen este lugar
        context['rutas_relacionadas'] = Ruta.objects.filter(
            puntos__lugar_turistico=self.object
        ).distinct()
        
        # Imágenes del lugar
        context['imagenes'] = self.object.imagenes.all()
        
        # Formulario de comentarios si se implementa
        context['comentario_form'] = ComentarioForm()
        
        return context

# ========== VISTAS PARA ESTABLECIMIENTOS ==========

class EstablecimientoListView(ListView):
    model = Establecimiento
    template_name = 'turismo/establecimiento_list.html'
    context_object_name = 'establecimientos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Establecimiento.objects.all()
        
        # Filtrar por tipo si se especifica
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por rango de precios
        rango_precios = self.request.GET.get('rango_precios')
        if rango_precios:
            queryset = queryset.filter(rango_precios=rango_precios)
        
        # Filtrar por servicios (búsqueda parcial)
        servicios = self.request.GET.get('servicios')
        if servicios:
            # Divide los servicios por comas y busca cada uno
            servicios_list = [s.strip() for s in servicios.split(',')]
            q_objects = Q()
            for servicio in servicios_list:
                q_objects |= Q(servicios__icontains=servicio)
            queryset = queryset.filter(q_objects)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = dict(Establecimiento.TIPO_CHOICES)
        context['rangos_precios'] = dict(Establecimiento.RANGO_PRECIOS_CHOICES)
        
        # Formulario de filtro con valores actuales
        form = FiltroEstablecimientoForm(self.request.GET)
        context['filtro_form'] = form
        
        return context

class EstablecimientoTipoListView(ListView):
    model = Establecimiento
    template_name = 'turismo/establecimiento_list.html'
    context_object_name = 'establecimientos'
    paginate_by = 12
    
    def get_queryset(self):
        return Establecimiento.objects.filter(tipo=self.kwargs['tipo'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = dict(Establecimiento.TIPO_CHOICES)
        context['rangos_precios'] = dict(Establecimiento.RANGO_PRECIOS_CHOICES)
        context['tipo_actual'] = self.kwargs['tipo']
        context['tipo_actual_nombre'] = dict(Establecimiento.TIPO_CHOICES).get(self.kwargs['tipo'])
        
        # Formulario de filtro con tipo preseleccionado
        initial = {'tipo': self.kwargs['tipo']}
        form = FiltroEstablecimientoForm(initial=initial)
        context['filtro_form'] = form
        
        return context

class EstablecimientoDetailView(DetailView):
    model = Establecimiento
    template_name = 'turismo/establecimiento_detail.html'
    context_object_name = 'establecimiento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Valoración media usando el método del modelo
        context['valoracion_media'] = self.object.get_valoracion_promedio()
        
        # Formulario de valoración
        context['form_valoracion'] = ValoracionForm()
        
        # Lugares turísticos cercanos
        context['lugares_cercanos'] = self.object.get_lugares_cercanos()
        
        # Establecimientos similares
        context['establecimientos_similares'] = Establecimiento.objects.filter(
            tipo=self.object.tipo
        ).exclude(id=self.object.id)[:3]
        
        return context

class EstablecimientoValorarView(FormView):
    template_name = 'turismo/valoracion_form.html'
    form_class = ValoracionForm
    
    def form_valid(self, form):
        establecimiento = get_object_or_404(Establecimiento, slug=self.kwargs['slug'])
        valoracion = form.save(commit=False)
        valoracion.establecimiento = establecimiento
        valoracion.save()
        
        messages.success(self.request, 'Tu valoración ha sido enviada y está pendiente de aprobación. ¡Gracias por compartir tu opinión!')
        
        return redirect('turismo:establecimiento_detail', slug=establecimiento.slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimiento'] = get_object_or_404(Establecimiento, slug=self.kwargs['slug'])
        return context

# ========== VISTAS PARA EVENTOS ==========

class EventoListView(ListView):
    model = Evento
    template_name = 'turismo/evento_list.html'
    context_object_name = 'eventos'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Evento.objects.all()
        
        # Filtrar por fechas
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_hasta)
        
        return queryset.order_by('fecha_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de filtro con valores actuales
        form = FiltroEventoForm(self.request.GET)
        context['filtro_form'] = form
        
        # Eventos destacados
        context['eventos_destacados'] = Evento.objects.filter(
            destacado=True
        )[:3]
        
        return context

class EventoDetailView(DetailView):
    model = Evento
    template_name = 'turismo/evento_detail.html'
    context_object_name = 'evento'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Eventos relacionados (próximos eventos)
        context['eventos_relacionados'] = Evento.objects.filter(
            fecha_inicio__gte=timezone.now()
        ).exclude(id=self.object.id).order_by('fecha_inicio')[:3]
        
        return context

# ========== VISTAS PARA RUTAS (ACTUALIZADAS CON MAPAS) ==========

class RutaListView(ListView):
    model = Ruta
    template_name = 'turismo/ruta_list.html'
    context_object_name = 'rutas'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dificultades'] = dict(Ruta.DIFICULTAD_CHOICES)
        
        # Estadísticas de rutas
        context['stats'] = {
            'total_rutas': Ruta.objects.count(),
            'rutas_con_puntos': Ruta.objects.filter(puntos__isnull=False).distinct().count(),
        }
        
        return context

class RutaDetailView(DetailView):
    """Vista del detalle de ruta con mapa integrado"""
    model = Ruta
    template_name = 'turismo/ruta_detail.html'
    context_object_name = 'ruta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Puntos de la ruta ordenados
        puntos_ordenados = self.object.get_puntos_ordenados()
        context['puntos'] = puntos_ordenados
        
        # ===== CONFIGURACIÓN COMPLETA DEL MAPA =====
        # Usar los nuevos métodos del modelo
        mapa_config = self.object.get_configuracion_mapa()
        context['mapa_config'] = json.dumps(mapa_config)
        
        # Centro del mapa calculado automáticamente
        context['centro_mapa'] = json.dumps(self.object.get_centro_mapa())
        
        # Bounds para ajustar automáticamente el zoom
        bounds = self.object.get_bounds_mapa()
        if bounds:
            context['mapa_bounds'] = json.dumps(bounds)
        
        # ===== INFORMACIÓN ADICIONAL PARA EL TEMPLATE =====
        
        # Estadísticas de la ruta
        context['estadisticas'] = {
            'total_puntos': puntos_ordenados.count(),
            'puntos_con_lugares': puntos_ordenados.filter(lugar_turistico__isnull=False).count(),
            'tiene_coordenadas': self.object.tiene_puntos(),
            'primer_punto': self.object.get_primer_punto(),
            'ultimo_punto': self.object.get_ultimo_punto(),
        }
        
        # Lugares turísticos únicos en esta ruta
        lugares_en_ruta = self.object.get_lugares_turisticos()
        context['lugares_en_ruta'] = lugares_en_ruta
        context['total_lugares_unicos'] = lugares_en_ruta.count()
        
        # Rutas similares (misma dificultad, excluyendo la actual)
        context['rutas_similares'] = Ruta.objects.filter(
            dificultad=self.object.dificultad
        ).exclude(id=self.object.id)[:3]
        
        # ===== DATOS PARA COMPARTIR Y SEO =====
        
        # URL del mapa independiente
        context['url_mapa_independiente'] = reverse(
            'turismo:ruta_mapa', 
            kwargs={'slug': self.object.slug}
        )
        
        # Metadatos para compartir en redes sociales
        if puntos_ordenados.exists():
            context['meta_description'] = (
                f"Ruta {self.object.nombre} - {puntos_ordenados.count()} puntos de interés. "
                f"Dificultad: {self.object.get_dificultad_display()}. "
                f"Distancia: {self.object.distancia} km. "
                f"Duración: {self.object.duracion_estimada}."
            )
        
        # ===== CONFIGURACIÓN ADICIONAL DEL MAPA =====
        
        # Determinar si mostrar controles avanzados
        context['mostrar_controles_avanzados'] = puntos_ordenados.count() > 3
        
        # Preparar datos para exportación (GPX, KML, etc.)
        context['datos_exportacion'] = {
            'formato_gpx': True,
            'formato_kml': True,
            'total_coordenadas': puntos_ordenados.count(),
        }
        
        # ===== INTERACTIVIDAD =====
        
        # Verificar si el usuario puede editar (para futuros features admin)
        context['puede_editar'] = (
            self.request.user.is_authenticated and 
            (self.request.user.is_staff or self.request.user.is_superuser)
        )
        
        # URLs de API para interactividad
        context['api_urls'] = {
            'coordenadas': reverse('turismo:api_ruta_coordenadas', kwargs={'slug': self.object.slug}),
            'validar_coordenadas': reverse('turismo:validar_coordenadas_ruta'),
        }
        
        return context

class RutaMapaView(DetailView):
    """Vista específica para mostrar el mapa de una ruta individual"""
    model = Ruta
    template_name = 'turismo/ruta_mapa.html'
    context_object_name = 'ruta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración completa del mapa para esta ruta específica
        config_mapa = self.object.get_configuracion_mapa()
        context['mapa_config'] = json.dumps(config_mapa)
        
        # Información básica de la ruta para el template
        context['total_puntos'] = self.object.puntos.count()
        context['primer_punto'] = self.object.get_primer_punto()
        context['ultimo_punto'] = self.object.get_ultimo_punto()
        
        # Bounds del mapa para ajuste automático
        bounds = self.object.get_bounds_mapa()
        if bounds:
            context['mapa_bounds'] = json.dumps(bounds)
        
        return context

# ========== VISTAS PARA TRANSPORTE ==========

class TransporteListView(ListView):
    model = Transporte
    template_name = 'turismo/transporte/list.html'
    context_object_name = 'transportes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Transporte.objects.filter(disponible=True).order_by('-destacado', 'nombre')
        
        # Filtrar por tipo si se especifica
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por origen
        origen = self.request.GET.get('origen')
        if origen:
            queryset = queryset.filter(origen__icontains=origen)
        
        # Filtrar por destino
        destino = self.request.GET.get('destino')
        if destino:
            queryset = queryset.filter(destino__icontains=destino)
        
        # Búsqueda general
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(origen__icontains=search) |
                Q(destino__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de filtro con valores actuales
        form = TransporteFiltroForm(self.request.GET)
        context['filtro_form'] = form
        
        # Transportes destacados
        context['transportes_destacados'] = Transporte.objects.filter(
            destacado=True, disponible=True
        )[:6]
        
        # Tipos de transporte para filtros
        context['tipos_transporte'] = dict(Transporte.TIPO_TRANSPORTE_CHOICES)
        
        # Query actual para mantener en paginación
        context['search'] = self.request.GET.get('search', '')
        
        return context

class TransporteDetailView(DetailView):
    model = Transporte
    template_name = 'turismo/transporte/detail.html'
    context_object_name = 'transporte'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Transportes relacionados (mismo tipo o misma ruta)
        context['transportes_relacionados'] = Transporte.objects.filter(
            Q(tipo=self.object.tipo) | 
            Q(origen=self.object.origen) | 
            Q(destino=self.object.destino)
        ).exclude(id=self.object.id).filter(disponible=True)[:4]
        
        return context

class TransportePorTipoListView(ListView):
    model = Transporte
    template_name = 'turismo/transporte/por_tipo.html'
    context_object_name = 'transportes'
    paginate_by = 12
    
    def get_queryset(self):
        return Transporte.objects.filter(
            tipo=self.kwargs['tipo'], 
            disponible=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.kwargs['tipo']
        context['tipo_display'] = dict(Transporte.TIPO_TRANSPORTE_CHOICES).get(
            self.kwargs['tipo'], self.kwargs['tipo']
        )
        return context

# ========== VISTAS PARA ARTESANÍAS (ACTUALIZADAS CON CATEGORÍAS DINÁMICAS) ==========

class ArtesaniaListView(ListView):
    model = Artesania
    template_name = 'turismo/artesanias/list.html'
    context_object_name = 'artesanias'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Artesania.objects.filter(disponible_venta=True).order_by('-destacado', 'nombre')
        
        # Filtrar por categoría (usando pk ahora)
        categoria = self.request.GET.get('categoria')
        if categoria:
            try:
                categoria_id = int(categoria)
                queryset = queryset.filter(categoria_id=categoria_id)
            except ValueError:
                pass
        
        # Filtrar por lugar de origen
        lugar_origen = self.request.GET.get('lugar_origen')
        if lugar_origen:
            queryset = queryset.filter(lugar_origen__icontains=lugar_origen)
        
        # Búsqueda general
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(artesano__icontains=search) |
                Q(lugar_origen__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de filtro
        form = ArtesaniaFiltroForm(self.request.GET)
        context['filtro_form'] = form
        
        # Artesanías destacadas
        context['artesanias_destacadas'] = Artesania.objects.filter(
            destacado=True, disponible_venta=True
        )[:6]
        
        # Categorías disponibles
        context['categorias'] = CategoriaArtesania.objects.all()
        
        # Lugares de origen únicos
        context['lugares_origen'] = Artesania.objects.values_list(
            'lugar_origen', flat=True
        ).distinct()
        
        # Query actual
        context['search'] = self.request.GET.get('search', '')
        
        return context

class ArtesaniaDetailView(DetailView):
    model = Artesania
    template_name = 'turismo/artesanias/detail.html'
    context_object_name = 'artesania'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Artesanías relacionadas (misma categoría o mismo artesano)
        context['artesanias_relacionadas'] = Artesania.objects.filter(
            Q(categoria=self.object.categoria) | Q(artesano=self.object.artesano)
        ).exclude(id=self.object.id).filter(disponible_venta=True)[:4]
        
        # Galería de imágenes
        context['imagenes'] = self.object.imagenes.all()
        
        return context

class ArtesaniaPorCategoriaListView(ListView):
    model = Artesania
    template_name = 'turismo/artesanias/por_categoria.html'
    context_object_name = 'artesanias'
    paginate_by = 12
    
    def get_queryset(self):
        categoria = get_object_or_404(CategoriaArtesania, slug=self.kwargs['slug'])
        return Artesania.objects.filter(
            categoria=categoria, 
            disponible_venta=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CategoriaArtesania, slug=self.kwargs['slug'])
        return context

class ArtesaniaPorArtesanoListView(ListView):
    model = Artesania
    template_name = 'turismo/artesanias/por_artesano.html'
    context_object_name = 'artesanias'
    paginate_by = 12
    
    def get_queryset(self):
        return Artesania.objects.filter(
            artesano__icontains=self.kwargs['artesano'], 
            disponible_venta=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artesano'] = self.kwargs['artesano']
        return context

class CategoriaArtesaniaListView(ListView):
    model = CategoriaArtesania
    template_name = 'turismo/artesanias/categorias.html'
    context_object_name = 'categorias'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de artesanías por categoría
        for categoria in context['categorias']:
            categoria.total_artesanias = categoria.artesanias.filter(disponible_venta=True).count()
        return context

# ========== VISTAS PARA ACTIVIDADES FÍSICAS (ACTUALIZADAS CON CATEGORÍAS DINÁMICAS) ==========

class ActividadFisicaListView(ListView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/list.html'
    context_object_name = 'actividades'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ActividadFisica.objects.filter(disponible=True).order_by('-destacado', 'nombre')
        
        # Filtrar por categoría (usando pk ahora)
        categoria = self.request.GET.get('categoria')
        if categoria:
            try:
                categoria_id = int(categoria)
                queryset = queryset.filter(categoria_id=categoria_id)
            except ValueError:
                pass
        
        # Filtrar por dificultad
        dificultad = self.request.GET.get('dificultad')
        if dificultad:
            queryset = queryset.filter(dificultad=dificultad)
        
        # Filtrar por edad mínima
        edad_minima = self.request.GET.get('edad_minima')
        if edad_minima:
            try:
                edad = int(edad_minima)
                queryset = queryset.filter(edad_minima__lte=edad)
            except ValueError:
                pass
        
        # Búsqueda general
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(ubicacion__icontains=search) |
                Q(instructor_guia__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de filtro
        form = ActividadFisicaFiltroForm(self.request.GET)
        context['filtro_form'] = form
        
        # Actividades destacadas
        context['actividades_destacadas'] = ActividadFisica.objects.filter(
            destacado=True, disponible=True
        )[:6]
        
        # Opciones para filtros
        context['categorias'] = CategoriaActividadFisica.objects.all()
        context['dificultad_choices'] = dict(ActividadFisica.DIFICULTAD_CHOICES)
        
        # Query actual
        context['search'] = self.request.GET.get('search', '')
        
        return context

class ActividadFisicaDetailView(DetailView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/detail.html'
    context_object_name = 'actividad'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Actividades relacionadas (misma categoría o misma dificultad)
        context['actividades_relacionadas'] = ActividadFisica.objects.filter(
            Q(categoria=self.object.categoria) | 
            Q(dificultad=self.object.dificultad)
        ).exclude(id=self.object.id).filter(disponible=True)[:4]
        
        # Galería de imágenes
        context['imagenes'] = self.object.imagenes.all()
        
        # Preparar coordenadas para mapa si existen
        if self.object.tiene_coordenadas():
            context['coordenadas_json'] = json.dumps({
                'lat': float(self.object.latitud),
                'lng': float(self.object.longitud),
                'nombre': self.object.nombre
            })
        
        return context

class ActividadPorCategoriaListView(ListView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/por_categoria.html'
    context_object_name = 'actividades'
    paginate_by = 12
    
    def get_queryset(self):
        categoria = get_object_or_404(CategoriaActividadFisica, slug=self.kwargs['slug'])
        return ActividadFisica.objects.filter(
            categoria=categoria, 
            disponible=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CategoriaActividadFisica, slug=self.kwargs['slug'])
        return context

class ActividadPorDificultadListView(ListView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/por_dificultad.html'
    context_object_name = 'actividades'
    paginate_by = 12
    
    def get_queryset(self):
        return ActividadFisica.objects.filter(
            dificultad=self.kwargs['dificultad'], 
            disponible=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dificultad'] = self.kwargs['dificultad']
        context['dificultad_display'] = dict(ActividadFisica.DIFICULTAD_CHOICES).get(
            self.kwargs['dificultad'], self.kwargs['dificultad']
        )
        return context

class CategoriaActividadFisicaListView(ListView):
    model = CategoriaActividadFisica
    template_name = 'turismo/actividades_fisicas/categorias.html'
    context_object_name = 'categorias'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de actividades por categoría
        for categoria in context['categorias']:
            categoria.total_actividades = categoria.actividades.filter(disponible=True).count()
        return context

# ========== VISTAS GENERALES ACTUALIZADAS ==========

class TurismoSearchViewActualizada(ListView):
    """Búsqueda actualizada que incluye todos los nuevos modelos"""
    template_name = 'turismo/turismo_search.html'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return []
        
        # Buscar en lugares turísticos
        lugares = LugarTuristico.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Buscar en establecimientos
        establecimientos = Establecimiento.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(servicios__icontains=query)
        )
        
        # Buscar en eventos
        eventos = Evento.objects.filter(
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(lugar__icontains=query)
        )
        
        # Buscar en rutas
        rutas = Ruta.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Buscar en transportes
        transportes = Transporte.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
            Q(origen__icontains=query) | Q(destino__icontains=query),
            disponible=True
        )
        
        # Buscar en artesanías
        artesanias = Artesania.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
            Q(artesano__icontains=query) | Q(lugar_origen__icontains=query),
            disponible_venta=True
        )
        
        # Buscar en actividades físicas
        actividades = ActividadFisica.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
            Q(ubicacion__icontains=query) | Q(instructor_guia__icontains=query),
            disponible=True
        )
        
        # Combinar resultados (guardar tipo para mostrar en plantilla)
        resultados = []
        
        for lugar in lugares:
            resultados.append({
                'tipo': 'lugar',
                'objeto': lugar,
                'nombre': lugar.nombre,
                'descripcion': lugar.descripcion,
                'imagen': lugar.imagen_principal,
                'url': lugar.get_absolute_url(),
                'categoria': lugar.categoria.nombre
            })
        
        for estab in establecimientos:
            resultados.append({
                'tipo': 'establecimiento',
                'objeto': estab,
                'nombre': estab.nombre,
                'descripcion': estab.descripcion,
                'imagen': estab.imagen,
                'url': estab.get_absolute_url(),
                'categoria': estab.get_tipo_display()
            })
        
        for evento in eventos:
            resultados.append({
                'tipo': 'evento',
                'objeto': evento,
                'nombre': evento.titulo,
                'descripcion': evento.descripcion,
                'imagen': evento.imagen,
                'url': evento.get_absolute_url(),
                'categoria': 'Evento'
            })
        
        for ruta in rutas:
            resultados.append({
                'tipo': 'ruta',
                'objeto': ruta,
                'nombre': ruta.nombre,
                'descripcion': ruta.descripcion,
                'imagen': ruta.imagen_principal,
                'url': ruta.get_absolute_url(),
                'categoria': f"Ruta ({ruta.get_dificultad_display()})"
            })
        
        for transporte in transportes:
            resultados.append({
                'tipo': 'transporte',
                'objeto': transporte,
                'nombre': transporte.nombre,
                'descripcion': transporte.descripcion,
                'imagen': transporte.imagen,
                'url': transporte.get_absolute_url(),
                'categoria': f"Transporte ({transporte.get_tipo_display()})"
            })
        
        for artesania in artesanias:
            resultados.append({
                'tipo': 'artesania',
                'objeto': artesania,
                'nombre': artesania.nombre,
                'descripcion': artesania.descripcion,
                'imagen': artesania.imagen_principal,
                'url': artesania.get_absolute_url(),
                'categoria': f"Artesanía ({artesania.categoria.nombre})"
            })
        
        for actividad in actividades:
            resultados.append({
                'tipo': 'actividad',
                'objeto': actividad,
                'nombre': actividad.nombre,
                'descripcion': actividad.descripcion,
                'imagen': actividad.imagen_principal,
                'url': actividad.get_absolute_url(),
                'categoria': f"Actividad ({actividad.categoria.nombre})"
            })
        
        return resultados
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class MapaGeneralActualizadoView(TemplateView):
    template_name = 'turismo/mapa_general.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Preparar datos para el mapa
        marcadores = []
        
        # Lugares turísticos con coordenadas
        lugares = LugarTuristico.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )
        
        for lugar in lugares:
            marcadores.append({
                'tipo': 'lugar',
                'nombre': lugar.nombre,
                'categoria': lugar.categoria.nombre,
                'latitud': float(lugar.latitud),
                'longitud': float(lugar.longitud),
                'imagen': lugar.imagen_principal.url if lugar.imagen_principal else None,
                'url': lugar.get_absolute_url(),
                'icon': 'place'
            })
        
        # Actividades físicas con coordenadas
        actividades = ActividadFisica.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False,
            disponible=True
        )
        
        for actividad in actividades:
            marcadores.append({
                'tipo': 'actividad',
                'nombre': actividad.nombre,
                'categoria': actividad.categoria.nombre,
                'latitud': float(actividad.latitud),
                'longitud': float(actividad.longitud),
                'imagen': actividad.imagen_principal.url if actividad.imagen_principal else None,
                'url': actividad.get_absolute_url(),
                'icon': 'fitness_center',
                'dificultad': actividad.dificultad
            })
        
        # Establecimientos con coordenadas
        establecimientos = Establecimiento.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )
        
        for estab in establecimientos:
            marcadores.append({
                'tipo': 'establecimiento',
                'nombre': estab.nombre,
                'categoria': estab.get_tipo_display(),
                'latitud': float(estab.latitud),
                'longitud': float(estab.longitud),
                'imagen': estab.imagen.url if estab.imagen else None,
                'url': estab.get_absolute_url(),
                'icon': 'business'
            })
        
        context['marcadores_json'] = json.dumps(marcadores)
        context['total_marcadores'] = len(marcadores)
        
        return context

class GaleriaView(ListView):
    template_name = 'turismo/galeria.html'
    model = Imagen
    context_object_name = 'imagenes'
    paginate_by = 20
    
    def get_queryset(self):
        return Imagen.objects.all().order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context

# ========== VISTA DE BÚSQUEDA ORIGINAL (COMPATIBILIDAD) ==========

class TurismoSearchView(ListView):
    """Vista de búsqueda original - mantenida para compatibilidad"""
    template_name = 'turismo/turismo_search.html'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return []
        
        # Buscar en lugares turísticos
        lugares = LugarTuristico.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Buscar en establecimientos
        establecimientos = Establecimiento.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(servicios__icontains=query)
        )
        
        # Buscar en eventos
        eventos = Evento.objects.filter(
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(lugar__icontains=query)
        )
        
        # Buscar en rutas
        rutas = Ruta.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Combinar resultados (guardar tipo para mostrar en plantilla)
        resultados = []
        
        for lugar in lugares:
            resultados.append({
                'tipo': 'lugar',
                'objeto': lugar,
                'nombre': lugar.nombre,
                'descripcion': lugar.descripcion,
                'imagen': lugar.imagen_principal,
                'url': lugar.get_absolute_url(),
                'categoria': lugar.categoria.nombre
            })
        
        for estab in establecimientos:
            resultados.append({
                'tipo': 'establecimiento',
                'objeto': estab,
                'nombre': estab.nombre,
                'descripcion': estab.descripcion,
                'imagen': estab.imagen,
                'url': estab.get_absolute_url(),
                'categoria': estab.get_tipo_display()
            })
        
        for evento in eventos:
            resultados.append({
                'tipo': 'evento',
                'objeto': evento,
                'nombre': evento.titulo,
                'descripcion': evento.descripcion,
                'imagen': evento.imagen,
                'url': evento.get_absolute_url(),
                'categoria': 'Evento'
            })
        
        for ruta in rutas:
            resultados.append({
                'tipo': 'ruta',
                'objeto': ruta,
                'nombre': ruta.nombre,
                'descripcion': ruta.descripcion,
                'imagen': ruta.imagen_principal,
                'url': ruta.get_absolute_url(),
                'categoria': f"Ruta ({ruta.get_dificultad_display()})"
            })
        
        return resultados
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

# ========== VISTA MAPA GENERAL ORIGINAL (COMPATIBILIDAD) ==========

class MapaGeneralView(TemplateView):
    """Vista del mapa general original - mantenida para compatibilidad"""
    template_name = 'turismo/mapa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lugares turísticos con coordenadas
        lugares = LugarTuristico.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )
        
        # Establecimientos con coordenadas
        establecimientos = Establecimiento.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )
        
        # Preparar datos para el mapa
        marcadores = []
        
        for lugar in lugares:
            marcadores.append({
                'tipo': 'lugar',
                'nombre': lugar.nombre,
                'categoria': lugar.categoria.nombre,
                'latitud': lugar.latitud,
                'longitud': lugar.longitud,
                'imagen': lugar.imagen_principal.url if lugar.imagen_principal else None,
                'url': lugar.get_absolute_url()
            })
        
        for estab in establecimientos:
            marcadores.append({
                'tipo': 'establecimiento',
                'nombre': estab.nombre,
                'categoria': estab.get_tipo_display(),
                'latitud': estab.latitud,
                'longitud': estab.longitud,
                'imagen': estab.imagen.url if estab.imagen else None,
                'url': estab.get_absolute_url()
            })
        
        context['marcadores_json'] = json.dumps(marcadores)
        context['categorias'] = Categoria.objects.all()
        context['tipos_establecimiento'] = dict(Establecimiento.TIPO_CHOICES)
        
        return context
    #(APIs y Funciones adicionales)

# ========== APIs PARA MAPAS Y FUNCIONALIDAD AVANZADA ==========

def api_ruta_coordenadas(request, slug):
    """API que retorna las coordenadas de una ruta específica en formato JSON"""
    try:
        ruta = get_object_or_404(Ruta, slug=slug)
        
        # Obtener configuración completa del mapa
        config_mapa = ruta.get_configuracion_mapa()
        
        return JsonResponse({
            'success': True,
            'ruta': {
                'id': ruta.id,
                'nombre': ruta.nombre,
                'slug': ruta.slug,
                'dificultad': ruta.dificultad,
                'distancia': float(ruta.distancia),
                'duracion_estimada': ruta.duracion_estimada,
            },
            'mapa': config_mapa,
            'centro': ruta.get_centro_mapa(),
            'bounds': ruta.get_bounds_mapa(),
        })
        
    except Ruta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ruta no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def api_punto_ruta_detalle(request, ruta_slug, punto_id):
    """API para obtener detalles de un punto específico de una ruta"""
    try:
        ruta = get_object_or_404(Ruta, slug=ruta_slug)
        punto = get_object_or_404(PuntoRuta, id=punto_id, ruta=ruta)
        
        # Información completa del punto
        punto_info = punto.get_info_marcador()
        
        # Si tiene lugar turístico asociado, agregar más información
        if punto.lugar_turistico:
            lugar = punto.lugar_turistico
            punto_info.update({
                'lugar_turistico_detalle': {
                    'horario': lugar.horario,
                    'costo_entrada': lugar.costo_entrada,
                    'categoria_nombre': lugar.categoria.nombre,
                    'total_imagenes': lugar.imagenes.count(),
                }
            })
        
        return JsonResponse({
            'success': True,
            'punto': punto_info,
            'ruta': {
                'nombre': ruta.nombre,
                'slug': ruta.slug,
            }
        })
        
    except (Ruta.DoesNotExist, PuntoRuta.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Punto o ruta no encontrada'
        }, status=404)

def api_rutas_con_mapas(request):
    """API que lista todas las rutas que tienen puntos con coordenadas"""
    rutas_con_mapas = []
    
    # Obtener rutas que tienen al menos un punto
    rutas = Ruta.objects.filter(puntos__isnull=False).distinct()
    
    for ruta in rutas:
        if ruta.tiene_puntos():
            rutas_con_mapas.append({
                'id': ruta.id,
                'nombre': ruta.nombre,
                'slug': ruta.slug,
                'dificultad': ruta.dificultad,
                'dificultad_display': ruta.get_dificultad_display(),
                'distancia': float(ruta.distancia),
                'duracion_estimada': ruta.duracion_estimada,
                'total_puntos': ruta.puntos.count(),
                'centro_mapa': ruta.get_centro_mapa(),
                'imagen_principal': ruta.imagen_principal.url if ruta.imagen_principal else None,
                'url_detalle': ruta.get_absolute_url(),
                'url_mapa': reverse('turismo:ruta_mapa', kwargs={'slug': ruta.slug}),
            })
    
    return JsonResponse({
        'success': True,
        'rutas': rutas_con_mapas,
        'total': len(rutas_con_mapas)
    })

def api_comparar_rutas(request):
    """API para comparar múltiples rutas en un solo mapa"""
    rutas_ids = request.GET.getlist('rutas[]')
    
    if not rutas_ids:
        return JsonResponse({
            'success': False,
            'error': 'No se especificaron rutas para comparar'
        }, status=400)
    
    try:
        rutas = Ruta.objects.filter(id__in=rutas_ids)
        rutas_data = []
        
        # Colores para diferenciar rutas
        colores_rutas = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        for i, ruta in enumerate(rutas):
            if ruta.tiene_puntos():
                config_mapa = ruta.get_configuracion_mapa()
                # Asignar color único a cada ruta
                config_mapa['color_ruta'] = colores_rutas[i % len(colores_rutas)]
                
                rutas_data.append({
                    'id': ruta.id,
                    'nombre': ruta.nombre,
                    'slug': ruta.slug,
                    'config_mapa': config_mapa,
                    'color': colores_rutas[i % len(colores_rutas)],
                })
        
        # Calcular centro y bounds generales
        todas_coordenadas = []
        for ruta in rutas:
            puntos = ruta.get_puntos_ordenados()
            for punto in puntos:
                todas_coordenadas.append({'lat': punto.latitud, 'lng': punto.longitud})
        
        centro_general = None
        bounds_general = None
        
        if todas_coordenadas:
            # Calcular centro promedio
            centro_lat = sum(coord['lat'] for coord in todas_coordenadas) / len(todas_coordenadas)
            centro_lng = sum(coord['lng'] for coord in todas_coordenadas) / len(todas_coordenadas)
            centro_general = {'lat': centro_lat, 'lng': centro_lng}
            
            # Calcular bounds
            lats = [coord['lat'] for coord in todas_coordenadas]
            lngs = [coord['lng'] for coord in todas_coordenadas]
            bounds_general = {
                'north': max(lats),
                'south': min(lats),
                'east': max(lngs),
                'west': min(lngs)
            }
        
        return JsonResponse({
            'success': True,
            'rutas': rutas_data,
            'centro_general': centro_general,
            'bounds_general': bounds_general,
            'total_rutas': len(rutas_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def validar_coordenadas_ruta(request):
    """API para validar que todas las coordenadas de una ruta sean válidas"""
    ruta_slug = request.GET.get('ruta_slug')
    
    if not ruta_slug:
        return JsonResponse({
            'success': False,
            'error': 'Slug de ruta requerido'
        }, status=400)
    
    try:
        ruta = get_object_or_404(Ruta, slug=ruta_slug)
        puntos_problematicos = []
        
        for punto in ruta.puntos.all():
            problemas = []
            
            # Validar coordenadas
            if punto.latitud is None or punto.longitud is None:
                problemas.append('Coordenadas faltantes')
            elif not (-90 <= punto.latitud <= 90):
                problemas.append('Latitud inválida')
            elif not (-180 <= punto.longitud <= 180):
                problemas.append('Longitud inválida')
            
            # Validar nombre
            if not punto.nombre and not punto.lugar_turistico:
                problemas.append('Nombre faltante')
            
            if problemas:
                puntos_problematicos.append({
                    'id': punto.id,
                    'orden': punto.orden,
                    'nombre': punto.get_nombre_display(),
                    'problemas': problemas
                })
        
        return JsonResponse({
            'success': True,
            'ruta': ruta.nombre,
            'valida': len(puntos_problematicos) == 0,
            'total_puntos': ruta.puntos.count(),
            'puntos_problematicos': puntos_problematicos,
            'total_problemas': len(puntos_problematicos)
        })
        
    except Ruta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ruta no encontrada'
        }, status=404)

# ========== APIs PARA DATOS DINÁMICOS ==========

def api_busqueda_rapida(request):
    """API para búsqueda rápida en tiempo real desde el header"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 3:
        return JsonResponse({
            'lugares': [],
            'transportes': [],
            'artesanias': [],
            'actividades': [],
            'establecimientos': [],
            'eventos': []
        })
    
    # Buscar en lugares turísticos (máximo 3)
    lugares = LugarTuristico.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query)
    )[:3]
    
    lugares_data = [{
        'nombre': lugar.nombre,
        'descripcion': lugar.descripcion,
        'url': lugar.get_absolute_url(),
        'categoria': lugar.categoria.nombre
    } for lugar in lugares]
    
    # Buscar en transportes (máximo 3)
    transportes = Transporte.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
        Q(origen__icontains=query) | Q(destino__icontains=query),
        disponible=True
    )[:3]
    
    transportes_data = [{
        'nombre': transporte.nombre,
        'origen': transporte.origen,
        'destino': transporte.destino,
        'url': transporte.get_absolute_url(),
        'tipo': transporte.get_tipo_display()
    } for transporte in transportes]
    
    # Buscar en artesanías (máximo 3)
    artesanias = Artesania.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
        Q(artesano__icontains=query) | Q(lugar_origen__icontains=query),
        disponible_venta=True
    )[:3]
    
    artesanias_data = [{
        'nombre': artesania.nombre,
        'artesano': artesania.artesano,
        'lugar_origen': artesania.lugar_origen,
        'url': artesania.get_absolute_url(),
        'categoria': artesania.categoria.nombre
    } for artesania in artesanias]
    
    # Buscar en actividades físicas (máximo 3)
    actividades = ActividadFisica.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query) |
        Q(ubicacion__icontains=query) | Q(instructor_guia__icontains=query),
        disponible=True
    )[:3]
    
    actividades_data = [{
        'nombre': actividad.nombre,
        'ubicacion': actividad.ubicacion,
        'dificultad': actividad.get_dificultad_display(),
        'url': actividad.get_absolute_url(),
        'categoria': actividad.categoria.nombre
    } for actividad in actividades]
    
    # Buscar en establecimientos (máximo 2)
    establecimientos = Establecimiento.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query)
    )[:2]
    
    establecimientos_data = [{
        'nombre': establecimiento.nombre,
        'tipo': establecimiento.get_tipo_display(),
        'direccion': establecimiento.direccion,
        'url': establecimiento.get_absolute_url()
    } for establecimiento in establecimientos]
    
    # Buscar en eventos (máximo 2)
    eventos = Evento.objects.filter(
        Q(titulo__icontains=query) | Q(descripcion__icontains=query)
    )[:2]
    
    eventos_data = [{
        'nombre': evento.titulo,
        'fecha': evento.fecha_inicio.strftime('%d/%m/%Y'),
        'lugar': evento.lugar,
        'url': evento.get_absolute_url()
    } for evento in eventos]
    
    return JsonResponse({
        'lugares': lugares_data,
        'transportes': transportes_data,
        'artesanias': artesanias_data,
        'actividades': actividades_data,
        'establecimientos': establecimientos_data,
        'eventos': eventos_data
    })

def api_transporte_list(request):
    """API JSON para lista de transportes"""
    transportes = Transporte.objects.filter(disponible=True).values(
        'id', 'nombre', 'tipo', 'origen', 'destino', 'duracion_estimada', 
        'costo_aproximado', 'slug'
    )
    
    # Filtros opcionales
    tipo = request.GET.get('tipo')
    if tipo:
        transportes = transportes.filter(tipo=tipo)
    
    return JsonResponse({
        'transportes': list(transportes),
        'count': transportes.count()
    })

def api_artesanias_list(request):
    """API JSON para lista de artesanías"""
    artesanias = Artesania.objects.filter(disponible_venta=True).select_related('categoria').values(
        'id', 'nombre', 'categoria__nombre', 'artesano', 'lugar_origen', 
        'precio_referencia', 'slug'
    )
    
    # Filtros opcionales
    categoria = request.GET.get('categoria')
    if categoria:
        try:
            categoria_id = int(categoria)
            artesanias = artesanias.filter(categoria_id=categoria_id)
        except ValueError:
            pass
    
    return JsonResponse({
        'artesanias': list(artesanias),
        'count': artesanias.count()
    })

def api_actividades_list(request):
    """API JSON para lista de actividades físicas"""
    actividades = ActividadFisica.objects.filter(disponible=True).select_related('categoria').values(
        'id', 'nombre', 'categoria__nombre', 'dificultad', 'ubicacion', 
        'duracion', 'costo', 'edad_minima', 'slug'
    )
    
    # Filtros opcionales
    categoria = request.GET.get('categoria')
    if categoria:
        try:
            categoria_id = int(categoria)
            actividades = actividades.filter(categoria_id=categoria_id)
        except ValueError:
            pass
    
    dificultad = request.GET.get('dificultad')
    if dificultad:
        actividades = actividades.filter(dificultad=dificultad)
    
    return JsonResponse({
        'actividades': list(actividades),
        'count': actividades.count()
    })

# ========== VISTAS ADMINISTRATIVAS ==========

class RutaMapaAdminView(DetailView):
    """Vista para administradores para editar configuración de mapas"""
    model = Ruta
    template_name = 'turismo/admin/ruta_mapa_admin.html'
    context_object_name = 'ruta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración actual del mapa
        context['mapa_config_actual'] = json.dumps(
            self.object.get_configuracion_mapa(), 
            indent=2
        )
        
        # Puntos de la ruta con información detallada
        puntos_detalle = []
        for punto in self.object.get_puntos_ordenados():
            puntos_detalle.append({
                'id': punto.id,
                'orden': punto.orden,
                'nombre': punto.get_nombre_display(),
                'latitud': punto.latitud,
                'longitud': punto.longitud,
                'tiene_lugar_turistico': punto.lugar_turistico is not None,
                'mostrar_en_mapa': punto.mostrar_en_mapa,
                'color_marcador': punto.color_marcador,
                'icono_personalizado': punto.icono_personalizado,
            })
        
        context['puntos_detalle'] = puntos_detalle
        context['total_puntos'] = len(puntos_detalle)
        
        # Configuraciones predefinidas
        context['configuraciones_predefinidas'] = [
            {
                'nombre': 'Ruta Senderismo',
                'config': {
                    'zoom': 14,
                    'estilo_marcador': 'numbered',
                    'mostrar_ruta': True,
                    'color_ruta': '#28a745',
                }
            },
            {
                'nombre': 'Ruta Urbana',
                'config': {
                    'zoom': 16,
                    'estilo_marcador': 'colored',
                    'mostrar_ruta': True,
                    'color_ruta': '#007bff',
                }
            },
            {
                'nombre': 'Ruta Aventura',
                'config': {
                    'zoom': 12,
                    'estilo_marcador': 'custom',
                    'mostrar_ruta': True,
                    'color_ruta': '#dc3545',
                }
            }
        ]
        
        return context

class MapaEstadisticasView(TemplateView):
    """Vista para mostrar estadísticas de uso de mapas"""
    template_name = 'turismo/admin/mapa_estadisticas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['stats'] = {
            'total_rutas': Ruta.objects.count(),
            'rutas_con_puntos': Ruta.objects.filter(puntos__isnull=False).distinct().count(),
            'total_puntos': PuntoRuta.objects.count(),
            'puntos_con_lugares': PuntoRuta.objects.filter(lugar_turistico__isnull=False).count(),
            'lugares_con_coordenadas': LugarTuristico.objects.filter(
                latitud__isnull=False, 
                longitud__isnull=False
            ).count(),
            'actividades_con_coordenadas': ActividadFisica.objects.filter(
                latitud__isnull=False, 
                longitud__isnull=False
            ).count(),
        }
        
        # Rutas por dificultad
        context['rutas_por_dificultad'] = list(
            Ruta.objects.values('dificultad').annotate(
                total=Count('id')
            ).order_by('dificultad')
        )
        
        # Puntos por ruta (top 10)
        context['rutas_mas_puntos'] = list(
            Ruta.objects.annotate(
                total_puntos=Count('puntos')
            ).order_by('-total_puntos')[:10].values('nombre', 'total_puntos', 'slug')
        )
        
        return context

# ========== VISTAS ADICIONALES PARA FUNCIONALIDADES EXTRAS ==========

class RutaComparadorView(TemplateView):
    """Vista para comparar múltiples rutas en un mismo mapa"""
    template_name = 'turismo/ruta_comparador.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # IDs de rutas a comparar (desde GET parameters)
        rutas_ids = self.request.GET.getlist('rutas')
        
        if rutas_ids:
            rutas = Ruta.objects.filter(id__in=rutas_ids)
            context['rutas_seleccionadas'] = rutas
            context['rutas_ids'] = json.dumps([int(id) for id in rutas_ids])
        else:
            context['rutas_seleccionadas'] = []
            context['rutas_ids'] = json.dumps([])
        
        # Todas las rutas disponibles para seleccionar
        context['todas_las_rutas'] = Ruta.objects.filter(
            puntos__isnull=False
        ).distinct().values('id', 'nombre', 'slug', 'dificultad')
        
        return context

class ExportarRutaView(DetailView):
    """Vista para exportar datos de una ruta en diferentes formatos"""
    model = Ruta
    
    def get(self, request, *args, **kwargs):
        ruta = self.get_object()
        formato = request.GET.get('formato', 'json')
        
        if formato == 'json':
            return self.exportar_json(ruta)
        elif formato == 'gpx':
            return self.exportar_gpx(ruta)
        elif formato == 'kml':
            return self.exportar_kml(ruta)
        else:
            return JsonResponse({'error': 'Formato no soportado'}, status=400)
    
    def exportar_json(self, ruta):
        """Exportar ruta en formato JSON"""
        data = {
            'ruta': {
                'nombre': ruta.nombre,
                'descripcion': ruta.descripcion,
                'dificultad': ruta.dificultad,
                'distancia': float(ruta.distancia),
                'duracion_estimada': ruta.duracion_estimada,
            },
            'puntos': ruta.get_coordenadas_puntos(),
            'configuracion_mapa': ruta.get_configuracion_mapa(),
            'exportado_en': timezone.now().isoformat(),
        }
        
        response = JsonResponse(data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="ruta_{ruta.slug}.json"'
        return response
    
    def exportar_gpx(self, ruta):
        """Exportar ruta en formato GPX para GPS"""
        # Generar contenido GPX básico
        gpx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Garzón Turismo">
    <trk>
        <name>{ruta.nombre}</name>
        <desc>{ruta.descripcion}</desc>
        <trkseg>
'''
        
        for punto in ruta.get_puntos_ordenados():
            gpx_content += f'''            <trkpt lat="{punto.latitud}" lon="{punto.longitud}">
                <name>{punto.get_nombre_display()}</name>
                <desc>{punto.get_descripcion_display()}</desc>
            </trkpt>
'''
        
        gpx_content += '''        </trkseg>
    </trk>
</gpx>'''
        
        response = HttpResponse(gpx_content, content_type='application/gpx+xml')
        response['Content-Disposition'] = f'attachment; filename="ruta_{ruta.slug}.gpx"'
        return response
    
    def exportar_kml(self, ruta):
        """Exportar ruta en formato KML para Google Earth"""
        # Generar contenido KML básico
        kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>{ruta.nombre}</name>
        <description>{ruta.descripcion}</description>
        <Placemark>
            <name>Ruta {ruta.nombre}</name>
            <LineString>
                <coordinates>
'''
        
        # Agregar coordenadas (formato: longitud,latitud,altitud)
        coordenadas = []
        for punto in ruta.get_puntos_ordenados():
            coordenadas.append(f"{punto.longitud},{punto.latitud},0")
        
        kml_content += "\n".join(coordenadas)
        
        kml_content += '''
                </coordinates>
            </LineString>
        </Placemark>
'''
        
        # Agregar marcadores para cada punto
        for punto in ruta.get_puntos_ordenados():
            kml_content += f'''        <Placemark>
            <name>{punto.get_nombre_display()}</name>
            <description>{punto.get_descripcion_display()}</description>
            <Point>
                <coordinates>{punto.longitud},{punto.latitud},0</coordinates>
            </Point>
        </Placemark>
'''
        
        kml_content += '''    </Document>
</kml>'''
        
        response = HttpResponse(kml_content, content_type='application/vnd.google-earth.kml+xml')
        response['Content-Disposition'] = f'attachment; filename="ruta_{ruta.slug}.kml"'
        return response

# ========== VISTAS PARA ESTADÍSTICAS Y REPORTES ==========

class EstadisticasTurismoView(TemplateView):
    """Vista con estadísticas generales del sitio turístico"""
    template_name = 'turismo/estadisticas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['stats_generales'] = {
            'total_lugares': LugarTuristico.objects.count(),
            'total_establecimientos': Establecimiento.objects.count(),
            'total_rutas': Ruta.objects.count(),
            'total_eventos': Evento.objects.count(),
            'total_transportes': Transporte.objects.filter(disponible=True).count(),
            'total_artesanias': Artesania.objects.filter(disponible_venta=True).count(),
            'total_actividades': ActividadFisica.objects.filter(disponible=True).count(),
        }
        
        # Estadísticas por categorías
        context['stats_categorias'] = {
            'lugares_por_categoria': list(
                Categoria.objects.annotate(
                    total=Count('lugares')
                ).values('nombre', 'total')
            ),
            'establecimientos_por_tipo': list(
                Establecimiento.objects.values('tipo').annotate(
                    total=Count('id')
                )
            ),
            'rutas_por_dificultad': list(
                Ruta.objects.values('dificultad').annotate(
                    total=Count('id')
                )
            ),
        }
        
        # Estadísticas de mapas
        context['stats_mapas'] = {
            'lugares_con_coordenadas': LugarTuristico.objects.filter(
                latitud__isnull=False, longitud__isnull=False
            ).count(),
            'actividades_con_coordenadas': ActividadFisica.objects.filter(
                latitud__isnull=False, longitud__isnull=False
            ).count(),
            'establecimientos_con_coordenadas': Establecimiento.objects.filter(
                latitud__isnull=False, longitud__isnull=False
            ).count(),
            'rutas_con_puntos': Ruta.objects.filter(
                puntos__isnull=False
            ).distinct().count(),
            'total_puntos_ruta': PuntoRuta.objects.count(),
        }
        
        return context

# ========== VISTAS AUXILIARES ==========

def obtener_coordenadas_municipio(request):
    """API para obtener las coordenadas centrales del municipio"""
    # Coordenadas de Garzón, Huila, Colombia
    coordenadas_garzon = {
        'lat': 2.1964,
        'lng': -75.6472,
        'zoom_default': 13,
        'nombre': 'Garzón, Huila'
    }
    
    return JsonResponse(coordenadas_garzon)

def verificar_disponibilidad_mapa(request):
    """API para verificar si los servicios de mapas están disponibles"""
    # Esta función puede expandirse para verificar APIs de Google Maps, etc.
    return JsonResponse({
        'disponible': True,
        'servicio': 'Google Maps',
        'mensaje': 'Servicio de mapas disponible'
    })

# ========== MANEJO DE ERRORES ESPECÍFICOS ==========

def error_404_personalizado(request, exception):
    """Vista personalizada para errores 404 en el módulo de turismo"""
    return render(request, 'turismo/errors/404.html', status=404)

def error_500_personalizado(request):
    """Vista personalizada para errores 500 en el módulo de turismo"""
    return render(request, 'turismo/errors/500.html', status=500)

# ========== VISTAS DE MANTENIMIENTO ==========

class MantenimientoView(TemplateView):
    """Vista para mostrar página de mantenimiento si es necesario"""
    template_name = 'turismo/mantenimiento.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo mostrar si el sitio está en mantenimiento
        # y el usuario no es staff
        if not request.user.is_staff:
            # Aquí podrías verificar una setting de Django
            # como SITIO_EN_MANTENIMIENTO = True
            pass
        return super().dispatch(request, *args, **kwargs)

       # REEMPLAZA tu clase TurismoSearchViewActualizada en turismo/views.py con esta versión:

class TurismoSearchViewActualizada(ListView):
    """Búsqueda actualizada que incluye todos los modelos"""
    template_name = 'turismo/turismo_search.html'
    context_object_name = 'resultados'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return []
        
        resultados = []
        
        # 1. Buscar en LUGARES TURÍSTICOS
        try:
            lugares = LugarTuristico.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query)
            )
            
            for lugar in lugares:
                resultados.append({
                    'tipo': 'lugar',
                    'objeto': lugar,
                    'nombre': lugar.nombre,
                    'descripcion': lugar.descripcion,
                    'imagen': lugar.imagen_principal,
                    'url': lugar.get_absolute_url(),
                    'categoria': lugar.categoria.nombre
                })
        except Exception as e:
            print(f"Error buscando lugares: {e}")
        
        # 2. Buscar en ESTABLECIMIENTOS
        try:
            establecimientos = Establecimiento.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query) | 
                Q(servicios__icontains=query)
            )
            
            for estab in establecimientos:
                resultados.append({
                    'tipo': 'establecimiento',
                    'objeto': estab,
                    'nombre': estab.nombre,
                    'descripcion': estab.descripcion,
                    'imagen': estab.imagen,
                    'url': estab.get_absolute_url(),
                    'categoria': estab.get_tipo_display()
                })
        except Exception as e:
            print(f"Error buscando establecimientos: {e}")
        
        # 3. Buscar en EVENTOS
        try:
            eventos = Evento.objects.filter(
                Q(titulo__icontains=query) | 
                Q(descripcion__icontains=query) | 
                Q(lugar__icontains=query)
            )
            
            for evento in eventos:
                resultados.append({
                    'tipo': 'evento',
                    'objeto': evento,
                    'nombre': evento.titulo,
                    'descripcion': evento.descripcion,
                    'imagen': evento.imagen,
                    'url': evento.get_absolute_url(),
                    'categoria': 'Evento'
                })
        except Exception as e:
            print(f"Error buscando eventos: {e}")
        
        # 4. Buscar en RUTAS
        try:
            rutas = Ruta.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query)
            )
            
            for ruta in rutas:
                resultados.append({
                    'tipo': 'ruta',
                    'objeto': ruta,
                    'nombre': ruta.nombre,
                    'descripcion': ruta.descripcion,
                    'imagen': ruta.imagen_principal,
                    'url': ruta.get_absolute_url(),
                    'categoria': f"Ruta ({ruta.get_dificultad_display()})"
                })
        except Exception as e:
            print(f"Error buscando rutas: {e}")
        
        # 5. Buscar en TRANSPORTES
        try:
            transportes = Transporte.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query) |
                Q(origen__icontains=query) | 
                Q(destino__icontains=query),
                disponible=True
            )
            
            for transporte in transportes:
                resultados.append({
                    'tipo': 'transporte',
                    'objeto': transporte,
                    'nombre': transporte.nombre,
                    'descripcion': transporte.descripcion,
                    'imagen': getattr(transporte, 'imagen', None),
                    'url': transporte.get_absolute_url(),
                    'categoria': f"Transporte ({transporte.get_tipo_display()})"
                })
        except Exception as e:
            print(f"Error buscando transportes: {e}")
        
        # 6. Buscar en ARTESANÍAS
        try:
            artesanias = Artesania.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query) |
                Q(artesano__icontains=query) | 
                Q(lugar_origen__icontains=query),
                disponible_venta=True
            )
            
            for artesania in artesanias:
                categoria_nombre = "Sin categoría"
                if hasattr(artesania, 'categoria') and artesania.categoria:
                    categoria_nombre = artesania.categoria.nombre
                
                resultados.append({
                    'tipo': 'artesania',
                    'objeto': artesania,
                    'nombre': artesania.nombre,
                    'descripcion': artesania.descripcion,
                    'imagen': artesania.imagen_principal,
                    'url': artesania.get_absolute_url(),
                    'categoria': f"Artesanía ({categoria_nombre})"
                })
        except Exception as e:
            print(f"Error buscando artesanías: {e}")
        
        # 7. Buscar en ACTIVIDADES FÍSICAS
        try:
            actividades = ActividadFisica.objects.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query) |
                Q(ubicacion__icontains=query) | 
                Q(instructor_guia__icontains=query),
                disponible=True
            )
            
            for actividad in actividades:
                categoria_nombre = "Sin categoría"
                if hasattr(actividad, 'categoria') and actividad.categoria:
                    categoria_nombre = actividad.categoria.nombre
                
                resultados.append({
                    'tipo': 'actividad',
                    'objeto': actividad,
                    'nombre': actividad.nombre,
                    'descripcion': actividad.descripcion,
                    'imagen': actividad.imagen_principal,
                    'url': actividad.get_absolute_url(),
                    'categoria': f"Actividad ({categoria_nombre})"
                })
        except Exception as e:
            print(f"Error buscando actividades físicas: {e}")
        
        # Debug: mostrar cuántos resultados encontramos por tipo
        tipos_count = {}
        for resultado in resultados:
            tipo = resultado['tipo']
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        print(f"Búsqueda para '{query}': {tipos_count}")
        print(f"Total resultados: {len(resultados)}")
        
        return resultados
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        
        # Contar resultados por tipo
        resultados = context['resultados']
        context['total_resultados'] = len(resultados)
        
        # Agrupar por tipo para los filtros
        tipos_count = {}
        for resultado in resultados:
            tipo = resultado['tipo']
            if tipo not in tipos_count:
                tipos_count[tipo] = 0
            tipos_count[tipo] += 1
        
        context['tipos_count'] = tipos_count
        
        return context
    
    # ========== VISTAS PARA GALERÍA FOTOGRÁFICA ==========

class GaleriaFotograficaView(ListView):
    """Vista principal de la galería fotográfica"""
    model = Fotografia
    template_name = 'turismo/galeria.html'
    context_object_name = 'fotografias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Fotografia.objects.filter(activa=True).select_related('categoria')
        
        # Filtrar por categoría si se especifica
        categoria_slug = self.request.GET.get('categoria')
        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        
        # Filtrar por tag si se especifica
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__tag__slug=tag_slug)
        
        # Búsqueda por título o descripción
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(ubicacion__icontains=search) |
                Q(fotografo__icontains=search)
            )
        
        # Ordenamiento
        orden = self.request.GET.get('orden', 'recientes')
        if orden == 'destacadas':
            queryset = queryset.order_by('-destacada', '-created')
        elif orden == 'populares':
            queryset = queryset.order_by('-vistas', '-created')
        elif orden == 'alfabetico':
            queryset = queryset.order_by('titulo')
        else:  # recientes por defecto
            queryset = queryset.order_by('-created')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Categorías con conteo de fotos
        context['categorias'] = CategoriaFotografia.objects.filter(
            activa=True
        ).annotate(
            total_fotos=Count('fotografias', filter=Q(fotografias__activa=True))
        ).order_by('orden', 'nombre')
        
        # Tags populares
        context['tags_populares'] = TagFotografia.objects.annotate(
            total_fotos=Count('fotografias', filter=Q(fotografias__activa=True))
        ).filter(total_fotos__gt=0).order_by('-total_fotos')[:10]
        
        # Fotografías destacadas para hero
        context['fotografias_destacadas'] = Fotografia.objects.filter(
            destacada=True, activa=True
        ).order_by('-created')[:3]
        
        # Estadísticas generales
        context['stats'] = {
            'total_fotografias': Fotografia.objects.filter(activa=True).count(),
            'total_categorias': CategoriaFotografia.objects.filter(activa=True).count(),
            'total_fotografos': Fotografia.objects.filter(activa=True).values('fotografo').distinct().count(),
        }
        
        # Filtros actuales
        context['filtros_actuales'] = {
            'categoria': self.request.GET.get('categoria', ''),
            'tag': self.request.GET.get('tag', ''),
            'q': self.request.GET.get('q', ''),
            'orden': self.request.GET.get('orden', 'recientes'),
        }
        
        return context


class FotografiaDetailView(DetailView):
    """Vista de detalle de una fotografía"""
    model = Fotografia
    template_name = 'turismo/fotografia_detail.html'
    context_object_name = 'fotografia'
    slug_field = 'slug'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Incrementar vistas
        obj.incrementar_vistas()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fotografías relacionadas
        context['fotografias_relacionadas'] = self.object.get_fotografias_relacionadas()
        
        # Tags de esta fotografía
        context['tags'] = TagFotografia.objects.filter(
            fotografias__fotografia=self.object
        )
        
        # Datos técnicos
        context['datos_tecnicos'] = self.object.get_datos_tecnicos()
        
        # Navegación anterior/siguiente
        categoria_fotos = Fotografia.objects.filter(
            categoria=self.object.categoria,
            activa=True
        ).order_by('id')
        
        try:
            context['foto_anterior'] = categoria_fotos.filter(
                id__lt=self.object.id
            ).last()
        except Fotografia.DoesNotExist:
            context['foto_anterior'] = None
        
        try:
            context['foto_siguiente'] = categoria_fotos.filter(
                id__gt=self.object.id
            ).first()
        except Fotografia.DoesNotExist:
            context['foto_siguiente'] = None
        
        return context


class GaleriaCategoriaView(ListView):
    """Vista de fotografías por categoría"""
    model = Fotografia
    template_name = 'turismo/categoria.html'
    context_object_name = 'fotografias'
    paginate_by = 20
    
    def get_queryset(self):
        self.categoria = get_object_or_404(
            CategoriaFotografia,
            slug=self.kwargs['slug'],
            activa=True
        )
        
        queryset = Fotografia.objects.filter(
            categoria=self.categoria,
            activa=True
        ).select_related('categoria')
        
        # Ordenamiento
        orden = self.request.GET.get('orden', 'recientes')
        if orden == 'destacadas':
            queryset = queryset.order_by('-destacada', '-created')
        elif orden == 'populares':
            queryset = queryset.order_by('-vistas', '-created')
        elif orden == 'alfabetico':
            queryset = queryset.order_by('titulo')
        else:
            queryset = queryset.order_by('-created')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        
        # Otras categorías
        context['otras_categorias'] = CategoriaFotografia.objects.filter(
            activa=True
        ).exclude(id=self.categoria.id).annotate(
            total_fotos=Count('fotografias', filter=Q(fotografias__activa=True))
        ).order_by('orden', 'nombre')
        
        # Filtros actuales
        context['filtros_actuales'] = {
            'orden': self.request.GET.get('orden', 'recientes'),
        }
        
        return context


class GaleriaTagView(ListView):
    """Vista de fotografías por tag"""
    model = Fotografia
    template_name = 'turismo/tag.html'
    context_object_name = 'fotografias'
    paginate_by = 20
    
    def get_queryset(self):
        self.tag = get_object_or_404(TagFotografia, slug=self.kwargs['slug'])
        
        return Fotografia.objects.filter(
            tags__tag=self.tag,
            activa=True
        ).select_related('categoria').order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        
        # Tags relacionados
        context['tags_relacionados'] = TagFotografia.objects.exclude(
            id=self.tag.id
        ).annotate(
            total_fotos=Count('fotografias', filter=Q(fotografias__activa=True))
        ).filter(total_fotos__gt=0).order_by('-total_fotos')[:10]
        
        return context


class GaleriaFotografoView(ListView):
    """Vista de fotografías por fotógrafo"""
    model = Fotografia
    template_name = 'turismo/fotografo.html'
    context_object_name = 'fotografias'
    paginate_by = 20
    
    def get_queryset(self):
        self.fotografo = self.kwargs['fotografo']
        
        return Fotografia.objects.filter(
            fotografo=self.fotografo,
            activa=True
        ).select_related('categoria').order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fotografo'] = self.fotografo
        
        # Estadísticas del fotógrafo
        context['stats_fotografo'] = {
            'total_fotos': self.get_queryset().count(),
            'categorias_cubiertas': self.get_queryset().values('categoria').distinct().count(),
            'total_vistas': self.get_queryset().aggregate(Sum('vistas'))['vistas__sum'] or 0,
        }
        
        # Otros fotógrafos
        context['otros_fotografos'] = Fotografia.objects.filter(
            activa=True
        ).exclude(fotografo='').values('fotografo').annotate(
            total_fotos=Count('id')
        ).order_by('-total_fotos')[:10]
        
        return context


# ========== API PARA GALERÍA ==========

def api_galeria_fotografias(request):
    """API para obtener fotografías con filtros"""
    fotografias = Fotografia.objects.filter(activa=True).select_related('categoria')
    
    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        fotografias = fotografias.filter(categoria__slug=categoria)
    
    tag = request.GET.get('tag')
    if tag:
        fotografias = fotografias.filter(tags__tag__slug=tag)
    
    # Paginación
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    fotografias_page = fotografias[start:end]
    
    # Serializar datos
    data = []
    for foto in fotografias_page:
        data.append({
            'id': foto.id,
            'titulo': foto.titulo,
            'descripcion': foto.descripcion,
            'imagen': foto.get_imagen_url(),
            'categoria': foto.categoria.nombre,
            'categoria_color': foto.categoria.color_tema,
            'fotografo': foto.fotografo,
            'ubicacion': foto.ubicacion,
            'vistas': foto.vistas,
            'destacada': foto.destacada,
            'url': foto.get_absolute_url(),
            'tags': [tag.tag.nombre for tag in foto.tags.all()]
        })
    
    return JsonResponse({
        'fotografias': data,
        'page': page,
        'per_page': per_page,
        'total': fotografias.count(),
        'has_next': end < fotografias.count(),
        'has_prev': page > 1
    })


def api_galeria_categorias(request):
    """API para obtener categorías con conteo"""
    categorias = CategoriaFotografia.objects.filter(activa=True).annotate(
        total_fotos=Count('fotografias', filter=Q(fotografias__activa=True))
    ).order_by('orden', 'nombre')
    
    data = []
    for categoria in categorias:
        data.append({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'slug': categoria.slug,
            'descripcion': categoria.descripcion,
            'icono': categoria.icono,
            'color_tema': categoria.color_tema,
            'total_fotos': categoria.total_fotos
        })
    
    return JsonResponse({'categorias': data})


def api_galeria_busqueda(request):
    """API para búsqueda rápida en la galería"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 3:
        return JsonResponse({'fotografias': []})
    
    fotografias = Fotografia.objects.filter(
        Q(titulo__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(ubicacion__icontains=query) |
        Q(fotografo__icontains=query),
        activa=True
    ).select_related('categoria')[:8]
    
    data = []
    for foto in fotografias:
        data.append({
            'titulo': foto.titulo,
            'categoria': foto.categoria.nombre,
            'fotografo': foto.fotografo,
            'imagen': foto.get_imagen_url(),
            'url': foto.get_absolute_url()
        })
    
    return JsonResponse({'fotografias': data})