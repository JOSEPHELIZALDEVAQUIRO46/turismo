# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('acerca-de/', views.AcercaDeView.as_view(), name='acerca_de'),
    path('terminos-y-condiciones/', views.TerminosCondicionesView.as_view(), name='terminos'),
    path('politica-privacidad/', views.PoliticaPrivacidadView.as_view(), name='privacidad'),
    path('pagina/<slug:slug>/', views.PaginaEstaticaView.as_view(), name='pagina_estatica'),
]