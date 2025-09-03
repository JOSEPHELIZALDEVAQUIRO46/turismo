/**
 * Script para el detalle de rutas - Manejo del mapa interactivo
 * Garzón Turístico
 */

// Variables globales
let routeMap;
let markers = [];
let routePath;
let routeDetailData;

/**
 * Función de callback para Google Maps API
 */
window.initGoogleMaps = function() {
    console.log('Google Maps API cargada, inicializando mapa de ruta...');
    
    // Esperar a que los datos estén disponibles
    setTimeout(() => {
        if (typeof window.routeDetailData !== 'undefined' && window.routeDetailData) {
            routeDetailData = window.routeDetailData;
            
            if (routeDetailData.puntos && routeDetailData.puntos.length > 0) {
                try {
                    initRouteMap();
                } catch (error) {
                    console.error('Error inicializando el mapa:', error);
                    showMapError('Error al cargar el mapa: ' + error.message);
                }
            } else {
                console.warn('No hay puntos de ruta disponibles');
                showMapError('No hay puntos de ruta disponibles');
            }
        } else {
            console.error('No hay datos de la ruta disponibles');
            showMapError('No se pudieron cargar los datos de la ruta');
        }
    }, 100);
};

/**
 * Inicializar el mapa de la ruta
 */
function initRouteMap() {
    const mapContainer = document.getElementById('route-map');
    
    if (!mapContainer) {
        console.error('Contenedor del mapa no encontrado');
        return;
    }
    
    console.log('Inicializando mapa con datos:', routeDetailData);
    
    // Calcular el centro y bounds del mapa
    const bounds = new google.maps.LatLngBounds();
    const puntos = routeDetailData.puntos;
    
    // Centro por defecto en Garzón si no hay puntos
    let center = { lat: 2.1975, lng: -75.6514 };
    
    if (puntos.length > 0) {
        // Usar el primer punto como centro inicial
        center = { lat: puntos[0].latitud, lng: puntos[0].longitud };
        
        // Extender bounds con todos los puntos
        puntos.forEach(punto => {
            bounds.extend(new google.maps.LatLng(punto.latitud, punto.longitud));
        });
    }
    
    // Crear el mapa
    routeMap = new google.maps.Map(mapContainer, {
        zoom: 13,
        center: center,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'on' }]
            },
            {
                featureType: 'transit',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ],
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
        zoomControl: true
    });
    
    console.log('Mapa base creado exitosamente');
    
    // Agregar marcadores
    addRouteMarkers();
    
    // Dibujar la ruta si hay más de un punto
    if (puntos.length > 1) {
        drawRoutePath();
    }
    
    // Ajustar la vista al contenido
    if (puntos.length > 1) {
        routeMap.fitBounds(bounds);
        
        // Asegurar un zoom apropiado
        const listener = google.maps.event.addListener(routeMap, 'idle', function() {
            if (routeMap.getZoom() > 15) routeMap.setZoom(15);
            google.maps.event.removeListener(listener);
        });
    } else if (puntos.length === 1) {
        routeMap.setZoom(14);
    }
    
    console.log('Mapa de ruta inicializado correctamente con ' + puntos.length + ' puntos');
}

/**
 * Agregar marcadores al mapa
 */
function addRouteMarkers() {
    const puntos = routeDetailData.puntos;
    
    // Limpiar marcadores existentes
    markers.forEach(markerData => {
        markerData.marker.setMap(null);
    });
    markers = [];
    
    puntos.forEach((punto, index) => {
        const position = { lat: punto.latitud, lng: punto.longitud };
        
        // Determinar el color del marcador
        let markerColor = '#5DAD47'; // Verde por defecto
        if (index === 0) {
            markerColor = '#22C55E'; // Verde más claro para inicio
        } else if (index === puntos.length - 1) {
            markerColor = '#EF4444'; // Rojo para final
        }
        
        // Crear marcador personalizado
        const marker = new google.maps.Marker({
            position: position,
            map: routeMap,
            title: punto.nombre,
            label: {
                text: punto.orden.toString(),
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px'
            },
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: markerColor,
                fillOpacity: 1,
                strokeColor: 'white',
                strokeWeight: 3,
                scale: 15
            },
            animation: google.maps.Animation.DROP
        });
        
        // Crear ventana de información
        const infoWindow = new google.maps.InfoWindow({
            content: createInfoWindowContent(punto, index)
        });
        
        // Agregar evento click
        marker.addListener('click', function() {
            // Cerrar otras ventanas
            markers.forEach(m => {
                if (m.infoWindow) {
                    m.infoWindow.close();
                }
            });
            
            infoWindow.open(routeMap, marker);
        });
        
        // Agregar efecto hover
        marker.addListener('mouseover', function() {
            marker.setOptions({
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    fillColor: markerColor,
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3,
                    scale: 18
                }
            });
        });
        
        marker.addListener('mouseout', function() {
            marker.setOptions({
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    fillColor: markerColor,
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3,
                    scale: 15
                }
            });
        });
        
        // Guardar referencia
        markers.push({
            marker: marker,
            infoWindow: infoWindow,
            punto: punto
        });
    });
    
    console.log('Agregados ' + markers.length + ' marcadores al mapa');
}

/**
 * Crear contenido para la ventana de información
 */
function createInfoWindowContent(punto, index) {
    const isFirst = index === 0;
    const isLast = index === routeDetailData.puntos.length - 1;
    
    let statusText = 'Punto intermedio';
    let statusColor = '#5DAD47';
    let statusIcon = '📍';
    
    if (isFirst) {
        statusText = 'Punto de inicio';
        statusColor = '#22C55E';
        statusIcon = '🚀';
    } else if (isLast) {
        statusText = 'Punto final';
        statusColor = '#EF4444';
        statusIcon = '🏁';
    }
    
    return `
        <div style="max-width: 320px; padding: 15px; font-family: system-ui, -apple-system, sans-serif;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="background: ${statusColor}; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; font-size: 14px;">
                    ${punto.orden}
                </div>
                <div style="flex: 1;">
                    <h6 style="margin: 0; color: #2c3e50; font-weight: bold; font-size: 16px;">${punto.nombre}</h6>
                    <small style="color: ${statusColor}; font-weight: 600; font-size: 12px;">
                        ${statusIcon} ${statusText}
                    </small>
                </div>
            </div>
            
            ${punto.descripcion ? `
                <div style="margin: 12px 0; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid ${statusColor};">
                    <p style="margin: 0; color: #495057; font-size: 14px; line-height: 1.5;">${punto.descripcion}</p>
                </div>
            ` : ''}
            
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0;">
                ${punto.tiempo_estancia ? `
                    <div style="display: flex; align-items: center; background: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">
                        <span style="margin-right: 4px;">⏱️</span>
                        ${punto.tiempo_estancia}
                    </div>
                ` : ''}
                
                <div style="display: flex; align-items: center; background: #f3e5f5; color: #7b1fa2; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">
                    <span style="margin-right: 4px;">📍</span>
                    ${punto.latitud.toFixed(4)}, ${punto.longitud.toFixed(4)}
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #e9ecef;">
                <div style="display: flex; gap: 8px;">
                    <button onclick="routeMap.setCenter({lat: ${punto.latitud}, lng: ${punto.longitud}}); routeMap.setZoom(17);" 
                            style="flex: 1; background: ${statusColor}; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity 0.2s;">
                        🔍 Acercar
                    </button>
                    <button onclick="navigator.geolocation && navigator.geolocation.getCurrentPosition(pos => { const directionsUrl = 'https://www.google.com/maps/dir/' + pos.coords.latitude + ',' + pos.coords.longitude + '/' + ${punto.latitud} + ',' + ${punto.longitud}; window.open(directionsUrl, '_blank'); }, () => { const directionsUrl = 'https://www.google.com/maps/dir//${punto.latitud},${punto.longitud}'; window.open(directionsUrl, '_blank'); });" 
                            style="flex: 1; background: #17a2b8; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: opacity 0.2s;">
                        🗺️ Ir
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Dibujar la ruta conectando los puntos
 */
function drawRoutePath() {
    const puntos = routeDetailData.puntos;
    
    if (puntos.length < 2) return;
    
    // Limpiar ruta existente
    if (routePath) {
        routePath.setMap(null);
    }
    
    const path = puntos.map(punto => ({
        lat: punto.latitud,
        lng: punto.longitud
    }));
    
    routePath = new google.maps.Polyline({
        path: path,
        geodesic: true,
        strokeColor: '#5DAD47',
        strokeOpacity: 0.8,
        strokeWeight: 4,
        icons: [{
            icon: {
                path: google.maps.SymbolPath.FORWARD_OPEN_ARROW,
                strokeColor: '#2e7d32',
                strokeWeight: 2,
                scale: 4
            },
            offset: '50%',
            repeat: '150px'
        }]
    });
    
    routePath.setMap(routeMap);
    
    // Agregar efecto de hover a la ruta
    routePath.addListener('mouseover', function() {
        routePath.setOptions({
            strokeWeight: 6,
            strokeOpacity: 1
        });
    });
    
    routePath.addListener('mouseout', function() {
        routePath.setOptions({
            strokeWeight: 4,
            strokeOpacity: 0.8
        });
    });
    
    console.log('Ruta dibujada conectando ' + puntos.length + ' puntos');
}

/**
 * Mostrar un punto específico en el mapa (función global)
 */
window.showPointOnMap = function(lat, lng, nombre) {
    if (!routeMap) {
        console.warn('El mapa no está inicializado aún');
        alert('El mapa se está cargando, intenta nuevamente en un momento.');
        return;
    }
    
    // Centrar el mapa en el punto
    const position = new google.maps.LatLng(lat, lng);
    routeMap.setCenter(position);
    routeMap.setZoom(16);
    
    // Encontrar y abrir la ventana de información correspondiente
    const markerData = markers.find(m => 
        Math.abs(m.punto.latitud - lat) < 0.0001 && 
        Math.abs(m.punto.longitud - lng) < 0.0001
    );
    
    if (markerData) {
        // Cerrar otras ventanas
        markers.forEach(m => {
            if (m.infoWindow) {
                m.infoWindow.close();
            }
        });
        
        // Abrir la ventana del punto seleccionado
        setTimeout(() => {
            markerData.infoWindow.open(routeMap, markerData.marker);
        }, 500);
        
        // Hacer bounce al marcador
        markerData.marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(() => {
            markerData.marker.setAnimation(null);
        }, 2100);
    }
    
    // Scroll suave al mapa
    setTimeout(() => {
        document.getElementById('route-map').scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }, 300);
};

/**
 * Mostrar error en el mapa
 */
function showMapError(message = 'No se pudieron cargar los datos de la ruta') {
    const mapContainer = document.getElementById('route-map');
    if (mapContainer) {
        const errorHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 500px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px dashed #dee2e6; border-radius: 8px; color: #6c757d; text-align: center; font-family: system-ui, -apple-system, sans-serif;">
                <div style="max-width: 400px; padding: 30px;">
                    <div style="font-size: 4rem; margin-bottom: 20px; opacity: 0.7;">🗺️</div>
                    <h4 style="margin-bottom: 15px; color: #495057; font-weight: 600;">Mapa no disponible</h4>
                    <p style="margin: 0; line-height: 1.5; color: #6c757d;">${message}</p>
                    <div style="margin-top: 20px;">
                        <button onclick="location.reload()" style="background: #5DAD47; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                            🔄 Reintentar
                        </button>
                    </div>
                </div>
            </div>
        `;
        mapContainer.innerHTML = errorHTML;
    }
}

/**
 * Manejo de errores de autenticación de Google Maps
 */
window.gm_authFailure = function() {
    console.error('Error de autenticación de Google Maps API');
    showMapError('Error de autenticación con Google Maps. Verifica la configuración de la API key.');
};

/**
 * Funciones adicionales cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configurar botón de descarga GPX
    const downloadBtn = document.getElementById('downloadGPX');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            if (routeDetailData && routeDetailData.puntos) {
                generateGPXDownload();
            } else {
                alert('No hay datos de ruta disponibles para descargar.');
            }
        });
    }
    
    // Agregar indicador de carga para el mapa
    const mapContainer = document.getElementById('route-map');
    if (mapContainer && !mapContainer.innerHTML.trim()) {
        mapContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 500px; background: #f8f9fa; border-radius: 8px; color: #6c757d;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 15px;">🔄</div>
                    <p>Cargando mapa interactivo...</p>
                </div>
            </div>
        `;
    }
});

/**
 * Generar y descargar archivo GPX
 */
function generateGPXDownload() {
    if (!routeDetailData || !routeDetailData.puntos || routeDetailData.puntos.length === 0) {
        alert('No hay puntos de ruta para exportar.');
        return;
    }
    
    const puntos = routeDetailData.puntos;
    const routeName = routeDetailData.ruta.nombre;
    
    let gpxContent = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Garzón Turístico" xmlns="http://www.topografix.com/GPX/1/1">
    <metadata>
        <name>${routeName}</name>
        <desc>${routeDetailData.ruta.descripcion || 'Ruta turística en Garzón, Huila'}</desc>
    </metadata>
    <trk>
        <name>${routeName}</name>
        <desc>Ruta de ${routeDetailData.ruta.distancia} km con duración estimada de ${routeDetailData.ruta.duracion_estimada}</desc>
        <trkseg>
`;
    
    puntos.forEach(punto => {
        gpxContent += `            <trkpt lat="${punto.latitud}" lon="${punto.longitud}">
                <name>${punto.nombre}</name>
                <desc>${punto.descripcion || ''}</desc>
            </trkpt>
`;
    });
    
    gpxContent += `        </trkseg>
    </trk>
`;
    
    puntos.forEach(punto => {
        gpxContent += `    <wpt lat="${punto.latitud}" lon="${punto.longitud}">
        <name>${punto.nombre}</name>
        <desc>${punto.descripcion || ''}</desc>
    </wpt>
`;
    });
    
    gpxContent += `</gpx>`;
    
    // Crear y descargar el archivo
    const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${routeDetailData.ruta.slug || 'ruta'}.gpx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log('Archivo GPX generado y descargado');
}