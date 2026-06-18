# app/models/user.py
from flask_login import UserMixin
from app import mongo
from bson import ObjectId
from datetime import datetime
import bcrypt

class User(UserMixin):
    """
    Classe représentant un utilisateur.
    Hérite de UserMixin pour Flask-Login.
    """
    
    def __init__(self, user_data):
        """
        Initialiser un utilisateur à partir des données MongoDB.
        
        Args:
            user_data (dict): Données de l'utilisateur depuis MongoDB
        """
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        # ⚠️ NE PAS utiliser self.is_active car c'est une propriété de UserMixin
        self._is_active = user_data.get('is_active', True)  # Utiliser un attribut privé
        self.is_admin = user_data.get('is_admin', False)
        self.total_queries = user_data.get('total_queries', 0)
        self.preferences = user_data.get('preferences', {})
    
    # ✅ Surcharger la propriété is_active de UserMixin
    @property
    def is_active(self):
        """Retourne True si l'utilisateur est actif."""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Définir l'état actif de l'utilisateur."""
        self._is_active = value
    
    @staticmethod
    def create_user(username, email, password):
        """
        Créer un nouvel utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            email (str): Email
            password (str): Mot de passe en clair
            
        Returns:
            User: Objet utilisateur créé
        """
        # Hasher le mot de passe
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now(),
            'last_login': None,
            'is_active': True,  # ✅ On stocke dans la base
            'is_admin': False,
            'total_queries': 0,
            'preferences': {}
        }
        
        # Insérer dans MongoDB
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        return User(user_data)
    
    @staticmethod
    def get_by_id(user_id):
        """
        Trouver un utilisateur par son ID.
        
        Args:
            user_id (str): ID de l'utilisateur
            
        Returns:
            User: Objet utilisateur ou None
        """
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_username(username):
        """
        Trouver un utilisateur par son nom d'utilisateur.
        
        Args:
            username (str): Nom d'utilisateur
            
        Returns:
            User: Objet utilisateur ou None
        """
        user_data = mongo.db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        """
        Trouver un utilisateur par son email.
        
        Args:
            email (str): Email
            
        Returns:
            User: Objet utilisateur ou None
        """
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    def check_password(self, password):
        """
        Vérifier si le mot de passe est correct.
        
        Args:
            password (str): Mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe correspond
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
    def update_last_login(self):
        """Mettre à jour la date de dernière connexion."""
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'last_login': datetime.now()}}
        )
        self.last_login = datetime.now()
    
    def increment_queries(self):
        """Incrémenter le nombre de requêtes de l'utilisateur."""
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$inc': {'total_queries': 1}}
        )
        self.total_queries += 1
    
    def save_chat_history(self, message, symptoms, prediction, confidence):
        """
        Sauvegarder une interaction du chatbot dans l'historique de l'utilisateur.
        
        Args:
            message (str): Message de l'utilisateur
            symptoms (list): Symptômes détectés
            prediction (str): Maladie prédite
            confidence (float): Confiance de la prédiction
        """
        history_entry = {
            'user_id': ObjectId(self.id),
            'username': self.username,
            'message': message,
            'symptoms': symptoms,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': datetime.now()
        }
        mongo.db.chat_history.insert_one(history_entry)
        
        # Incrémenter le compteur
        self.increment_queries()
    
    def get_history(self, limit=50):
        """
        Récupérer l'historique des conversations de l'utilisateur.
        
        Args:
            limit (int): Nombre maximum d'entrées
            
        Returns:
            list: Liste des entrées d'historique
        """
        history = list(mongo.db.chat_history.find(
            {'user_id': ObjectId(self.id)},
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
        
        return history
    
    def get_stats(self):
        """
        Obtenir les statistiques de l'utilisateur.
        
        Returns:
            dict: Statistiques
        """
        total_queries = mongo.db.chat_history.count_documents(
            {'user_id': ObjectId(self.id)}
        )
        
        # Compter les maladies les plus fréquentes
        pipeline = [
            {'$match': {'user_id': ObjectId(self.id)}},
            {'$group': {
                '_id': '$prediction',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        top_diseases = list(mongo.db.chat_history.aggregate(pipeline))
        
        return {
            'total_queries': total_queries,
            'top_diseases': top_diseases
        }
    
    # ✅ Méthodes supplémentaires utiles
    def deactivate(self):
        """Désactiver l'utilisateur."""
        self._is_active = False
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_active': False}}
        )
    
    def activate(self):
        """Activer l'utilisateur."""
        self._is_active = True
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_active': True}}
        )