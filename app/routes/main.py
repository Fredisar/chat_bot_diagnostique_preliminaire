# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify
from app import mongo
from app.services.nlp_service import process_symptoms
from app.services.ml_service import predict_disease, get_model_info
import logging

logger = logging.getLogger(__name__)

# Créer le Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Page d'accueil du chatbot.
    Affiche l'interface utilisateur.
    """
    return render_template('index.html')

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint API pour le chatbot.
    
    Reçoit le message de l'utilisateur, le traite et retourne une prédiction.
    
    Request body:
        {
            "message": "J'ai mal à la tête et de la fièvre"
        }
    
    Response:
        {
            "success": true,
            "symptoms": ["headache", "fever"],
            "disease": "Grippe",
            "confidence": 85.5,
            "top_3": [...],
            "message": "Réponse formatée pour l'utilisateur"
        }
    """
    try:
        # 1. Récupérer le message de l'utilisateur
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message manquant'
            }), 400
        
        user_message = data.get('message', '')
        logger.info(f"📩 Message reçu : {user_message}")
        
        # 2. Traiter le message avec NLP
        # process_symptoms extrait les symptômes du texte
        symptoms = process_symptoms(user_message)
        logger.info(f"🔍 Symptômes détectés : {symptoms}")
        
        # 3. Prédire la maladie avec ML
        prediction_result = predict_disease(symptoms)
        
        if not prediction_result.get('success', False):
            # Cas où la prédiction a échoué
            return jsonify({
                'success': False,
                'error': prediction_result.get('error', 'Erreur de prédiction'),
                'message': "Je n'ai pas pu analyser vos symptômes. Pouvez-vous les décrire plus précisément ?",
                'symptoms': symptoms
            })
        
        # 4. Formater la réponse pour l'utilisateur
        disease = prediction_result['disease']
        confidence = prediction_result['confidence']
        top_3 = prediction_result['top_3']
        
        # Créer un message formaté pour l'utilisateur
        formatted_message = f"🔍 **Diagnostic préliminaire :** {disease}\n\n"
        formatted_message += f"📊 **Confiance :** {confidence:.1f}%\n\n"
        
        if len(top_3) > 1:
            formatted_message += "📋 **Autres possibilités :**\n"
            for i, item in enumerate(top_3[1:], 2):
                formatted_message += f"   {i}. {item['disease']} ({item['confidence']:.1f}%)\n"
        
        formatted_message += "\n⚠️ **Important :** Ce diagnostic est préliminaire. "
        formatted_message += "Consultez toujours un médecin pour une confirmation."
        
        # 5. Sauvegarder dans l'historique (MongoDB)
        try:
            history_entry = {
                'user_message': user_message,
                'symptoms': symptoms,
                'prediction': disease,
                'confidence': confidence,
                'timestamp': __import__('datetime').datetime.now()
            }
            mongo.db.history.insert_one(history_entry)
            logger.info("💾 Historique sauvegardé")
        except Exception as e:
            logger.warning(f"⚠️ Erreur sauvegarde historique : {e}")
        
        # 6. Retourner la réponse
        return jsonify({
            'success': True,
            'symptoms': symptoms,
            'disease': disease,
            'confidence': confidence,
            'top_3': top_3,
            'message': formatted_message
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur dans chat() : {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Une erreur s'est produite. Veuillez réessayer."
        }), 500

@main_bp.route('/api/history', methods=['GET'])
def get_history():
    """
    Récupérer l'historique des conversations.
    
    Query params:
        limit (int): Nombre d'entrées à récupérer (défaut: 20)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Récupérer l'historique depuis MongoDB
        history = list(mongo.db.history.find(
            {}, 
            {'_id': 0}  # Exclure _id
        ).sort('timestamp', -1).limit(limit))
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur dans get_history() : {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/model-info', methods=['GET'])
def model_info():
    """
    Obtenir des informations sur le modèle actuel.
    
    Utile pour le débogage et l'administration.
    """
    info = get_model_info()
    return jsonify(info)

# app/routes/main.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import mongo
from app.services.nlp_service import process_symptoms
from app.services.ml_service import predict_disease
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil du chatbot."""
    return render_template('index.html')

@main_bp.route('/api/chat', methods=['POST'])
@login_required  # 🔒 Protection : seul les utilisateurs connectés peuvent utiliser le chatbot
def chat():
    """Endpoint API pour le chatbot."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message manquant'
            }), 400
        
        user_message = data.get('message', '')
        logger.info(f"📩 Message reçu de {current_user.username}: {user_message}")
        
        # Traiter le message avec NLP
        symptoms = process_symptoms(user_message)
        logger.info(f"🔍 Symptômes détectés : {symptoms}")
        
        # Prédire la maladie
        prediction_result = predict_disease(symptoms)
        
        if not prediction_result.get('success', False):
            return jsonify({
                'success': False,
                'error': prediction_result.get('error', 'Erreur de prédiction'),
                'message': "Je n'ai pas pu analyser vos symptômes.",
                'symptoms': symptoms
            })
        
        # Sauvegarder dans l'historique de l'utilisateur
        current_user.save_chat_history(
            message=user_message,
            symptoms=symptoms,
            prediction=prediction_result['disease'],
            confidence=prediction_result['confidence']
        )
        
        # Formater la réponse
        disease = prediction_result['disease']
        confidence = prediction_result['confidence']
        top_3 = prediction_result['top_3']
        
        formatted_message = f"🔍 **Diagnostic préliminaire :** {disease}\n\n"
        formatted_message += f"📊 **Confiance :** {confidence:.1f}%\n\n"
        
        if len(top_3) > 1:
            formatted_message += "📋 **Autres possibilités :**\n"
            for i, item in enumerate(top_3[1:], 2):
                formatted_message += f"   {i}. {item['disease']} ({item['confidence']:.1f}%)\n"
        
        formatted_message += "\n⚠️ **Important :** Ce diagnostic est préliminaire. "
        formatted_message += "Consultez toujours un médecin pour une confirmation."
        
        return jsonify({
            'success': True,
            'symptoms': symptoms,
            'disease': disease,
            'confidence': confidence,
            'top_3': top_3,
            'message': formatted_message
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur dans chat() : {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Une erreur s'est produite. Veuillez réessayer."
        }), 500