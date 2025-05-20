# blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('categoria/<slug:slug>/', views.PostCategoriaListView.as_view(), name='categoria_posts'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('buscar/', views.PostSearchView.as_view(), name='post_search'),
]