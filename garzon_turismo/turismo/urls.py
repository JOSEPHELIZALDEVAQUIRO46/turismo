# turismo/urls.py

from django.urls import path
from . import views

app_name = 'turismo'

urlpatterns = [
    # Lugares turísticos
    path('lugares/', views.LugarTuristicoListView.as_view(), name='lugar_list'),
    path('lugares/categoria/<slug:slug>/', views.LugarTuristicoCategoriaListView.as_view(), name='lugares_categoria'),
    path('lugar/<slug:slug>/', views.LugarTuristicoDetailView.as_view(), name='lugar_detail'),
   
    # Establecimientos
    path('establecimientos/', views.EstablecimientoListView.as_view(), name='establecimiento_list'),
    path('establecimientos/tipo/<str:tipo>/', views.EstablecimientoTipoListView.as_view(), name='establecimientos_tipo'),
    path('establecimiento/<slug:slug>/', views.EstablecimientoDetailView.as_view(), name='establecimiento_detail'),
    path('establecimiento/<slug:slug>/valorar/', views.EstablecimientoValorarView.as_view(), name='establecimiento_valorar'),
   
    # Eventos
    path('eventos/', views.EventoListView.as_view(), name='evento_list'),
    path('evento/<slug:slug>/', views.EventoDetailView.as_view(), name='evento_detail'),
   
    # Rutas turísticas
    path('rutas/', views.RutaListView.as_view(), name='ruta_list'),
    path('ruta/<slug:slug>/', views.RutaDetailView.as_view(), name='ruta_detail'),
   
    # Búsqueda
    path('buscar/', views.TurismoSearchView.as_view(), name='turismo_search'),
   
    # Mapa general
    path('mapa/', views.MapaGeneralView.as_view(), name='mapa'),
   
    # Galería
    path('galeria/', views.GaleriaView.as_view(), name='galeria'),
    
    # URLs para Transporte
    path('transporte/', views.TransporteListView.as_view(), name='transporte_list'),
    path('transporte/<slug:slug>/', views.TransporteDetailView.as_view(), name='transporte_detail'),
    path('transporte/tipo/<str:tipo>/', views.TransportePorTipoListView.as_view(), name='transporte_por_tipo'),
    
    # URLs para Artesanías
    path('artesanias/', views.ArtesaniaListView.as_view(), name='artesanias_list'),
    path('artesania/<slug:slug>/', views.ArtesaniaDetailView.as_view(), name='artesania_detail'),
    path('artesanias/categoria/<str:categoria>/', views.ArtesaniaPorCategoriaListView.as_view(), name='artesanias_por_categoria'),
    path('artesanias/artesano/<str:artesano>/', views.ArtesaniaPorArtesanoListView.as_view(), name='artesanias_por_artesano'),
    
    # URLs para Actividades Físicas
    path('actividades-fisicas/', views.ActividadFisicaListView.as_view(), name='actividades_fisicas_list'),
    path('actividad-fisica/<slug:slug>/', views.ActividadFisicaDetailView.as_view(), name='actividad_fisica_detail'),
    path('actividades-fisicas/tipo/<str:tipo>/', views.ActividadPorTipoListView.as_view(), name='actividades_por_tipo'),
    path('actividades-fisicas/dificultad/<str:dificultad>/', views.ActividadPorDificultadListView.as_view(), name='actividades_por_dificultad'),
    
    # APIs para datos dinámicos
    path('api/transporte/', views.api_transporte_list, name='api_transporte_list'),
    path('api/artesanias/', views.api_artesanias_list, name='api_artesanias_list'),
    path('api/actividades/', views.api_actividades_list, name='api_actividades_list'),
    
    # API para búsqueda rápida en tiempo real
    path('api/busqueda-rapida/', views.api_busqueda_rapida, name='api_busqueda_rapida'),
]