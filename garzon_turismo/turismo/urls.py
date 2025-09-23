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
   
    # Rutas turísticas (ACTUALIZADAS con mapas)
    path('rutas/', views.RutaListView.as_view(), name='ruta_list'),
    path('ruta/<slug:slug>/', views.RutaDetailView.as_view(), name='ruta_detail'),
    path('ruta/<slug:slug>/mapa/', views.RutaMapaView.as_view(), name='ruta_mapa'),  # NUEVO: Mapa independiente
   
    # Búsqueda (ACTUALIZADA)
    path('buscar/', views.TurismoSearchViewActualizada.as_view(), name='turismo_search'),
   
    # Mapa general (ACTUALIZADO)
    path('mapa/', views.MapaGeneralActualizadoView.as_view(), name='mapa'),
   
    # Galería
    path('galeria/', views.GaleriaView.as_view(), name='galeria'),
   
    # URLs para Transporte
    path('transporte/', views.TransporteListView.as_view(), name='transporte_list'),
    path('transporte/<slug:slug>/', views.TransporteDetailView.as_view(), name='transporte_detail'),
    path('transporte/tipo/<str:tipo>/', views.TransportePorTipoListView.as_view(), name='transporte_por_tipo'),
   
    # URLs para Artesanías (ACTUALIZADAS con categorías dinámicas)
    path('artesanias/', views.ArtesaniaListView.as_view(), name='artesanias_list'),
    path('artesania/<slug:slug>/', views.ArtesaniaDetailView.as_view(), name='artesania_detail'),
    path('artesanias/categoria/<slug:slug>/', views.ArtesaniaPorCategoriaListView.as_view(), name='artesanias_por_categoria'),  # Ahora usa slug
    path('artesanias/artesano/<str:artesano>/', views.ArtesaniaPorArtesanoListView.as_view(), name='artesanias_por_artesano'),
   
    # URLs para Actividades Físicas (ACTUALIZADAS con categorías dinámicas)
    path('actividades-fisicas/', views.ActividadFisicaListView.as_view(), name='actividades_fisicas_list'),
    path('actividad-fisica/<slug:slug>/', views.ActividadFisicaDetailView.as_view(), name='actividad_fisica_detail'),
    path('actividades-fisicas/categoria/<slug:slug>/', views.ActividadPorCategoriaListView.as_view(), name='actividades_por_categoria'),  # NUEVO
    path('actividades-fisicas/dificultad/<str:dificultad>/', views.ActividadPorDificultadListView.as_view(), name='actividades_por_dificultad'),
   
    # ========== APIs PARA MAPAS Y FUNCIONALIDAD AVANZADA ==========
    
    # APIs para mapas de rutas
    path('api/ruta/<slug:slug>/coordenadas/', views.api_ruta_coordenadas, name='api_ruta_coordenadas'),
    path('api/ruta/<slug:ruta_slug>/punto/<int:punto_id>/', views.api_punto_ruta_detalle, name='api_punto_ruta_detalle'),
    path('api/rutas/con-mapas/', views.api_rutas_con_mapas, name='api_rutas_con_mapas'),
    path('api/rutas/comparar/', views.api_comparar_rutas, name='api_comparar_rutas'),
    path('api/rutas/validar-coordenadas/', views.validar_coordenadas_ruta, name='validar_coordenadas_ruta'),
   
    # APIs para datos dinámicos
    path('api/transporte/', views.api_transporte_list, name='api_transporte_list'),
    path('api/artesanias/', views.api_artesanias_list, name='api_artesanias_list'),
    path('api/actividades/', views.api_actividades_list, name='api_actividades_list'),
   
    # API para búsqueda rápida en tiempo real
    path('api/busqueda-rapida/', views.api_busqueda_rapida, name='api_busqueda_rapida'),
    
    # ========== URLs ADMINISTRATIVAS (OPCIONALES) ==========
    
    # Administración de mapas de rutas
    path('admin/ruta/<slug:slug>/mapa/', views.RutaMapaAdminView.as_view(), name='ruta_mapa_admin'),
    
    # Estadísticas de mapas
    path('admin/mapas/estadisticas/', views.MapaEstadisticasView.as_view(), name='mapa_estadisticas'),
    
    # ========== URLs PARA CATEGORÍAS DINÁMICAS ==========
    
    # Categorías de artesanías
    path('artesanias/categorias/', views.CategoriaArtesaniaListView.as_view(), name='categorias_artesanias'),
    
    # Categorías de actividades físicas
    path('actividades-fisicas/categorias/', views.CategoriaActividadFisicaListView.as_view(), name='categorias_actividades'),

     # ========== URLs PARA GALERÍA FOTOGRÁFICA ==========
    
    # Galería principal
    path('galeria/', views.GaleriaFotograficaView.as_view(), name='galeria'),
    
    # Detalle de fotografía
    path('galeria/foto/<slug:slug>/', views.FotografiaDetailView.as_view(), name='fotografia_detail'),
    
    # Fotografías por categoría
    path('galeria/categoria/<slug:slug>/', views.GaleriaCategoriaView.as_view(), name='galeria_categoria'),
    
    # Fotografías por tag
    path('galeria/tag/<slug:slug>/', views.GaleriaTagView.as_view(), name='galeria_tag'),
    
    # Fotografías por fotógrafo
    path('galeria/fotografo/<str:fotografo>/', views.GaleriaFotografoView.as_view(), name='galeria_fotografo'),
    
    # ========== APIs PARA GALERÍA ==========
    
    # API de fotografías con filtros
    path('api/galeria/fotografias/', views.api_galeria_fotografias, name='api_galeria_fotografias'),
    
    # API de categorías
    path('api/galeria/categorias/', views.api_galeria_categorias, name='api_galeria_categorias'),
    
    # API de búsqueda rápida
    path('api/galeria/busqueda/', views.api_galeria_busqueda, name='api_galeria_busqueda'),
   
]   