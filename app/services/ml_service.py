# app/services/ml_service.py
from app.models.disease_model import DiseasePredictor
import logging
import os

logger = logging.getLogger(__name__)

# 1. Créer une instance globale du prédicteur
# Cette instance sera partagée par toute l'application
predictor = DiseasePredictor()
model_loaded = False

def initialize_model():
    """
    Initialiser le modèle au démarrage de l'application.
    
    C'est appelé dans app/__init__.py
    
    Fonctionnement :
    1. Essayer de charger un modèle sauvegardé
    2. Si ça échoue, entraîner un nouveau modèle
    """
    global model_loaded
    
    logger.info("🔄 Initialisation du modèle de prédiction...")
    
    # Étape 1 : Essayer de charger le modèle existant
    model_path = 'models/disease_model.joblib'
    
    if os.path.exists(model_path):
        logger.info("📂 Chargement du modèle existant...")
        try:
            loaded = predictor.load_model(model_path)
            if loaded:
                model_loaded = True
                logger.info("✅ Modèle chargé avec succès")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors du chargement : {e}")
    
    # Étape 2 : Si pas de modèle, en entraîner un nouveau
    logger.info("🆕 Aucun modèle trouvé - Entraînement en cours...")
    
    dataset_path = 'data/training_cleaned.csv'
    if not os.path.exists(dataset_path):
        logger.error(f"❌ Fichier de données introuvable : {dataset_path}")
        return False
    
    try:
        # Lancer le pipeline d'entraînement
        results = predictor.train_pipeline(dataset_path)
        model_loaded = True
        logger.info(f"✅ Modèle entraîné avec précision : {results['accuracy']*100:.2f}%")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'entraînement : {e}")
        return False

def predict_disease(symptoms):
    """
    Prédire la maladie à partir des symptômes.
    
    Cette fonction est appelée par la route Flask.
    
    Args:
        symptoms (list): Liste des symptômes détectés
        
    Returns:
        dict: Résultat de la prédiction
    """
    global model_loaded
    
    # Vérifier que le modèle est disponible
    if not model_loaded:
        logger.warning("⚠️ Le modèle n'est pas initialisé - tentative d'initialisation")
        if not initialize_model():
            return {
                'success': False,
                'error': 'Le modèle n\'est pas disponible'
            }
    
    # Vérifier qu'il y a des symptômes
    if not symptoms:
        return {
            'success': False,
            'error': 'Aucun symptôme détecté',
            'message': 'Veuillez décrire plus précisément vos symptômes.'
        }
    
    try:
        # Faire la prédiction
        prediction = predictor.predict_disease(symptoms)
        
        # Formater le résultat
        return {
            'success': True,
            'disease': prediction['disease'],
            'confidence': prediction['confidence'],
            'top_3': prediction['top_3'],
            'symptoms_detected': symptoms
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_model_info():
    """
    Obtenir des informations sur le modèle chargé.
    
    Utile pour déboguer et comprendre le modèle.
    
    Returns:
        dict: Informations sur le modèle
    """
    if not model_loaded or not predictor.is_trained:
        return {
            'is_loaded': False,
            'message': 'Le modèle n\'est pas chargé'
        }
    
    # Compter le nombre de symptômes et maladies
    n_symptoms = len(predictor.symptom_columns) if predictor.symptom_columns else 0
    n_diseases = len(predictor.disease_classes) if predictor.disease_classes else 0
    
    # Obtenir les 10 symptômes les plus importants
    top_features = []
    if predictor.feature_importance is not None:
        top_features = predictor.feature_importance.head(10).to_dict('records')
    
    return {
        'is_loaded': True,
        'is_trained': predictor.is_trained,
        'n_symptoms': n_symptoms,
        'n_diseases': n_diseases,
        'n_estimators': predictor.model.n_estimators if predictor.model else 0,
        'top_10_important_symptoms': top_features
    }