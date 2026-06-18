# run.py
from app import create_app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Lancer le serveur Flask
    # debug=True : rechargement automatique et messages d'erreur détaillés
    app.run(debug=True, host='0.0.0.0', port=5000)