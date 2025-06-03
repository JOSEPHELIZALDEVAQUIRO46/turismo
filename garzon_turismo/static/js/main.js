/**
 * Main JavaScript - Alma del Huila - Garzón
 * 
 * Este archivo contiene todas las funcionalidades
 * necesarias para la interacción del sitio web.
 */

(function() {
    'use strict';

    // Variables DOM
    const body = document.body;
    const preloader = document.querySelector('.preloader');
    const header = document.querySelector('.site-header');
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = searchOverlay ? searchOverlay.querySelector('input[type="text"]') : null;
    const backToTop = document.getElementById('backToTop');
    const mobileToggle = document.querySelector('.navbar-toggler');

    /**
     * Preloader
     * Oculta el preloader cuando la página ha cargado completamente
     */
    function hidePreloader() {
        if (preloader) {
            preloader.classList.add('loaded');
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }
    }

    /**
     * Header Scroll
     * Añade una clase al header cuando se hace scroll
     */
    function handleScroll() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        // Back to Top Button
        if (backToTop) {
            if (window.scrollY > 500) {
                backToTop.classList.add('active');
            } else {
                backToTop.classList.remove('active');
            }
        }
    }

    /**
     * Search Overlay
     * Funcionalidad para mostrar/ocultar el overlay de búsqueda
     */
    function toggleSearchOverlay() {
        if (searchOverlay) {
            searchOverlay.classList.toggle('active');
            body.style.overflow = searchOverlay.classList.contains('active') ? 'hidden' : '';
            
            if (searchOverlay.classList.contains('active') && searchInput) {
                setTimeout(() => {
                    searchInput.focus();
                }, 100);
            }
        }
    }

    /**
     * Back to Top
     * Scroll suave hacia el inicio de la página
     */
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    /**
     * Initialize AOS (Animate on Scroll)
     */
    function initAOS() {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 50
        });
    }

    /**
     * Initialize Swiper Sliders
     */
    function initSwipers() {
        // Hero Slider
        const heroSlider = document.querySelector('.hero-slider');
        if (heroSlider) {
            new Swiper(heroSlider, {
                slidesPerView: 1,
                spaceBetween: 0,
                effect: 'fade',
                speed: 1000,
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                },
                loop: true,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
            });
        }

        // Testimonios Slider
        const testimonialSlider = document.querySelector('.testimonial-slider');
        if (testimonialSlider) {
            new Swiper(testimonialSlider, {
                slidesPerView: 1,
                spaceBetween: 30,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                autoplay: {
                    delay: 4000,
                    disableOnInteraction: false,
                },
                breakpoints: {
                    768: {
                        slidesPerView: 2,
                    },
                    992: {
                        slidesPerView: 3,
                    }
                }
            });
        }

        // Destinos Slider
        const destinationSlider = document.querySelector('.destination-slider');
        if (destinationSlider) {
            new Swiper(destinationSlider, {
                slidesPerView: 1,
                spaceBetween: 20,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                breakpoints: {
                    576: {
                        slidesPerView: 2,
                    },
                    992: {
                        slidesPerView: 3,
                    },
                    1200: {
                        slidesPerView: 4,
                    }
                }
            });
        }
    }

    /**
     * Mobile Navigation
     * Toggle para el menú móvil
     */
    function handleMobileNav() {
        if (mobileToggle) {
            const navbarCollapse = document.getElementById('navbarMain');
            
            // Cierra el menú móvil cuando se hace click en un enlace
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (window.innerWidth < 992) {
                        navbarCollapse.classList.remove('show');
                    }
                });
            });
        }
    }

    /**
     * Bootstrap Tooltips
     * Inicializa los tooltips de Bootstrap
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Bootstrap Toasts
     * Inicializa los toasts de Bootstrap para los mensajes
     */
    function initToasts() {
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.map(function (toastEl) {
            return new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 5000
            });
        });
    }

    /**
     * Counters Animation
     * Animación para los contadores en la sección de estadísticas
     */
    function initCounters() {
        const counters = document.querySelectorAll('.counter-number');
        
        if (counters.length) {
            const observerOptions = {
                threshold: 0.5
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const counter = entry.target;
                        const target = parseInt(counter.getAttribute('data-target'));
                        const duration = 2000; // 2 segundos
                        const increment = target / (duration / 16); // 60fps
                        
                        let current = 0;
                        const updateCounter = () => {
                            current += increment;
                            counter.textContent = Math.ceil(current);
                            
                            if (current < target) {
                                requestAnimationFrame(updateCounter);
                            } else {
                                counter.textContent = target;
                            }
                        };
                        
                        updateCounter();
                        observer.unobserve(counter);
                    }
                });
            }, observerOptions);
            
            counters.forEach(counter => {
                observer.observe(counter);
            });
        }
    }

    /**
     * Lazy Loading Images
     * Carga diferida de imágenes para mejorar el rendimiento
     */
    function initLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if (lazyImages.length) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Newsletter Form
     * Validación y envío del formulario de newsletter
     */
    function handleNewsletterForm() {
        const newsletterForm = document.querySelector('.newsletter-form');
        
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const emailInput = this.querySelector('input[type="email"]');
                const email = emailInput.value.trim();
                
                if (email && validateEmail(email)) {
                    // Aquí iría la lógica para enviar el formulario al backend
                    // Por ahora, solo mostramos un mensaje de éxito
                    
                    // Simular éxito
                    alert('¡Gracias por suscribirte a nuestro boletín!');
                    newsletterForm.reset();
                } else {
                    alert('Por favor, introduce un email válido');
                }
            });
        }
    }

    /**
     * Validate Email
     * Función auxiliar para validar emails
     */
    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    /**
     * Google Maps
     * Inicialización del mapa de Google si existe en la página
     */
    function initMap() {
        const mapElement = document.getElementById('google-map');
        
        if (mapElement && typeof google !== 'undefined' && google.maps) {
            const lat = parseFloat(mapElement.getAttribute('data-lat') || '2.1976');
            const lng = parseFloat(mapElement.getAttribute('data-lng') || '-75.6276');
            
            const mapOptions = {
                center: { lat, lng },
                zoom: 14,
                styles: [
                    {
                        "featureType": "administrative",
                        "elementType": "labels.text.fill",
                        "stylers": [
                            {
                                "color": "#444444"
                            }
                        ]
                    },
                    {
                        "featureType": "landscape",
                        "elementType": "all",
                        "stylers": [
                            {
                                "color": "#f2f2f2"
                            }
                        ]
                    },
                    {
                        "featureType": "poi",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "road",
                        "elementType": "all",
                        "stylers": [
                            {
                                "saturation": -100
                            },
                            {
                                "lightness": 45
                            }
                        ]
                    },
                    {
                        "featureType": "road.highway",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "simplified"
                            }
                        ]
                    },
                    {
                        "featureType": "road.arterial",
                        "elementType": "labels.icon",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "transit",
                        "elementType": "all",
                        "stylers": [
                            {
                                "visibility": "off"
                            }
                        ]
                    },
                    {
                        "featureType": "water",
                        "elementType": "all",
                        "stylers": [
                            {
                                "color": "#5DAD47"
                            },
                            {
                                "visibility": "on"
                            }
                        ]
                    }
                ]
            };
            
            const map = new google.maps.Map(mapElement, mapOptions);
            
            // Marcador central
            new google.maps.Marker({
                position: { lat, lng },
                map: map,
                title: 'Garzón, Huila',
                icon: {
                    url: '/static/img/map-marker.png',
                    scaledSize: new google.maps.Size(40, 40)
                }
            });
        }
    }

    /**
     * Event Listeners
     */
    function setupEventListeners() {
        // Preloader
        window.addEventListener('load', hidePreloader);
        
        // Scroll
        window.addEventListener('scroll', handleScroll);
        
        // Search
        if (searchToggle) {
            searchToggle.addEventListener('click', toggleSearchOverlay);
        }
        if (searchClose) {
            searchClose.addEventListener('click', toggleSearchOverlay);
        }
        
        // Back to Top
        if (backToTop) {
            backToTop.addEventListener('click', scrollToTop);
        }
        
        // Document click para cerrar el overlay de búsqueda
        document.addEventListener('click', function(e) {
            if (searchOverlay && searchOverlay.classList.contains('active')) {
                if (e.target === searchOverlay) {
                    toggleSearchOverlay();
                }
            }
        });
        
        // Escape key para cerrar el overlay de búsqueda
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchOverlay && searchOverlay.classList.contains('active')) {
                toggleSearchOverlay();
            }
        });
    }

    /**
     * Inicialización
     */
    function init() {
        // Setup event listeners
        setupEventListeners();
        
        // Initialize components
        initAOS();
        initSwipers();
        handleMobileNav();
        initTooltips();
        initToasts();
        initCounters();
        initLazyLoading();
        handleNewsletterForm();
        initMap();
        
        // Trigger scroll once to set correct states
        handleScroll();
    }

    // Run initialization
    document.addEventListener('DOMContentLoaded', init);

})();