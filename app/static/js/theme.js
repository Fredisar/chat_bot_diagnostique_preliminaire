/**
 * Gestion du thème (clair/sombre)
 */
(function() {
    'use strict';
    
    // Récupérer le thème sauvegardé ou utiliser le thème système
    const getPreferredTheme = () => {
        const saved = localStorage.getItem('theme');
        if (saved) return saved;
        
        // Vérifier le thème système
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    };
    
    // Appliquer le thème
    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Mettre à jour l'icône du bouton
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                toggle.title = 'Passer en mode clair';
            } else {
                icon.className = 'fas fa-moon';
                toggle.title = 'Passer en mode sombre';
            }
        }
    };
    
    // Basculer le thème
    const toggleTheme = () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    };
    
    // Initialiser
    document.addEventListener('DOMContentLoaded', function() {
        const theme = getPreferredTheme();
        setTheme(theme);
        
        // Ajouter l'écouteur d'événement
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', toggleTheme);
        }
        
        // Écouter les changements de thème système
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    });
})();