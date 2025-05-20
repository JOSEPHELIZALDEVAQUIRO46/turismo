from django.db import models

from django.db import models
from core.models import TimeStampedModel

class Contacto(TimeStampedModel):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.asunto} - {self.nombre}"
    
    class Meta:
        ordering = ['-created']