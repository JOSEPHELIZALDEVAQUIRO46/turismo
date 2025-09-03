/**
 * home.js - Funcionalidades específicas para la página de inicio
 * Incluye inicialización del mapa de Google Maps para Garzón
 */

// Función para inicializar el mapa de Google Maps
function initHomeMap() {
    const mapElement = document.getElementById('home-map');
    
    if (!mapElement) {
        console.warn('Elemento del mapa no encontrado');
        return;
    }

    // Coordenadas del parque principal de Garzón (Centro del pueblo)
    const garzonCenter = {
        lat: 2.1975, 
        lng: -75.6300
    };

    // Configuración del mapa
    const mapOptions = {
        zoom: 16,
        center: garzonCenter,
        mapTypeId: google.maps.MapTypeId.SATELLITE,
        styles: [
            {
                "featureType": "administrative",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#FFFFFF"}]
            },
            {
                "featureType": "administrative",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#000000"}, {"weight": 2}]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#FFFFFF"}]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#000000"}, {"weight": 2}]
            },
            {
                "featureType": "road",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#FFFFFF"}]
            },
            {
                "featureType": "road",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#000000"}, {"weight": 2}]
            },
            {
                "featureType": "water",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#FFFFFF"}]
            },
            {
                "featureType": "water",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#5DAD47"}, {"weight": 2}]
            }
        ],
        // Controles del mapa
        zoomControl: true,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_CENTER,
            mapTypeIds: [
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.SATELLITE,
                google.maps.MapTypeId.HYBRID,
                google.maps.MapTypeId.TERRAIN
            ]
        },
        scaleControl: true,
        streetViewControl: true,
        rotateControl: false,
        fullscreenControl: true
    };

    try {
        // Crear el mapa
        const map = new google.maps.Map(mapElement, mapOptions);

        // Marcador principal del parque central de Garzón
        const mainMarker = new google.maps.Marker({
            position: garzonCenter,
            map: map,
            title: "Parque Principal de Garzón - Carrera 11",
            icon: {
                url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                scaledSize: new google.maps.Size(40, 40)
            },
            animation: google.maps.Animation.DROP
        });

        // Información del marcador principal
        const infoWindowContent = `
            <div style="max-width: 280px; text-align: center; font-family: Arial, sans-serif;">
                <h6 style="color: #5DAD47; margin-bottom: 8px; font-weight: bold;">
                    <i class="ph-crown" style="margin-right: 5px;"></i>
                    Garzón
                </h6>
                <p style="margin-bottom: 8px; color: #666; font-size: 14px;">
                    <strong>Centro Histórico</strong>
                </p>
                <p style="margin-bottom: 8px; color: #666; font-size: 13px;">
                    Capital Diocesana del Huila
                </p>
                <p style="margin-bottom: 12px; color: #888; font-size: 12px;">
                    Corazón de nuestra hermosa ciudad, rodeado de arquitectura colonial y tradición cafetera
                </p>
                <a href="/turismo/mapa/" style="
                    display: inline-block;
                    background-color: #5DAD47;
                    color: white;
                    padding: 8px 16px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-bottom: 8px;
                ">Ver mapa completo</a>
                <br>
                <small style="color: #999; font-size: 11px;">
                    Vista satelital - Cambia a mapa en los controles superiores
                </small>
            </div>
        `;

        const infoWindow = new google.maps.InfoWindow({
            content: infoWindowContent
        });

        // Evento click para mostrar info
        mainMarker.addListener('click', () => {
            infoWindow.open(map, mainMarker);
        });

        // Mostrar info window automáticamente al cargar
        setTimeout(() => {
            infoWindow.open(map, mainMarker);
        }, 1000);

        // Agregar marcadores adicionales si existen datos
        const marcadoresData = mapElement.getAttribute('data-marcadores');
        if (marcadoresData && marcadoresData !== '[]') {
            try {
                const marcadores = JSON.parse(marcadoresData);
                agregarMarcadoresLugares(map, marcadores);
            } catch (e) {
                console.warn('Error al parsear marcadores:', e);
            }
        }

        // Ocultar el loading
        const loadingElement = mapElement.querySelector('.map-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        console.log('Mapa satelital de Garzón inicializado correctamente en el parque principal');

    } catch (error) {
        console.error('Error al inicializar el mapa:', error);
        mostrarErrorMapa(mapElement);
    }
}

// Función para agregar marcadores de lugares turísticos
function agregarMarcadoresLugares(map, marcadores) {
    marcadores.forEach((lugar, index) => {
        if (lugar.latitud && lugar.longitud) {
            const marker = new google.maps.Marker({
                position: {
                    lat: parseFloat(lugar.latitud),
                    lng: parseFloat(lugar.longitud)
                },
                map: map,
                title: lugar.nombre,
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    scaledSize: new google.maps.Size(28, 28)
                }
            });

            const infoContent = `
                <div style="max-width: 220px; text-align: center;">
                    ${lugar.imagen ? `<img src="${lugar.imagen}" alt="${lugar.nombre}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 4px; margin-bottom: 8px;">` : ''}
                    <h6 style="color: #5DAD47; margin-bottom: 4px; font-weight: bold;">${lugar.nombre}</h6>
                    <p style="color: #666; font-size: 12px; margin-bottom: 8px;">${lugar.categoria || 'Lugar turístico'}</p>
                    ${lugar.url ? `<a href="${lugar.url}" style="color: #5DAD47; font-size: 12px; text-decoration: none; font-weight: bold;">Ver detalles</a>` : ''}
                </div>
            `;

            const infoWindow = new google.maps.InfoWindow({
                content: infoContent
            });

            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
        }
    });
}

// Función para mostrar error si el mapa no carga
function mostrarErrorMapa(mapElement) {
    const loadingElement = mapElement.querySelector('.map-loading');
    if (loadingElement) {
        loadingElement.innerHTML = `
            <div class="text-center">
                <i class="ph-warning-circle text-warning" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h6 class="text-muted">Error al cargar el mapa</h6>
                <p class="text-muted small">Por favor, recarga la página o verifica tu conexión a internet.</p>
                <button onclick="location.reload()" class="btn btn-outline-primary btn-sm">
                    <i class="ph-arrow-clockwise"></i> Recargar
                </button>
            </div>
        `;
    }
}

// Función de respaldo si Google Maps no carga
function googleMapsError() {
    console.error('Error al cargar Google Maps API');
    const mapElement = document.getElementById('home-map');
    if (mapElement) {
        mostrarErrorMapa(mapElement);
    }
}

// Función alternativa para inicializar sin callback
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si Google Maps ya está disponible
    if (typeof google !== 'undefined' && google.maps) {
        initHomeMap();
    } else {
        // Esperar a que Google Maps se cargue
        let attempts = 0;
        const maxAttempts = 50; // 5 segundos máximo
        
        const checkGoogleMaps = setInterval(() => {
            attempts++;
            
            if (typeof google !== 'undefined' && google.maps) {
                clearInterval(checkGoogleMaps);
                initHomeMap();
            } else if (attempts >= maxAttempts) {
                clearInterval(checkGoogleMaps);
                console.warn('Google Maps no se pudo cargar después de 5 segundos');
                googleMapsError();
            }
        }, 100);
    }
});

// Exponer funciones globalmente para callback
window.initHomeMap = initHomeMap;
window.googleMapsError = googleMapsError;

// Función para agregar marcadores de lugares turísticos
function agregarMarcadoresLugares(map, marcadores) {
    marcadores.forEach((lugar, index) => {
        if (lugar.latitud && lugar.longitud) {
            const marker = new google.maps.Marker({
                position: {
                    lat: parseFloat(lugar.latitud),
                    lng: parseFloat(lugar.longitud)
                },
                map: map,
                title: lugar.nombre,
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    scaledSize: new google.maps.Size(24, 24)
                }
            });

            const infoContent = `
                <div style="max-width: 200px; text-align: center;">
                    ${lugar.imagen ? `<img src="${lugar.imagen}" alt="${lugar.nombre}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 4px; margin-bottom: 8px;">` : ''}
                    <h6 style="color: #5DAD47; margin-bottom: 4px;">${lugar.nombre}</h6>
                    <p style="color: #666; font-size: 12px; margin-bottom: 8px;">${lugar.categoria || 'Lugar turístico'}</p>
                    ${lugar.url ? `<a href="${lugar.url}" style="color: #5DAD47; font-size: 12px; text-decoration: none;">Ver detalles</a>` : ''}
                </div>
            `;

            const infoWindow = new google.maps.InfoWindow({
                content: infoContent
            });

            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
        }
    });
}

// Función para mostrar error si el mapa no carga
function mostrarErrorMapa(mapElement) {
    const loadingElement = mapElement.querySelector('.map-loading');
    if (loadingElement) {
        loadingElement.innerHTML = `
            <div class="text-center">
                <i class="ph-warning-circle text-warning" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h6 class="text-muted">Error al cargar el mapa</h6>
                <p class="text-muted small">Por favor, recarga la página o verifica tu conexión a internet.</p>
                <button onclick="location.reload()" class="btn btn-outline-primary btn-sm">
                    <i class="ph-arrow-clockwise"></i> Recargar
                </button>
            </div>
        `;
    }
}

// Función de respaldo si Google Maps no carga
function googleMapsError() {
    console.error('Error al cargar Google Maps API');
    const mapElement = document.getElementById('home-map');
    if (mapElement) {
        mostrarErrorMapa(mapElement);
    }
}

// Función alternativa para inicializar sin callback
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si Google Maps ya está disponible
    if (typeof google !== 'undefined' && google.maps) {
        initHomeMap();
    } else {
        // Esperar a que Google Maps se cargue
        let attempts = 0;
        const maxAttempts = 50; // 5 segundos máximo
        
        const checkGoogleMaps = setInterval(() => {
            attempts++;
            
            if (typeof google !== 'undefined' && google.maps) {
                clearInterval(checkGoogleMaps);
                initHomeMap();
            } else if (attempts >= maxAttempts) {
                clearInterval(checkGoogleMaps);
                console.warn('Google Maps no se pudo cargar después de 5 segundos');
                googleMapsError();
            }
        }, 100);
    }
});

// Exponer funciones globalmente para callback
window.initHomeMap = initHomeMap;
window.googleMapsError = googleMapsError;