from .models import ConfiguracionSitio, PaginaEstatica

def configuracion_sitio(request):
    """
    Agrega la configuración del sitio al contexto de todas las plantillas
    """
    try:
        config = ConfiguracionSitio.objects.first()
    except:
        config = None
    
    paginas_menu = PaginaEstatica.objects.filter(en_menu=True).order_by('orden_menu')
    
    return {
        'config': config,
        'paginas_menu': paginas_menu
    }