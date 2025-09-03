/**
 * ==========================================
 * FUNCIONALIDAD PARA LISTA DE RUTAS
 * Archivo: static/js/route_list.js
 * ==========================================
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== FILTROS DE RUTAS ==========
    const filterBtns = document.querySelectorAll('.filter-btn');
    const routeItems = document.querySelectorAll('.route-item');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remover clase active de todos los botones
            filterBtns.forEach(b => {
                b.classList.remove('active');
                b.style.backgroundColor = 'transparent';
                b.style.color = '#5DAD47';
                b.style.borderColor = '#5DAD47';
            });
            
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            this.style.backgroundColor = '#5DAD47';
            this.style.color = 'white';
            this.style.borderColor = '#5DAD47';
            
            const filter = this.getAttribute('data-filter');
            
            routeItems.forEach((item, index) => {
                if (filter === '*' || item.classList.contains(filter.substring(1))) {
                    item.style.display = 'block';
                    item.style.opacity = '0';
                    // Animación escalonada
                    setTimeout(() => {
                        item.style.transition = 'opacity 0.3s ease';
                        item.style.opacity = '1';
                        item.classList.add('aos-animate');
                    }, index * 50);
                } else {
                    item.style.transition = 'opacity 0.2s ease';
                    item.style.opacity = '0';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 200);
                }
            });
        });
    });
    
    // ========== BOTONES DE FAVORITOS ==========
    document.querySelectorAll('.btn-favorite').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const heart = this.querySelector('.ph-heart');
            const isLiked = heart.classList.contains('ph-heart-fill');
            
            // Animación de click
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
            
            if (isLiked) {
                heart.className = 'ph-heart';
                this.classList.remove('btn-danger');
                this.classList.add('btn-outline-secondary');
                
                // Mostrar mensaje
                showToast('Ruta removida de favoritos', 'info');
            } else {
                heart.className = 'ph-heart-fill';
                this.classList.remove('btn-outline-secondary');
                this.style.backgroundColor = '#5DAD47';
                this.style.borderColor = '#5DAD47';
                this.style.color = 'white';
                
                // Efecto de partículas
                createHeartEffect(this);
                
                // Mostrar mensaje
                showToast('Ruta agregada a favoritos', 'success');
            }
        });
    });
    
    // ========== BOTONES DE COMPARTIR ==========
    document.querySelectorAll('.btn-share').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const routeCard = this.closest('.route-card');
            const routeTitle = routeCard.querySelector('.card-title a').textContent;
            const routeUrl = routeCard.querySelector('.card-title a').href;
            
            if (navigator.share && /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                navigator.share({
                    title: routeTitle,
                    text: `Descubre esta increíble ruta turística en Garzón: ${routeTitle}`,
                    url: routeUrl
                }).catch(console.error);
            } else {
                // Fallback: copiar al portapapeles
                navigator.clipboard.writeText(routeUrl).then(() => {
                    // Feedback visual
                    const originalIcon = this.querySelector('i');
                    const originalClass = originalIcon.className;
                    const originalTitle = this.getAttribute('title');
                    
                    originalIcon.className = 'ph-check';
                    this.setAttribute('title', '¡Enlace copiado!');
                    this.style.backgroundColor = '#5DAD47';
                    this.style.borderColor = '#5DAD47';
                    this.style.color = 'white';
                    
                    showToast('Enlace copiado al portapapeles', 'success');
                    
                    setTimeout(() => {
                        originalIcon.className = originalClass;
                        this.setAttribute('title', originalTitle);
                        this.style.backgroundColor = 'transparent';
                        this.style.borderColor = '#6c757d';
                        this.style.color = '#6c757d';
                    }, 2000);
                }).catch(() => {
                    // Si falla el clipboard, mostrar modal con el enlace
                    showShareModal(routeTitle, routeUrl);
                });
            }
        });
    });
    
    // ========== EFECTOS HOVER EN TARJETAS ==========
    document.querySelectorAll('.route-card-enhanced').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            // El CSS ya maneja el hover, no necesitamos resetear aquí
        });
    });
    
    // ========== ANIMACIÓN DE ESTADÍSTICAS ==========
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const animateStats = () => {
        statNumbers.forEach((stat, index) => {
            const finalValue = parseInt(stat.textContent);
            let currentValue = 0;
            const increment = finalValue / 30; // 30 frames para la animación
            
            const timer = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    currentValue = finalValue;
                    clearInterval(timer);
                }
                stat.textContent = Math.floor(currentValue);
            }, 50);
        });
    };
    
    // Ejecutar animación cuando las estadísticas estén en viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                observer.unobserve(entry.target);
            }
        });
    });
    
    const statsContainer = document.querySelector('.floating-stats');
    if (statsContainer) {
        observer.observe(statsContainer);
    }
    
    // ========== SMOOTH SCROLL PARA NAVEGACIÓN ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// ========== FUNCIONES AUXILIARES ==========

/**
 * Crear efecto de corazón animado
 */
function createHeartEffect(button) {
    const rect = button.getBoundingClientRect();
    const heart = document.createElement('div');
    heart.innerHTML = '♥';
    heart.style.cssText = `
        position: fixed;
        left: ${rect.left + rect.width / 2}px;
        top: ${rect.top}px;
        color: #5DAD47;
        font-size: 20px;
        pointer-events: none;
        z-index: 9999;
        transition: all 0.8s ease-out;
    `;
    
    document.body.appendChild(heart);
    
    setTimeout(() => {
        heart.style.transform = 'translateY(-30px)';
        heart.style.opacity = '0';
    }, 10);
    
    setTimeout(() => {
        document.body.removeChild(heart);
    }, 800);
}

/**
 * Mostrar modal de compartir (fallback)
 */
function showShareModal(title, url) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Compartir Ruta</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="small mb-2">${title}</p>
                    <div class="input-group">
                        <input type="text" class="form-control" value="${url}" readonly>
                        <button class="btn btn-outline-secondary copy-url-btn" type="button">
                            <i class="ph-copy"></i>
                        </button>
                    </div>
                    <div class="mt-3">
                        <div class="d-grid gap-2">
                            <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}" 
                               target="_blank" class="btn btn-primary btn-sm">
                                <i class="ph-facebook-logo me-2"></i>Facebook
                            </a>
                            <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}" 
                               target="_blank" class="btn btn-info btn-sm">
                                <i class="ph-twitter-logo me-2"></i>Twitter
                            </a>
                            <a href="https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}" 
                               target="_blank" class="btn btn-success btn-sm">
                                <i class="ph-whatsapp-logo me-2"></i>WhatsApp
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Botón copiar del modal
    modal.querySelector('.copy-url-btn').addEventListener('click', function() {
        const input = modal.querySelector('input');
        input.select();
        navigator.clipboard.writeText(input.value).then(() => {
            this.innerHTML = '<i class="ph-check"></i>';
            showToast('Enlace copiado', 'success');
            setTimeout(() => {
                this.innerHTML = '<i class="ph-copy"></i>';
            }, 1000);
        });
    });
    
    // Limpiar modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

/**
 * Mostrar notificación toast
 */
function showToast(message, type = 'info') {
    // Verificar si ya existe un contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'info' ? 'bg-info' : 'bg-primary';
    
    const toastHTML = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
            <div class="toast-body d-flex align-items-center">
                <i class="ph-${type === 'success' ? 'check-circle' : type === 'info' ? 'info' : 'bell'} me-2"></i>
                ${message}
                <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    
    toast.show();
    
    // Limpiar toast después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

/**
 * Cargar vista previa de mapa para una ruta (función placeholder)
 */
function loadRoutePreview(routeSlug, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Simulación de carga de vista previa
    container.innerHTML = `
        <div class="d-flex align-items-center justify-content-center h-100">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <small>Cargando mapa...</small>
        </div>
    `;
    
    // Simular carga después de 2 segundos
    setTimeout(() => {
        container.innerHTML = `
            <div class="text-center">
                <i class="ph-map-trifold mb-1" style="font-size: 24px; color: #5DAD47;"></i>
                <div>Vista previa disponible</div>
                <small class="text-success">Mapa cargado</small>
            </div>
        `;
    }, 2000);
}

/**
 * Funciones de utilidad para animaciones
 */
const AnimationUtils = {
    
    /**
     * Animar entrada de elementos
     */
    fadeInUp: function(elements, delay = 100) {
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * delay);
        });
    },
    
    /**
     * Animar números contadores
     */
    animateCounter: function(element, targetValue, duration = 2000) {
        const startValue = 0;
        const increment = targetValue / (duration / 16);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(currentValue);
        }, 16);
    },
    
    /**
     * Efecto de pulsación
     */
    pulse: function(element, scale = 1.05, duration = 300) {
        const originalTransform = element.style.transform;
        element.style.transition = `transform ${duration}ms ease`;
        element.style.transform = `scale(${scale})`;
        
        setTimeout(() => {
            element.style.transform = originalTransform;
        }, duration);
    }
};

/**
 * Inicialización de lazy loading para imágenes
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

/**
 * Manejar errores de carga de imágenes
 */
function handleImageErrors() {
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/img/placeholder.jpg';
            this.alt = 'Imagen no disponible';
        });
    });
}

/**
 * Funciones de inicialización
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar lazy loading
    initLazyLoading();
    
    // Manejar errores de imágenes
    handleImageErrors();
    
    // Agregar clase para animaciones CSS
    document.body.classList.add('animations-ready');
});

/**
 * Optimización de rendimiento
 */
const PerformanceUtils = {
    
    /**
     * Debounce para eventos que se disparan frecuentemente
     */
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },
    
    /**
     * Throttle para limitar la frecuencia de ejecución
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

/**
 * Manejo de eventos de scroll optimizado
 */
window.addEventListener('scroll', PerformanceUtils.throttle(function() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Efecto parallax sutil en el hero
    const hero = document.querySelector('.hero-routes');
    if (hero) {
        const offset = scrollTop * 0.5;
        hero.style.transform = `translateY(${offset}px)`;
    }
    
    // Mostrar/ocultar botón de scroll to top si existe
    const scrollBtn = document.querySelector('.scroll-to-top');
    if (scrollBtn) {
        if (scrollTop > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    }
}, 16));

/**
 * Funciones de accesibilidad
 */
const AccessibilityUtils = {
    
    /**
     * Mejorar navegación por teclado
     */
    enhanceKeyboardNavigation: function() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', function() {
            document.body.classList.remove('keyboard-navigation');
        });
    },
    
    /**
     * Anunciar cambios dinámicos para lectores de pantalla
     */
    announceChange: function(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
};

// Inicializar mejoras de accesibilidad
AccessibilityUtils.enhanceKeyboardNavigation();

/**
 * Exportar funciones para uso global
 */
window.RouteListUtils = {
    showToast,
    createHeartEffect,
    AnimationUtils,
    PerformanceUtils,
    AccessibilityUtils
};
