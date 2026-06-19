/**
 * Basculer l'affichage du mot de passe
 */
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.password-toggle');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

/**
 * Fermer automatiquement les messages flash après 5 secondes
 */
document.addEventListener('DOMContentLoaded', function() {
    // Fermer les messages flash automatiquement
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
    
    // Gérer la fermeture manuelle des messages flash
    const closeButtons = document.querySelectorAll('.flash-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
});

/**
 * Validation du formulaire d'inscription en temps réel
 */
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('.auth-form[action*="register"]');
    if (registerForm) {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (password && confirmPassword) {
            confirmPassword.addEventListener('input', function() {
                if (this.value !== password.value) {
                    this.setCustomValidity('Les mots de passe ne correspondent pas');
                } else {
                    this.setCustomValidity('');
                }
            });
            
            password.addEventListener('input', function() {
                if (this.value.length > 0 && this.value.length < 6) {
                    this.setCustomValidity('Le mot de passe doit contenir au moins 6 caractères');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    }
});

/**
 * Indicateur de force du mot de passe
 */
document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('password');
    if (passwordField) {
        const strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength';
        strengthIndicator.style.cssText = `
            height: 4px;
            border-radius: 2px;
            margin-top: 0.5rem;
            background: #f0f0f0;
            transition: background 0.3s;
        `;
        passwordField.parentElement.appendChild(strengthIndicator);
        
        passwordField.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            const colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60'];
            const messages = ['Très faible', 'Faible', 'Moyen', 'Fort', 'Très fort'];
            
            strengthIndicator.style.width = `${(strength + 1) * 20}%`;
            strengthIndicator.style.background = colors[Math.min(strength, 4)];
            
            // Ajouter un tooltip
            const tooltip = document.querySelector('.password-tooltip');
            if (tooltip) {
                tooltip.textContent = messages[Math.min(strength, 4)];
            } else {
                const tip = document.createElement('small');
                tip.className = 'password-tooltip form-hint';
                tip.textContent = messages[Math.min(strength, 4)];
                strengthIndicator.parentElement.appendChild(tip);
            }
        });
    }
});

/**
 * Vérifier la force du mot de passe
 */
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    return Math.min(strength, 4);
}

/**
 * Gérer la redirection après connexion
 */
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.auth-form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            
            if (!username.value || !password.value) {
                e.preventDefault();
                showFlash('Veuillez remplir tous les champs.', 'error');
            }
        });
    }
});

/**
 * Afficher un message flash personnalisé
 */
function showFlash(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || 
                     document.querySelector('.main-content');
    
    if (container) {
        const flash = document.createElement('div');
        flash.className = `flash flash-${type}`;
        flash.innerHTML = `
            ${message}
            <button class="flash-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.prepend(flash);
        
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    }
}