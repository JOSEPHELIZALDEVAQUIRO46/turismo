# turismo/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Categoria, LugarTuristico, Imagen, Ruta, PuntoRuta, 
    Establecimiento, Evento, Transporte, Artesania, 
    ActividadFisica, ImagenArtesania, ImagenActividadFisica
)

# ========== HELPER FUNCTIONS ==========

def crear_imagen_prueba(nombre="test.jpg"):
    """Crea una imagen de prueba para los tests"""
    return SimpleUploadedFile(
        nombre,
        b"file_content",
        content_type="image/jpeg"
    )

# ========== TESTS DE MODELOS EXISTENTES ==========

class CategoriaModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Parques Naturales",
            descripcion="Espacios naturales protegidos"
        )
    
    def test_categoria_creation(self):
        """Test que la categoría se crea correctamente"""
        self.assertEqual(self.categoria.nombre, "Parques Naturales")
        self.assertTrue(self.categoria.slug)
        self.assertEqual(self.categoria.slug, "parques-naturales")
    
    def test_str_method(self):
        """Test del método __str__"""
        self.assertEqual(str(self.categoria), "Parques Naturales")
    
    def test_get_absolute_url(self):
        """Test de la URL absoluta"""
        expected_url = reverse('turismo:lugares_categoria', kwargs={'slug': self.categoria.slug})
        self.assertEqual(self.categoria.get_absolute_url(), expected_url)

class LugarTuristicoModelTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Parques")
        self.imagen = crear_imagen_prueba()
        
        self.lugar = LugarTuristico.objects.create(
            nombre="Estrecho del Magdalena",
            categoria=self.categoria,
            descripcion="Punto donde el río se estrecha",
            direccion="San Agustín, Huila",
            imagen_principal=self.imagen,
            latitud=1.8833,
            longitud=-76.2833,
            destacado=True,
            horario="8:00 AM - 5:00 PM",
            costo_entrada="$15.000"
        )
    
    def test_lugar_creation(self):
        """Test que el lugar turístico se crea correctamente"""
        self.assertEqual(self.lugar.nombre, "Estrecho del Magdalena")
        self.assertEqual(self.lugar.categoria, self.categoria)
        self.assertTrue(self.lugar.destacado)
        self.assertTrue(self.lugar.slug)
    
    def test_slug_generation(self):
        """Test que el slug se genera automáticamente"""
        self.assertEqual(self.lugar.slug, "estrecho-del-magdalena")
    
    def test_tiene_coordenadas(self):
        """Test del método tiene_coordenadas"""
        self.assertTrue(self.lugar.tiene_coordenadas())
        
        # Crear lugar sin coordenadas
        lugar_sin_coords = LugarTuristico.objects.create(
            nombre="Lugar sin coordenadas",
            categoria=self.categoria,
            descripcion="Test",
            direccion="Test"
        )
        self.assertFalse(lugar_sin_coords.tiene_coordenadas())
    
    def test_get_imagen_principal_url(self):
        """Test del método get_imagen_principal_url"""
        # Con imagen
        self.assertIn('lugares/', self.lugar.get_imagen_principal_url())
        
        # Sin imagen
        lugar_sin_imagen = LugarTuristico.objects.create(
            nombre="Sin imagen",
            categoria=self.categoria,
            descripcion="Test",
            direccion="Test"
        )
        self.assertEqual(lugar_sin_imagen.get_imagen_principal_url(), '/static/img/placeholder.jpg')

class EstablecimientoModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        self.establecimiento = Establecimiento.objects.create(
            nombre="Hotel Boutique Garzón",
            tipo="hotel",
            descripcion="Hotel acogedor en el centro",
            direccion="Calle 5 # 3-45",
            telefono="3124567890",
            email="info@hotelboutique.com",
            imagen=self.imagen,
            rango_precios="$$",
            servicios="wifi, piscina, desayuno, aire acondicionado",
            destacado=True
        )
    
    def test_establecimiento_creation(self):
        """Test que el establecimiento se crea correctamente"""
        self.assertEqual(self.establecimiento.nombre, "Hotel Boutique Garzón")
        self.assertEqual(self.establecimiento.tipo, "hotel")
        self.assertTrue(self.establecimiento.destacado)
    
    def test_get_servicios_list(self):
        """Test del método get_servicios_list"""
        servicios = self.establecimiento.get_servicios_list()
        expected = ["wifi", "piscina", "desayuno", "aire acondicionado"]
        self.assertEqual(servicios, expected)
    
    def test_str_method(self):
        """Test del método __str__"""
        expected = "Hotel Boutique Garzón (Hotel)"
        self.assertEqual(str(self.establecimiento), expected)

class RutaModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        self.ruta = Ruta.objects.create(
            nombre="Ruta Arqueológica",
            descripcion="Recorrido por sitios arqueológicos",
            duracion_estimada="6 horas",
            distancia=Decimal('15.50'),
            dificultad="media",
            imagen_principal=self.imagen
        )
    
    def test_ruta_creation(self):
        """Test que la ruta se crea correctamente"""
        self.assertEqual(self.ruta.nombre, "Ruta Arqueológica")
        self.assertEqual(self.ruta.dificultad, "media")
        self.assertEqual(self.ruta.distancia, Decimal('15.50'))
    
    def test_get_color_dificultad(self):
        """Test del método get_color_dificultad"""
        self.assertEqual(self.ruta.get_color_dificultad(), "warning")
        
        # Test otros niveles
        ruta_facil = Ruta.objects.create(
            nombre="Ruta Fácil",
            descripcion="Test",
            duracion_estimada="2 horas",
            distancia=Decimal('5.00'),
            dificultad="facil"
        )
        self.assertEqual(ruta_facil.get_color_dificultad(), "success")

class EventoModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        
        # Evento futuro
        fecha_futura = timezone.now() + timedelta(days=30)
        self.evento_futuro = Evento.objects.create(
            titulo="Festival de la Achira",
            descripcion="Celebración tradicional",
            fecha_inicio=fecha_futura,
            fecha_fin=fecha_futura + timedelta(hours=8),
            lugar="Plaza Principal",
            imagen=self.imagen,
            destacado=True
        )
        
        # Evento pasado
        fecha_pasada = timezone.now() - timedelta(days=30)
        self.evento_pasado = Evento.objects.create(
            titulo="Evento Pasado",
            descripcion="Test",
            fecha_inicio=fecha_pasada,
            fecha_fin=fecha_pasada + timedelta(hours=4),
            lugar="Test"
        )
    
    def test_evento_creation(self):
        """Test que el evento se crea correctamente"""
        self.assertEqual(self.evento_futuro.titulo, "Festival de la Achira")
        self.assertTrue(self.evento_futuro.destacado)
    
    def test_ha_pasado(self):
        """Test del método ha_pasado"""
        self.assertFalse(self.evento_futuro.ha_pasado())
        self.assertTrue(self.evento_pasado.ha_pasado())
    
    def test_get_estado_display(self):
        """Test del método get_estado_display"""
        self.assertEqual(self.evento_futuro.get_estado_display(), "Próximamente")
        self.assertEqual(self.evento_pasado.get_estado_display(), "Finalizado")
    
    def test_get_duracion_dias(self):
        """Test del método get_duracion_dias"""
        self.assertEqual(self.evento_futuro.get_duracion_dias(), 1)

# ========== TESTS DE NUEVOS MODELOS ==========

class TransporteModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        self.transporte = Transporte.objects.create(
            nombre="Bus Garzón - San Agustín",
            tipo="bus",
            descripcion="Transporte directo y cómodo",
            origen="Garzón",
            destino="San Agustín",
            duracion_estimada="2 horas",
            costo_aproximado="$15.000",
            contacto="Transportes Unidos",
            telefono="3101234567",
            horarios="Salidas cada 2 horas de 6:00 AM a 6:00 PM",
            imagen=self.imagen,
            destacado=True
        )
    
    def test_transporte_creation(self):
        """Test que el transporte se crea correctamente"""
        self.assertEqual(self.transporte.nombre, "Bus Garzón - San Agustín")
        self.assertEqual(self.transporte.tipo, "bus")
        self.assertEqual(self.transporte.origen, "Garzón")
        self.assertEqual(self.transporte.destino, "San Agustín")
        self.assertTrue(self.transporte.disponible)
        self.assertTrue(self.transporte.destacado)
    
    def test_slug_generation(self):
        """Test que el slug se genera automáticamente"""
        self.assertEqual(self.transporte.slug, "bus-garzon-san-agustin")
    
    def test_str_method(self):
        """Test del método __str__"""
        expected = "Bus Garzón - San Agustín (Autobús)"
        self.assertEqual(str(self.transporte), expected)
    
    def test_get_absolute_url(self):
        """Test de la URL absoluta"""
        expected_url = reverse('turismo:transporte_detail', kwargs={'slug': self.transporte.slug})
        self.assertEqual(self.transporte.get_absolute_url(), expected_url)

class ArtesaniaModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        self.artesania = Artesania.objects.create(
            nombre="Cerámica Tradicional de Pitalito",
            categoria="ceramica",
            descripcion="Pieza única elaborada a mano",
            artesano="María González",
            lugar_origen="Pitalito, Huila",
            tecnica_elaboracion="Moldeado a mano y cocción en horno de leña",
            materiales="Arcilla roja, agua, pigmentos naturales",
            precio_referencia="$85.000",
            tiempo_elaboracion="3 días",
            imagen_principal=self.imagen,
            destacado=True,
            historia="Técnica transmitida por generaciones"
        )
    
    def test_artesania_creation(self):
        """Test que la artesanía se crea correctamente"""
        self.assertEqual(self.artesania.nombre, "Cerámica Tradicional de Pitalito")
        self.assertEqual(self.artesania.categoria, "ceramica")
        self.assertEqual(self.artesania.artesano, "María González")
        self.assertTrue(self.artesania.disponible_venta)
        self.assertTrue(self.artesania.destacado)
    
    def test_get_materiales_list(self):
        """Test del método get_materiales_list"""
        materiales = self.artesania.get_materiales_list()
        expected = ["Arcilla roja", "agua", "pigmentos naturales"]
        self.assertEqual(materiales, expected)
    
    def test_str_method(self):
        """Test del método __str__"""
        expected = "Cerámica Tradicional de Pitalito - María González"
        self.assertEqual(str(self.artesania), expected)
    
    def test_slug_generation(self):
        """Test que el slug se genera automáticamente"""
        self.assertEqual(self.artesania.slug, "ceramica-tradicional-de-pitalito")

class ActividadFisicaModelTest(TestCase):
    def setUp(self):
        self.imagen = crear_imagen_prueba()
        self.actividad = ActividadFisica.objects.create(
            nombre="Senderismo al Estrecho del Magdalena",
            tipo_actividad="senderismo",
            descripcion="Caminata ecológica con guía especializado",
            ubicacion="San Agustín, Huila",
            dificultad="intermedio",
            duracion="4 horas",
            costo="$35.000",
            edad_minima=12,
            capacidad_maxima=15,
            equipamiento_incluido="Bastones de apoyo, agua, snack",
            equipamiento_requerido="Zapatos de senderismo, protector solar, gorra",
            recomendaciones_salud="No recomendado para personas con problemas cardíacos",
            mejor_epoca="Temporada seca (diciembre a marzo)",
            instructor_guia="Carlos Ramírez - Guía certificado",
            contacto="EcoTours Huila",
            telefono="3157894561",
            email="info@ecotourshuila.com",
            imagen_principal=self.imagen,
            latitud=1.8833,
            longitud=-76.2833,
            destacado=True
        )
    
    def test_actividad_creation(self):
        """Test que la actividad física se crea correctamente"""
        self.assertEqual(self.actividad.nombre, "Senderismo al Estrecho del Magdalena")
        self.assertEqual(self.actividad.tipo_actividad, "senderismo")
        self.assertEqual(self.actividad.dificultad, "intermedio")
        self.assertEqual(self.actividad.edad_minima, 12)
        self.assertTrue(self.actividad.disponible)
        self.assertTrue(self.actividad.destacado)
    
    def test_get_color_dificultad(self):
        """Test del método get_color_dificultad"""
        self.assertEqual(self.actividad.get_color_dificultad(), "warning")
        
        # Test otros niveles
        actividad_facil = ActividadFisica.objects.create(
            nombre="Caminata Fácil",
            tipo_actividad="senderismo",
            descripcion="Test",
            ubicacion="Test",
            dificultad="principiante",
            duracion="1 hora"
        )
        self.assertEqual(actividad_facil.get_color_dificultad(), "success")
    
    def test_get_equipamiento_lists(self):
        """Test de los métodos de equipamiento"""
        incluido = self.actividad.get_equipamiento_incluido_list()
        requerido = self.actividad.get_equipamiento_requerido_list()
        
        expected_incluido = ["Bastones de apoyo", "agua", "snack"]
        expected_requerido = ["Zapatos de senderismo", "protector solar", "gorra"]
        
        self.assertEqual(incluido, expected_incluido)
        self.assertEqual(requerido, expected_requerido)
    
    def test_tiene_coordenadas(self):
        """Test del método tiene_coordenadas"""
        self.assertTrue(self.actividad.tiene_coordenadas())
        
        # Actividad sin coordenadas
        actividad_sin_coords = ActividadFisica.objects.create(
            nombre="Sin coordenadas",
            tipo_actividad="otro",
            descripcion="Test",
            ubicacion="Test",
            duracion="1 hora"
        )
        self.assertFalse(actividad_sin_coords.tiene_coordenadas())
    
    def test_es_apta_para_edad(self):
        """Test del método es_apta_para_edad"""
        self.assertTrue(self.actividad.es_apta_para_edad(15))  # Mayor a edad mínima
        self.assertTrue(self.actividad.es_apta_para_edad(12))  # Igual a edad mínima
        self.assertFalse(self.actividad.es_apta_para_edad(10)) # Menor a edad mínima

# ========== TESTS DE VISTAS ==========

class LugarTuristicoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre="Parques")
        self.lugar = LugarTuristico.objects.create(
            nombre="Lugar de Prueba",
            categoria=self.categoria,
            descripcion="Descripción de prueba",
            direccion="Dirección de prueba"
        )
    
    def test_lugar_list_view(self):
        """Test de la vista lista de lugares turísticos"""
        url = reverse('turismo:lugar_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lugar.nombre)
        self.assertIn('lugares', response.context)
    
    def test_lugar_detail_view(self):
        """Test de la vista detalle de lugar turístico"""
        url = reverse('turismo:lugar_detail', kwargs={'slug': self.lugar.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lugar.nombre)
        self.assertEqual(response.context['lugar'], self.lugar)

class EstablecimientoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.establecimiento = Establecimiento.objects.create(
            nombre="Establecimiento de Prueba",
            tipo="hotel",
            descripcion="Descripción de prueba",
            direccion="Dirección de prueba",
            telefono="123456789"
        )
    
    def test_establecimiento_list_view(self):
        """Test de la vista lista de establecimientos"""
        url = reverse('turismo:establecimiento_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.establecimiento.nombre)
    
    def test_establecimiento_detail_view(self):
        """Test de la vista detalle de establecimiento"""
        url = reverse('turismo:establecimiento_detail', kwargs={'slug': self.establecimiento.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.establecimiento.nombre)

class TransporteViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.transporte = Transporte.objects.create(
            nombre="Bus de Prueba",
            tipo="bus",
            descripcion="Descripción de prueba",
            origen="Garzón",
            destino="Neiva",
            duracion_estimada="3 horas"
        )
    
    def test_transporte_list_view(self):
        """Test de la vista lista de transportes"""
        url = reverse('turismo:transporte_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.transporte.nombre)
        self.assertIn('transportes', response.context)
    
    def test_transporte_detail_view(self):
        """Test de la vista detalle de transporte"""
        url = reverse('turismo:transporte_detail', kwargs={'slug': self.transporte.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.transporte.nombre)
    
    def test_transporte_filtro_por_tipo(self):
        """Test del filtro por tipo de transporte"""
        url = reverse('turismo:transporte_list')
        response = self.client.get(url, {'tipo': 'bus'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.transporte.nombre)

class ArtesaniaViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.imagen = crear_imagen_prueba()
        self.artesania = Artesania.objects.create(
            nombre="Artesanía de Prueba",
            categoria="ceramica",
            descripcion="Descripción de prueba",
            artesano="Artesano de Prueba",
            lugar_origen="Pitalito",
            materiales="Arcilla, agua",
            imagen_principal=self.imagen
        )
    
    def test_artesanias_list_view(self):
        """Test de la vista lista de artesanías"""
        url = reverse('turismo:artesanias_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artesania.nombre)
    
    def test_artesania_detail_view(self):
        """Test de la vista detalle de artesanía"""
        url = reverse('turismo:artesania_detail', kwargs={'slug': self.artesania.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artesania.nombre)

class ActividadFisicaViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.imagen = crear_imagen_prueba()
        self.actividad = ActividadFisica.objects.create(
            nombre="Actividad de Prueba",
            tipo_actividad="senderismo",
            descripcion="Descripción de prueba",
            ubicacion="San Agustín",
            dificultad="principiante",
            duracion="2 horas",
            imagen_principal=self.imagen
        )
    
    def test_actividades_list_view(self):
        """Test de la vista lista de actividades físicas"""
        url = reverse('turismo:actividades_fisicas_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.actividad.nombre)
    
    def test_actividad_detail_view(self):
        """Test de la vista detalle de actividad física"""
        url = reverse('turismo:actividad_fisica_detail', kwargs={'slug': self.actividad.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.actividad.nombre)

# ========== TESTS DE BÚSQUEDA ==========

class BusquedaTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear datos de prueba para búsqueda
        categoria = Categoria.objects.create(nombre="Parques")
        self.lugar = LugarTuristico.objects.create(
            nombre="Parque Principal",
            categoria=categoria,
            descripcion="Parque central de la ciudad",
            direccion="Centro"
        )
        
        self.transporte = Transporte.objects.create(
            nombre="Bus Turístico",
            tipo="bus",
            descripcion="Transporte para turistas",
            origen="Garzón",
            destino="San Agustín",
            duracion_estimada="2 horas"
        )
    
    def test_busqueda_general(self):
        """Test de la búsqueda general"""
        url = reverse('turismo:turismo_search')
        response = self.client.get(url, {'q': 'parque'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'parque', case_sensitive=False)
    
    def test_busqueda_sin_query(self):
        """Test de búsqueda sin parámetro de búsqueda"""
        url = reverse('turismo:turismo_search')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

# ========== TESTS DE APIs ==========

class APITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.transporte = Transporte.objects.create(
            nombre="Bus API Test",
            tipo="bus",
            descripcion="Para test de API",
            origen="A",
            destino="B",
            duracion_estimada="1 hora"
        )
    
    def test_api_transporte_list(self):
        """Test de la API de transportes"""
        url = reverse('turismo:api_transporte_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('transportes', data)
        self.assertIn('count', data)
        self.assertGreater(data['count'], 0)
    
    def test_api_artesanias_list(self):
        """Test de la API de artesanías"""
        imagen = crear_imagen_prueba()
        Artesania.objects.create(
            nombre="API Test",
            categoria="ceramica",
            descripcion="Test",
            artesano="Test",
            lugar_origen="Test",
            materiales="Test",
            imagen_principal=imagen
        )
        
        url = reverse('turismo:api_artesanias_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('artesanias', data)
        self.assertIn('count', data)

# ========== TESTS DE INTEGRACIÓN ==========

class IntegracionTest(TestCase):
    """Tests que verifican la interacción entre diferentes componentes"""
    
    def setUp(self):
        self.client = Client()
        
        # Crear datos completos para tests de integración
        self.categoria = Categoria.objects.create(nombre="Aventura")
        
        self.lugar = LugarTuristico.objects.create(
            nombre="Estrecho del Magdalena",
            categoria=self.categoria,
            descripcion="Lugar impresionante",
            direccion="San Agustín",
            latitud=1.8833,
            longitud=-76.2833
        )
        
        imagen = crear_imagen_prueba()
        self.actividad = ActividadFisica.objects.create(
            nombre="Senderismo al Estrecho",
            tipo_actividad="senderismo",
            descripcion="Caminata al estrecho",
            ubicacion="San Agustín",
            dificultad="intermedio",
            duracion="4 horas",
            imagen_principal=imagen,
            latitud=1.8833,
            longitud=-76.2833
        )
    
    def test_flujo_completo_usuario(self):
        """Test que simula el flujo completo de un usuario"""
        # 1. Usuario visita página de lugares
        response = self.client.get(reverse('turismo:lugar_list'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Usuario ve detalle de un lugar
        response = self.client.get(reverse('turismo:lugar_detail', kwargs={'slug': self.lugar.slug}))
        self.assertEqual(response.status_code, 200)
        
        # 3. Usuario busca actividades
        response = self.client.get(reverse('turismo:actividades_fisicas_list'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Usuario ve detalle de actividad
        response = self.client.get(reverse('turismo:actividad_fisica_detail', kwargs={'slug': self.actividad.slug}))
        self.assertEqual(response.status_code, 200)
    
    def test_busqueda_cruzada(self):
        """Test que verifica que la búsqueda encuentre diferentes tipos de contenido"""
        # Buscar por "estrecho" debería encontrar tanto el lugar como la actividad
        response = self.client.get(reverse('turismo:turismo_search'), {'q': 'estrecho'})
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        self.assertIn('Estrecho del Magdalena', content)
        self.assertIn('Senderismo al Estrecho', content)
