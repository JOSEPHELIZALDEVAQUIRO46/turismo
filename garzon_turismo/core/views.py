# core/views.py

from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404, render
from .models import PaginaEstatica, Testimonio, Banner, ConfiguracionSitio
from turismo.models import LugarTuristico, Evento, Establecimiento, Ruta
from blog.models import Post

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración del sitio
        try:
            context['config'] = ConfiguracionSitio.objects.first()
        except:
            pass
        
        # Banners activos
        context['banners'] = Banner.objects.filter(activo=True).order_by('orden')
        
        # Lugares turísticos destacados
        context['lugares_destacados'] = LugarTuristico.objects.filter(
            destacado=True
        )[:6]
        
        # Eventos próximos
        from django.utils import timezone
        context['eventos_proximos'] = Evento.objects.filter(
            fecha_inicio__gte=timezone.now(),
            destacado=True
        ).order_by('fecha_inicio')[:3]
        
        # Establecimientos destacados
        context['establecimientos_destacados'] = Establecimiento.objects.filter(
            destacado=True
        )[:4]
        
        # Posts recientes
        context['posts_recientes'] = Post.objects.filter(
            publicado=True
        ).order_by('-fecha_publicacion')[:3]
        
        # Rutas destacadas
        context['rutas'] = Ruta.objects.all()[:2]
        
        # Testimonios
        context['testimonios'] = Testimonio.objects.filter(activo=True)
        
        # Datos para mapa
        lugares_mapa = LugarTuristico.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        )[:20]  # Limitar a 20 para no sobrecargar el mapa inicial
        
        # Preparar datos de marcadores para el mapa
        import json
        marcadores = []
        
        for lugar in lugares_mapa:
            marcadores.append({
                'nombre': lugar.nombre,
                'latitud': lugar.latitud,
                'longitud': lugar.longitud,
                'categoria': lugar.categoria.nombre,
                'imagen': lugar.imagen_principal.url if lugar.imagen_principal else '',
                'url': lugar.get_absolute_url()
            })
        
        context['marcadores_json'] = json.dumps(marcadores)
        
        return context

class PaginaEstaticaView(DetailView):
    model = PaginaEstatica
    template_name = 'core/pagina_estatica.html'
    context_object_name = 'pagina'

class AcercaDeView(TemplateView):
    template_name = 'core/acerca_de.html'

class TerminosCondicionesView(TemplateView):
    template_name = 'core/terminos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ConfiguracionSitio.objects.first()
        if config:
            context['terminos_texto'] = config.texto_terminos
        return context

class PoliticaPrivacidadView(TemplateView):
    template_name = 'core/privacidad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = ConfiguracionSitio.objects.first()
        if config:
            context['privacidad_texto'] = config.texto_privacidad
        return context

def error_404(request, exception):
    return render(request, 'core/404.html', status=404)

def error_500(request):
    return render(request, 'core/500.html', status=500)