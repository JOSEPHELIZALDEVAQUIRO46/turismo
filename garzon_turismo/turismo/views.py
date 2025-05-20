# turismo/views.py

from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, 
    PuntoRuta, Establecimiento, Evento
)
from .forms import (
    ValoracionForm, ComentarioForm, 
    FiltroEstablecimientoForm, FiltroEventoForm
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