// main.js - OnlineBazar E-commerce JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Preloader
    window.addEventListener('load', function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.transition = 'opacity 0.5s ease';
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.custom-navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }

    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.style.display = 'block';
                backToTopButton.classList.add('animate__fadeIn');
                backToTopButton.classList.remove('animate__fadeOut');
            } else {
                backToTopButton.classList.add('animate__fadeOut');
                backToTopButton.classList.remove('animate__fadeIn');
                setTimeout(() => {
                    backToTopButton.style.display = 'none';
                }, 500);
            }
        });

        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const imgContainer = this.querySelector('.product-img-container');
            const actions = this.querySelector('.product-actions');
            if (imgContainer && actions) {
                imgContainer.style.transform = 'translateY(-10px)';
                actions.style.opacity = '1';
            }
        });

        card.addEventListener('mouseleave', function() {
            const imgContainer = this.querySelector('.product-img-container');
            const actions = this.querySelector('.product-actions');
            if (imgContainer && actions) {
                imgContainer.style.transform = 'translateY(0)';
                actions.style.opacity = '0';
            }
        });
    });

    // Wishlist functionality
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const icon = this.querySelector('i');
            
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas', 'animate__animated', 'animate__heartBeat');
                addToWishlist(productId);
            } else {
                icon.classList.remove('fas', 'animate__heartBeat');
                icon.classList.add('far');
                removeFromWishlist(productId);
            }
            
            // Remove animation class after animation completes
            setTimeout(() => {
                icon.classList.remove('animate__heartBeat');
            }, 1000);
        });
    });

    // Quick view functionality
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    quickViewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            // In a real implementation, you would fetch product details via AJAX
            // and display them in a modal
            window.location.href = `/single-product-page/${productId}`;
        });
    });

    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.btn-add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.closest('.product-card').querySelector('.wishlist-btn').getAttribute('data-product-id');
            
            // We no longer manually stop the submission because we redirect to checkout/cart
            // addToCart handles the real form submit which will navigate away!
            addToCart(productId, 1);
            
            // Visual feedback (in case of slow connection)
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            this.classList.add('added-to-cart');
        });
    });

    // Search form submission
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[name="search"]');
            if (searchInput.value.trim() !== '') {
                this.action = `/shop/ALL/ALL/ALL/?search=${encodeURIComponent(searchInput.value.trim())}`;
                this.submit();
            }
        });
    }

    // Newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const submitButton = this.querySelector('button[type="submit"]');
            
            if (validateEmail(emailInput.value)) {
                // In a real implementation, you would send this to your backend
                submitButton.innerHTML = '<i class="fas fa-check"></i> Subscribed!';
                submitButton.disabled = true;
                emailInput.disabled = true;
                
                // Show success message
                showToast('Successfully subscribed to our newsletter!', 'success');
            } else {
                showToast('Please enter a valid email address', 'error');
            }
        });
    }

    // Testimonial slider (would be implemented if you add a slider)
    // initializeTestimonialSlider();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Update cart count on page load
    updateCartCount();
});

// Helper Functions

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">
            ${type === 'success' ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-exclamation-circle"></i>'}
        </div>
        <div class="toast-message">${message}</div>
    `;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Hide after delay
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 500);
    }, 3000);
}

function addToCart(productId, quantity) {
    // Submit an actual POST request to the backend instead of storing in LocalStorage
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/add-to-cart/';
    
    // Add CSRF Token
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    if (csrfElement) {
        csrfInput.value = csrfElement.value;
    } else {
        const match = document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'));
        csrfInput.value = match ? match[2] : '';
    }
    form.appendChild(csrfInput);

    const pidInput = document.createElement('input');
    pidInput.type = 'hidden';
    pidInput.name = 'pid';
    pidInput.value = productId;
    form.appendChild(pidInput);

    const colorInput = document.createElement('input');
    colorInput.type = 'hidden';
    colorInput.name = 'color';
    colorInput.value = "";
    form.appendChild(colorInput);
    
    const sizeInput = document.createElement('input');
    sizeInput.type = 'hidden';
    sizeInput.name = 'size';
    sizeInput.value = "";
    form.appendChild(sizeInput);

    document.body.appendChild(form);
    form.submit();
}

function removeFromCart(productId) {
    // Should be handled by backend URL in django templates
}

function updateCartCount() {
    // Clean up old localStorage cart to prevent mismatch
    if (localStorage.getItem('onlineBazarCart')) {
        localStorage.removeItem('onlineBazarCart');
    }
    
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        // Hide badge if count is 0
        const val = parseInt(element.textContent);
        if (val > 0) {
            element.style.display = 'flex';
        } else {
            element.style.display = 'none';
        }
    });
}

function addToWishlist(productId) {
    // In a real implementation, this would make an AJAX call to your backend
    console.log(`Adding product ${productId} to wishlist`);
    
    // For demo purposes, we'll use localStorage
    let wishlist = JSON.parse(localStorage.getItem('onlineBazarWishlist')) || [];
    if (!wishlist.includes(productId)) {
        wishlist.push(productId);
        localStorage.setItem('onlineBazarWishlist', JSON.stringify(wishlist));
    }
    showToast('Product added to wishlist!', 'success');
}

function removeFromWishlist(productId) {
    let wishlist = JSON.parse(localStorage.getItem('onlineBazarWishlist')) || [];
    wishlist = wishlist.filter(id => id !== productId);
    localStorage.setItem('onlineBazarWishlist', JSON.stringify(wishlist));
    showToast('Product removed from wishlist', 'error');
}

// This would be used if you implement a testimonial slider
function initializeTestimonialSlider() {
    const testimonialSlider = document.querySelector('.testimonial-slider');
    if (testimonialSlider) {
        // Initialize a slider library like Swiper.js or implement your own
    }
}