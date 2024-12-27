document.addEventListener("DOMContentLoaded", function() {
    // Initialize accordion
    initializeAccordion();
    // Initialize form validation
    initializeFormValidation();
});

function initializeAccordion() {
    const accordionItems = document.querySelectorAll(".accordion-item h3");
    
    accordionItems.forEach(item => {
        // Add cursor pointer and aria attributes for accessibility
        item.style.cursor = 'pointer';
        item.setAttribute('aria-expanded', 'false');
        
        item.addEventListener("click", () => {
            const content = item.nextElementSibling;
            const isExpanded = item.getAttribute('aria-expanded') === 'true';
            
            // Toggle aria-expanded attribute
            item.setAttribute('aria-expanded', !isExpanded);
            
            // Add smooth animation
            if (!isExpanded) {
                content.style.display = 'block';
                content.style.maxHeight = '0';
                content.style.opacity = '0';
                // Trigger reflow
                content.offsetHeight;
                content.style.transition = 'max-height 0.3s ease-in-out, opacity 0.3s ease-in-out';
                content.style.maxHeight = content.scrollHeight + 'px';
                content.style.opacity = '1';
            } else {
                content.style.maxHeight = '0';
                content.style.opacity = '0';
                // Remove display:block after animation
                setTimeout(() => {
                    content.style.display = 'none';
                }, 300);
            }
        });
    });
}

function initializeFormValidation() {
    const form = document.querySelector("form");
    const fields = {
        name: {
            element: document.getElementById("name"),
            validate: value => value.length >= 2,
            message: "Name must be at least 2 characters long"
        },
        email: {
            element: document.getElementById("email"),
            validate: validateEmail,
            message: "Please enter a valid email address"
        },
        message: {
            element: document.getElementById("message"),
            validate: value => value.length >= 10,
            message: "Message must be at least 10 characters long"
        }
    };

    // Add real-time validation
    Object.keys(fields).forEach(fieldName => {
        const field = fields[fieldName];
        const element = field.element;
        
        // Add error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'red';
        errorDiv.style.fontSize = '0.8em';
        errorDiv.style.display = 'none';
        element.parentNode.insertBefore(errorDiv, element.nextSibling);

        // Add input event listener for real-time validation
        element.addEventListener('input', debounce(() => {
            validateField(field, errorDiv);
        }, 500));
    });

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        
        let isValid = true;
        
        // Validate all fields
        Object.keys(fields).forEach(fieldName => {
            const field = fields[fieldName];
            const errorDiv = field.element.nextElementSibling;
            if (!validateField(field, errorDiv)) {
                isValid = false;
            }
        });

        if (isValid) {
            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            // Submit form
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => response.json())
            .then(data => {
                alert('Message sent successfully!');
                form.reset();
            })
            .catch(error => {
                alert('Error sending message. Please try again.');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
        }
    });
}

function validateField(field, errorDiv) {
    const value = field.element.value.trim();
    const isValid = field.validate(value);
    
    if (!isValid) {
        field.element.style.borderColor = 'red';
        errorDiv.textContent = field.message;
        errorDiv.style.display = 'block';
    } else {
        field.element.style.borderColor = 'green';
        errorDiv.style.display = 'none';
    }
    
    return isValid;
}

function validateEmail(email) {
    // Enhanced email regex pattern
    const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase());
}

// Debounce function to limit how often a function is called
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
