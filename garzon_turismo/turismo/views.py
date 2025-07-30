# turismo/views.py

from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, 
    PuntoRuta, Establecimiento, Evento,
    Transporte, Artesania, ActividadFisica
)
from .forms import (
    ValoracionForm, ComentarioForm, 
    FiltroEstablecimientoForm, FiltroEventoForm,
    TransporteFiltroForm, ArtesaniaFiltroForm, ActividadFisicaFiltroForm
)

# Vistas para Lugares Turísticos
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

# Vistas para Establecimientos
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
        # Valoración media
        context['valoracion_media'] = self.object.valoraciones.filter(
            aprobado=True
        ).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        
        # Valoraciones aprobadas
        context['valoraciones'] = self.object.valoraciones.filter(aprobado=True)
        
        # Formulario de valoración
        context['form_valoracion'] = ValoracionForm()
        
        # Lugares turísticos cercanos (podría mejorarse con geolocalización)
        context['lugares_cercanos'] = LugarTuristico.objects.filter(
            destacado=True
        )[:3]
        
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

# Vistas para Eventos
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
        from django.utils import timezone
        context['eventos_relacionados'] = Evento.objects.filter(
            fecha_inicio__gte=timezone.now()
        ).exclude(id=self.object.id).order_by('fecha_inicio')[:3]
        
        return context

# Vistas para Rutas
class RutaListView(ListView):
    model = Ruta
    template_name = 'turismo/ruta_list.html'
    context_object_name = 'rutas'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dificultades'] = dict(Ruta.DIFICULTAD_CHOICES)
        return context

class RutaDetailView(DetailView):
    model = Ruta
    template_name = 'turismo/ruta_detail.html'
    context_object_name = 'ruta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Puntos de la ruta ordenados
        context['puntos'] = self.object.puntos.all().order_by('orden')
        
        # Preparar datos para el mapa
        import json
        puntos_json = []
        
        for punto in context['puntos']:
            lugar = None
            if punto.lugar_turistico:
                lugar = {
                    'nombre': punto.lugar_turistico.nombre,
                    'slug': punto.lugar_turistico.slug,
                    'imagen': punto.lugar_turistico.imagen_principal.url if punto.lugar_turistico.imagen_principal else None
                }
            
            puntos_json.append({
                'nombre': punto.nombre if punto.nombre else (punto.lugar_turistico.nombre if punto.lugar_turistico else f"Punto {punto.orden}"),
                'descripcion': punto.descripcion,
                'latitud': punto.latitud,
                'longitud': punto.longitud,
                'orden': punto.orden,
                'tiempo_estancia': punto.tiempo_estancia,
                'lugar_turistico': lugar
            })
        
        context['puntos_json'] = json.dumps(puntos_json)
        
        # Rutas similares
        context['rutas_similares'] = Ruta.objects.filter(
            dificultad=self.object.dificultad
        ).exclude(id=self.object.id)[:3]
        
        return context

# Vistas adicionales para mapas y búsqueda
class MapaGeneralView(TemplateView):
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
        import json
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

class TurismoSearchView(ListView):
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

# ========== VISTAS PARA ARTESANÍAS ==========

class ArtesaniaListView(ListView):
    model = Artesania
    template_name = 'turismo/artesanias/list.html'
    context_object_name = 'artesanias'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Artesania.objects.filter(disponible_venta=True).order_by('-destacado', 'nombre')
        
        # Filtrar por categoría
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
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
        context['categoria_choices'] = dict(Artesania.CATEGORIA_CHOICES)
        
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
        return Artesania.objects.filter(
            categoria=self.kwargs['categoria'], 
            disponible_venta=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.kwargs['categoria']
        context['categoria_display'] = dict(Artesania.CATEGORIA_CHOICES).get(
            self.kwargs['categoria'], self.kwargs['categoria']
        )
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

# ========== VISTAS PARA ACTIVIDADES FÍSICAS ==========

class ActividadFisicaListView(ListView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/list.html'
    context_object_name = 'actividades'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ActividadFisica.objects.filter(disponible=True).order_by('-destacado', 'nombre')
        
        # Filtrar por tipo de actividad
        tipo_actividad = self.request.GET.get('tipo_actividad')
        if tipo_actividad:
            queryset = queryset.filter(tipo_actividad=tipo_actividad)
        
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
        context['tipo_choices'] = dict(ActividadFisica.TIPO_ACTIVIDAD_CHOICES)
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
        
        # Actividades relacionadas (mismo tipo o misma dificultad)
        context['actividades_relacionadas'] = ActividadFisica.objects.filter(
            Q(tipo_actividad=self.object.tipo_actividad) | 
            Q(dificultad=self.object.dificultad)
        ).exclude(id=self.object.id).filter(disponible=True)[:4]
        
        # Galería de imágenes
        context['imagenes'] = self.object.imagenes.all()
        
        # Preparar coordenadas para mapa si existen
        if self.object.tiene_coordenadas():
            import json
            context['coordenadas_json'] = json.dumps({
                'lat': float(self.object.latitud),
                'lng': float(self.object.longitud),
                'nombre': self.object.nombre
            })
        
        return context

class ActividadPorTipoListView(ListView):
    model = ActividadFisica
    template_name = 'turismo/actividades_fisicas/por_tipo.html'
    context_object_name = 'actividades'
    paginate_by = 12
    
    def get_queryset(self):
        return ActividadFisica.objects.filter(
            tipo_actividad=self.kwargs['tipo'], 
            disponible=True
        ).order_by('-destacado', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.kwargs['tipo']
        context['tipo_display'] = dict(ActividadFisica.TIPO_ACTIVIDAD_CHOICES).get(
            self.kwargs['tipo'], self.kwargs['tipo']
        )
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

# ========== VISTAS GENERALES ACTUALIZADAS ==========

class TurismoSearchViewActualizada(ListView):
    """Actualización de tu TurismoSearchView existente para incluir los nuevos modelos"""
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
        
        # NUEVAS BÚSQUEDAS EN LOS MODELOS AGREGADOS
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
        
        # AGREGAR LOS NUEVOS RESULTADOS
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
                'categoria': f"Artesanía ({artesania.get_categoria_display()})"
            })
        
        for actividad in actividades:
            resultados.append({
                'tipo': 'actividad',
                'objeto': actividad,
                'nombre': actividad.nombre,
                'descripcion': actividad.descripcion,
                'imagen': actividad.imagen_principal,
                'url': actividad.get_absolute_url(),
                'categoria': f"Actividad ({actividad.get_tipo_actividad_display()})"
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
        import json
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
                'categoria': actividad.get_tipo_actividad_display(),
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

# ========== API PARA BÚSQUEDA RÁPIDA ==========

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
        'categoria': artesania.get_categoria_display()
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
        'tipo': actividad.get_tipo_actividad_display()
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
    
# ========== APIs PARA DATOS DINÁMICOS ==========

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
    artesanias = Artesania.objects.filter(disponible_venta=True).values(
        'id', 'nombre', 'categoria', 'artesano', 'lugar_origen', 
        'precio_referencia', 'slug'
    )
    
    # Filtros opcionales
    categoria = request.GET.get('categoria')
    if categoria:
        artesanias = artesanias.filter(categoria=categoria)
    
    return JsonResponse({
        'artesanias': list(artesanias),
        'count': artesanias.count()
    })

def api_actividades_list(request):
    """API JSON para lista de actividades físicas"""
    actividades = ActividadFisica.objects.filter(disponible=True).values(
        'id', 'nombre', 'tipo_actividad', 'dificultad', 'ubicacion', 
        'duracion', 'costo', 'edad_minima', 'slug'
    )
    
    # Filtros opcionales
    tipo_actividad = request.GET.get('tipo_actividad')
    if tipo_actividad:
        actividades = actividades.filter(tipo_actividad=tipo_actividad)
    
    dificultad = request.GET.get('dificultad')
    if dificultad:
        actividades = actividades.filter(dificultad=dificultad)
    
    return JsonResponse({
        'actividades': list(actividades),
        'count': actividades.count()
    })