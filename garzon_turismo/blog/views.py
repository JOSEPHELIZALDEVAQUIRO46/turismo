from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Post, CategoriaBlog

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(publicado=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaBlog.objects.all()
        return context

class PostCategoriaListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(
            categorias__slug=self.kwargs['slug'],
            publicado=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaBlog.objects.all()
        context['categoria_actual'] = CategoriaBlog.objects.get(slug=self.kwargs['slug'])
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(publicado=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener posts relacionados basados en categorías
        context['posts_relacionados'] = Post.objects.filter(
            categorias__in=self.object.categorias.all(),
            publicado=True
        ).exclude(id=self.object.id).distinct()[:3]
        return context

class PostSearchView(ListView):
    model = Post
    template_name = 'blog/post_search.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Post.objects.filter(
                Q(titulo__icontains=query) | 
                Q(contenido__icontains=query),
                publicado=True
            ).distinct()
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context