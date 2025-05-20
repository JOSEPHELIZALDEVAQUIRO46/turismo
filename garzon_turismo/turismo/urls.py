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
]