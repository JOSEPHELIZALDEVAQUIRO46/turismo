# core/utils.py

import os
from django.utils.text import slugify
from django.utils import timezone

def get_upload_path(instance, filename, base_path):
    """
    Genera una ruta de carga adecuada para un archivo
    con un formato tipo: base_path/año/mes/nombre-slugificado.extension
    """
    now = timezone.now()
    name, ext = os.path.splitext(filename)
    slug_name = slugify(name)
    return os.path.join(
        base_path,
        str(now.year),
        str(now.month),
        f"{slug_name}{ext}".lower()
    )

def truncate_chars(value, max_length):
    """
    Trunca un texto a una longitud específica sin cortar palabras
    """
    if len(value) <= max_length:
        return value
    
    truncd_val = value[:max_length]
    if value[max_length] != ' ':
        truncd_val = truncd_val[:truncd_val.rfind(' ')]
    
    return truncd_val + '...'

def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip