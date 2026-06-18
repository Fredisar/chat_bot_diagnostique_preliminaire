# app/__init__.py
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Initialiser les extensions
mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/chatbot_medical')
    
    # Logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialiser MongoDB
    mongo.init_app(app)
    
    # Configurer Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Enregistrer les Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
    # Initialiser le modèle ML
    with app.app_context():
        try:
            from app.services.ml_service import initialize_model
            initialize_model()
        except Exception as e:
            app.logger.error(f"❌ Erreur d'initialisation du modèle : {e}")
    
    return app

# User loader pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Charger un utilisateur à partir de son ID."""
    from app.models.user import User
    return User.get_by_id(user_id)