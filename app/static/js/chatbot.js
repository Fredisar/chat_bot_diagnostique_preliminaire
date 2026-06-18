// app/static/js/chatbot.js

/**
 * Envoyer un message au chatbot
 */
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) {
        // Si le message est vide, on ne fait rien
        return;
    }
    
    // Désactiver le bouton pendant l'envoi
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi...';
    
    // Ajouter le message de l'utilisateur
    addMessage(message, 'user');
    input.value = '';
    
    // Afficher l'indicateur de chargement
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading';
    loadingDiv.id = 'loadingMessage';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';
    document.getElementById('chatMessages').appendChild(loadingDiv);
    scrollToBottom();
    
    try {
        // Envoyer la requête au serveur
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Supprimer l'indicateur de chargement
        const loadingMsg = document.getElementById('loadingMessage');
        if (loadingMsg) loadingMsg.remove();
        
        if (data.success) {
            // Afficher la réponse du bot avec mise en forme
            addMessage(data.message, 'bot');
        } else {
            addMessage("❌ Désolé, une erreur s'est produite. Veuillez réessayer.", 'bot');
            if (data.error) {
                console.error("Erreur:", data.error);
            }
        }
    } catch (error) {
        // Supprimer l'indicateur de chargement
        const loadingMsg = document.getElementById('loadingMessage');
        if (loadingMsg) loadingMsg.remove();
        
        addMessage("❌ Erreur de connexion. Vérifiez votre réseau.", 'bot');
        console.error("Erreur:", error);
    } finally {
        // Réactiver le bouton
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Envoyer';
        input.focus();
    }
}

/**
 * Ajouter un message dans le chat
 */
function addMessage(text, sender) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Si c'est un message du bot, on formate le texte (markdown simple)
    if (sender === 'bot') {
        // Remplacer les **texte** par du gras
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Remplacer les sauts de ligne par des <br>
        formattedText = formattedText.replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedText;
    } else {
        messageDiv.textContent = text;
    }
    
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Faire défiler le chat vers le bas
 */
function scrollToBottom() {
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * Envoyer avec la touche Entrée
 */
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    
    // Vérifier si les éléments existent
    if (!input || !sendButton) {
        console.error("❌ Éléments du chat introuvables !");
        return;
    }
    
    // Gérer la touche Entrée
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Gérer le clic sur le bouton
    sendButton.addEventListener('click', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Focus sur l'input au chargement
    input.focus();
    
    console.log("✅ Chatbot initialisé !");
});