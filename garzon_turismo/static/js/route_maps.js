/**
 * ==========================================
 * SISTEMA DE MAPAS PARA RUTAS TURÍSTICAS
 * Archivo: static/js/route_maps.js
 * ==========================================
 */

// Clase principal para manejar los mapas de rutas
class GarzonRouteMaps {
    constructor() {
        this.map = null;
        this.directionsService = null;
        this.directionsRenderer = null;
        this.markers = [];
        this.infoWindows = [];
        this.routePath = null;
        this.bounds = null;
        this.currentRoute = null;
        
        // Colores por tipo de ruta
        this.routeColors = {
            'city-tour-patrimonial': '#8B4513',
            'magica-ancestral': '#9932CC',
            'paraiso-natural': '#228B22',
            'gastronomica': '#FF6347',
            'magica-cafe': '#8B4513'
        };
        
        // Iconos personalizados para marcadores
        this.markerIcons = {
            inicio: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#22C55E',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#FFFFFF'
            },
            fin: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#EF4444',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#FFFFFF'
            },
            punto: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 8,
                fillColor: '#5DAD47',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#FFFFFF'
            },
            lugar: {
                url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            },
            establecimiento: {
                url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
            }
        };
    }

    /**
     * Inicializar mapa para una ruta
     */
    initRouteMap(containerId, routeData) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Contenedor del mapa no encontrado:', containerId);
            return;
        }

        // Mostrar loading
        this.showLoading(container);

        // Guardar datos de la ruta
        this.currentRoute = routeData;

        // Inicializar el mapa
        const mapOptions = {
            zoom: 13,
            center: { lat: 2.1928, lng: -75.6924 }, // Centro de Garzón
            mapTypeId: 'roadmap',
            styles: this.getMapStyles(),
            mapTypeControl: true,
            streetViewControl: false,
            fullscreenControl: false
        };

        this.map = new google.maps.Map(container, mapOptions);
        this.bounds = new google.maps.LatLngBounds();

        // Inicializar servicios de direcciones
        this.directionsService = new google.maps.DirectionsService();
        this.directionsRenderer = new google.maps.DirectionsRenderer({
            map: this.map,
            suppressMarkers: true,
            polylineOptions: {
                strokeColor: this.getRouteColor(),
                strokeOpacity: 0.8,
                strokeWeight: 4
            }
        });

        // Cargar puntos de la ruta
        if (routeData && routeData.puntos && routeData.puntos.length > 0) {
            this.loadRoutePoints(routeData.puntos);
            this.drawRoute(routeData.puntos);
        }

        // Cargar lugares y establecimientos cercanos
        this.loadNearbyPlaces();

        // Agregar controles personalizados
        this.addCustomControls(container);

        // Agregar panel de información
        this.addRouteInfoPanel();
    }

    /**
     * Obtener estilos del mapa
     */
    getMapStyles() {
        return [
            {
                "featureType": "poi",
                "elementType": "labels",
                "stylers": [{ "visibility": "off" }]
            },
            {
                "featureType": "transit",
                "elementType": "labels",
                "stylers": [{ "visibility": "off" }]
            }
        ];
    }

    /**
     * Obtener color de la ruta según el tipo
     */
    getRouteColor() {
        if (!this.currentRoute || !this.currentRoute.tipo) return '#5DAD47';
        return this.routeColors[this.currentRoute.tipo] || '#5DAD47';
    }

    /**
     * Cargar puntos de la ruta
     */
    loadRoutePoints(puntos) {
        puntos.forEach((punto, index) => {
            const position = {
                lat: parseFloat(punto.latitud),
                lng: parseFloat(punto.longitud)
            };

            // Determinar el icono
            let icon;
            if (index === 0) {
                icon = this.markerIcons.inicio;
            } else if (index === puntos.length - 1) {
                icon = this.markerIcons.fin;
            } else {
                icon = this.markerIcons.punto;
            }

            // Crear marcador
            const marker = new google.maps.Marker({
                position: position,
                map: this.map,
                title: punto.nombre,
                icon: icon,
                animation: google.maps.Animation.DROP,
                zIndex: 100 + index
            });

            // Crear ventana de información
            const infoContent = this.createInfoWindowContent(punto, index + 1, puntos.length);
            const infoWindow = new google.maps.InfoWindow({
                content: infoContent,
                maxWidth: 320
            });

            // Evento click en marcador
            marker.addListener('click', () => {
                // Cerrar otras ventanas de información
                this.closeAllInfoWindows();
                // Abrir esta ventana
                infoWindow.open(this.map, marker);
            });

            // Guardar referencias
            this.markers.push(marker);
            this.infoWindows.push(infoWindow);

            // Extender límites del mapa
            this.bounds.extend(position);
        });

        // Ajustar vista del mapa
        this.map.fitBounds(this.bounds);
    }

    /**
     * Crear contenido para ventana de información
     */
    createInfoWindowContent(punto, orden, total) {
        const tipoTexto = orden === 1 ? 'INICIO' : orden === total ? 'FIN' : `Punto ${orden}`;
        
        let content = `
            <div class="custom-info-window">
                <div class="info-header" style="background: linear-gradient(135deg, ${this.getRouteColor()} 0%, ${this.getRouteColor()}dd 100%);">
                    <div class="info-meta">
                        <span class="info-badge">${tipoTexto}</span>
                        <span class="info-coordinates">${punto.latitud.toFixed(4)}, ${punto.longitud.toFixed(4)}</span>
                    </div>
                    <h6>${punto.nombre}</h6>
                </div>
                <div class="info-body">
        `;

        if (punto.descripcion) {
            content += `<p class="info-description">${punto.descripcion}</p>`;
        }

        content += `
                    <div class="info-details">
                        <div class="info-detail-item">
                            <i class="ph-map-pin"></i>
                            <span>Punto ${orden} de ${total}</span>
                        </div>
        `;

        if (punto.tiempo_estancia) {
            content += `
                        <div class="info-detail-item">
                            <i class="ph-clock"></i>
                            <span>Tiempo sugerido: ${punto.tiempo_estancia}</span>
                        </div>
            `;
        }

        content += `
                    </div>
                    <div class="info-actions">
        `;

        if (punto.lugar_turistico) {
            content += `
                        <a href="/turismo/lugar/${punto.lugar_turistico.slug}/" class="info-btn info-btn-primary" target="_blank">
                            Ver detalles
                        </a>
            `;
        }

        content += `
                        <button class="info-btn info-btn-secondary" onclick="garzonMaps.centerOnPoint(${punto.latitud}, ${punto.longitud})">
                            Centrar aquí
                        </button>
                    </div>
                </div>
            </div>
        `;

        return content;
    }

    /**
     * Dibujar la ruta entre los puntos
     */
    drawRoute(puntos) {
        if (puntos.length < 2) return;

        const waypoints = [];
        for (let i = 1; i < puntos.length - 1; i++) {
            waypoints.push({
                location: {
                    lat: parseFloat(puntos[i].latitud),
                    lng: parseFloat(puntos[i].longitud)
                },
                stopover: true
            });
        }

        const request = {
            origin: {
                lat: parseFloat(puntos[0].latitud),
                lng: parseFloat(puntos[0].longitud)
            },
            destination: {
                lat: parseFloat(puntos[puntos.length - 1].latitud),
                lng: parseFloat(puntos[puntos.length - 1].longitud)
            },
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.DRIVING,
            optimizeWaypoints: false
        };

        this.directionsService.route(request, (result, status) => {
            if (status === 'OK') {
                this.directionsRenderer.setDirections(result);
            } else {
                console.warn('No se pudo calcular la ruta:', status);
                // Dibujar línea directa como fallback
                this.drawDirectPath(puntos);
            }
        });
    }

    /**
     * Dibujar ruta directa (fallback)
     */
    drawDirectPath(puntos) {
        const path = puntos.map(punto => ({
            lat: parseFloat(punto.latitud),
            lng: parseFloat(punto.longitud)
        }));

        this.routePath = new google.maps.Polyline({
            path: path,
            geodesic: true,
            strokeColor: this.getRouteColor(),
            strokeOpacity: 0.8,
            strokeWeight: 4,
            map: this.map
        });
    }

    /**
     * Cargar lugares y establecimientos cercanos
     */
    loadNearbyPlaces() {
        // Esta función se puede expandir para cargar datos dinámicamente
        // Por ahora, solo muestra un ejemplo de cómo agregar marcadores adicionales
        
        // Ejemplo: agregar algunos lugares turísticos
        const lugaresEjemplo = [
            {
                nombre: "Catedral San Sebastián",
                tipo: "lugar",
                lat: 2.1950,
                lng: -75.6910,
                categoria: "Patrimonio"
            },
            {
                nombre: "Parque Principal",
                tipo: "lugar",
                lat: 2.1935,
                lng: -75.6925,
                categoria: "Espacio Público"
            }
        ];

        // Agregar marcadores para lugares
        lugaresEjemplo.forEach(lugar => {
            const marker = new google.maps.Marker({
                position: { lat: lugar.lat, lng: lugar.lng },
                map: this.map,
                title: lugar.nombre,
                icon: this.markerIcons.lugar,
                zIndex: 50
            });

            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div class="custom-info-window">
                        <div class="info-header" style="background-color: #2196F3;">
                            <h6>${lugar.nombre}</h6>
                        </div>
                        <div class="info-body">
                            <p class="info-description">Categoría: ${lugar.categoria}</p>
                        </div>
                    </div>
                `
            });

            marker.addListener('click', () => {
                this.closeAllInfoWindows();
                infoWindow.open(this.map, marker);
            });

            this.markers.push(marker);
            this.infoWindows.push(infoWindow);
        });
    }

    /**
     * Agregar controles personalizados
     */
    addCustomControls(container) {
        const controlsHTML = `
            <div class="map-controls">
                <button class="map-control-btn" onclick="garzonMaps.centerRoute()">
                    <i class="ph-crosshair"></i>
                    <span>Centrar Ruta</span>
                </button>
                <button class="map-control-btn" onclick="garzonMaps.toggleMapType()">
                    <i class="ph-globe"></i>
                    <span>Vista Satélite</span>
                </button>
                <button class="map-control-btn" onclick="garzonMaps.toggleFullscreen()">
                    <i class="ph-arrows-out"></i>
                    <span>Pantalla Completa</span>
                </button>
                <button class="map-control-btn" onclick="garzonMaps.downloadGPX()">
                    <i class="ph-download"></i>
                    <span>Descargar GPX</span>
                </button>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', controlsHTML);
    }

    /**
     * Agregar panel de información de la ruta
     */
    addRouteInfoPanel() {
        if (!this.currentRoute) return;

        const panelHTML = `
            <div class="route-info-panel">
                <h6 class="route-info-title">
                    <i class="ph-path"></i>
                    ${this.currentRoute.nombre}
                </h6>
                <div class="route-info-stats">
                    <div class="route-stat-item">
                        <div class="route-stat-icon">📍</div>
                        <span>${this.currentRoute.puntos.length} paradas</span>
                    </div>
                    <div class="route-stat-item">
                        <div class="route-stat-icon">⏱️</div>
                        <span>${this.currentRoute.duracion}</span>
                    </div>
                    <div class="route-stat-item">
                        <div class="route-stat-icon">📏</div>
                        <span>${this.currentRoute.distancia}</span>
                    </div>
                    <div class="route-stat-item">
                        <div class="route-stat-icon">🎯</div>
                        <span>${this.currentRoute.dificultad}</span>
                    </div>
                </div>
            </div>
        `;

        const mapDiv = this.map.getDiv();
        mapDiv.insertAdjacentHTML('afterbegin', panelHTML);
    }

    /**
     * Cerrar todas las ventanas de información
     */
    closeAllInfoWindows() {
        this.infoWindows.forEach(infoWindow => {
            infoWindow.close();
        });
    }

    /**
     * Centrar en un punto específico
     */
    centerOnPoint(lat, lng) {
        this.map.setCenter({ lat: parseFloat(lat), lng: parseFloat(lng) });
        this.map.setZoom(17);
    }

    /**
     * Centrar la ruta completa
     */
    centerRoute() {
        if (this.bounds) {
            this.map.fitBounds(this.bounds);
        }
    }

    /**
     * Alternar tipo de mapa
     */
    toggleMapType() {
        const currentType = this.map.getMapTypeId();
        const newType = currentType === 'roadmap' ? 'satellite' : 'roadmap';
        this.map.setMapTypeId(newType);
        
        // Actualizar texto del botón
        const btn = document.querySelector('.map-control-btn:nth-child(2)');
        if (btn) {
            const span = btn.querySelector('span');
            span.textContent = newType === 'satellite' ? 'Vista Mapa' : 'Vista Satélite';
        }
    }

    /**
     * Alternar pantalla completa
     */
    toggleFullscreen() {
        const container = document.querySelector('.route-map-container');
        if (!container) return;

        container.classList.toggle('fullscreen');
        
        // Forzar redimensionamiento del mapa
        setTimeout(() => {
            google.maps.event.trigger(this.map, 'resize');
            this.centerRoute();
        }, 300);
    }

    /**
     * Descargar archivo GPX
     */
    downloadGPX() {
        if (!this.currentRoute || !this.currentRoute.puntos) {
            alert('No hay datos de ruta para descargar');
            return;
        }

        let gpxContent = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Alma del Huila - Garzón Turismo">
  <metadata>
    <name>${this.currentRoute.nombre}</name>
    <desc>Ruta turística en Garzón, Huila</desc>
    <time>${new Date().toISOString()}</time>
  </metadata>
  <trk>
    <name>${this.currentRoute.nombre}</name>
    <trkseg>`;

        this.currentRoute.puntos.forEach(punto => {
            gpxContent += `
      <trkpt lat="${punto.latitud}" lon="${punto.longitud}">
        <name>${punto.nombre}</name>
        <desc>${punto.descripcion || ''}</desc>
      </trkpt>`;
        });

        gpxContent += `
    </trkseg>
  </trk>
</gpx>`;

        // Crear y descargar archivo
        const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ruta-${this.currentRoute.tipo || 'garzon'}.gpx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Mostrar loading
     */
    showLoading(container) {
        const loadingHTML = `
            <div class="map-loading">
                <div class="loading-spinner"></div>
            </div>
        `;
        container.innerHTML = loadingHTML;
    }

    /**
     * Mostrar placeholder cuando no hay mapa
     */
    showMapPlaceholder(container, message = 'No se pudo cargar el mapa') {
        const placeholderHTML = `
            <div class="map-placeholder">
                <div class="placeholder-content">
                    <div class="placeholder-icon">🗺️</div>
                    <h4>Mapa no disponible</h4>
                    <p>${message}</p>
                </div>
            </div>
        `;
        container.innerHTML = placeholderHTML;
    }
}

// Instancia global
let garzonMaps = null;

/**
 * Función de callback para Google Maps
 */
window.initGoogleMaps = function() {
    console.log('Google Maps API cargada');
    
    // Crear instancia global
    garzonMaps = new GarzonRouteMaps();
    
    // Si estamos en una página de detalle de ruta, inicializar el mapa
    const mapContainer = document.getElementById('route-map');
    if (mapContainer && window.routeData) {
        garzonMaps.initRouteMap('route-map', window.routeData);
    }
};

/**
 * Función para mostrar un punto específico en el mapa
 */
window.showPointOnMap = function(lat, lng, nombre) {
    if (garzonMaps) {
        garzonMaps.centerOnPoint(lat, lng);
        
        // Buscar y abrir el marcador correspondiente
        garzonMaps.markers.forEach((marker, index) => {
            const markerPos = marker.getPosition();
            if (Math.abs(markerPos.lat() - lat) < 0.001 && Math.abs(markerPos.lng() - lng) < 0.001) {
                garzonMaps.closeAllInfoWindows();
                garzonMaps.infoWindows[index].open(garzonMaps.map, marker);
            }
        });
    }
};

