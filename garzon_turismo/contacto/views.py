from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Contacto
from .forms import ContactoForm

class ContactoView(FormView):
    template_name = 'contacto/contacto.html'
    form_class = ContactoForm
    success_url = reverse_lazy('contacto:gracias')
    
    def form_valid(self, form):
        # Crear y guardar el objeto Contacto
        Contacto.objects.create(
            nombre=form.cleaned_data['nombre'],
            email=form.cleaned_data['email'],
            asunto=form.cleaned_data['asunto'],
            mensaje=form.cleaned_data['mensaje']
        )
        
        # Añadir mensaje de éxito
        messages.success(self.request, 'Mensaje enviado correctamente. Nos pondremos en contacto contigo pronto.')
        
        return super().form_valid(form)

class ContactoGraciasView(TemplateView):
    template_name = 'contacto/gracias.html'