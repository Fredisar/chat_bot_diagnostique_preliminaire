# app/services/ml_service.py
from app.models.disease_model import DiseasePredictor
from app.services.translations import translate_disease, translate_symptoms
import logging
import os

logger = logging.getLogger(__name__)

predictor = DiseasePredictor()
model_loaded = False

def initialize_model():
    """Initialiser le modèle au démarrage de l'application."""
    global model_loaded
    
    logger.info("🔄 Initialisation du modèle de prédiction...")
    
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
    
    logger.info("🆕 Aucun modèle trouvé - Entraînement en cours...")
    
    dataset_path = 'data/training_cleaned.csv'
    if not os.path.exists(dataset_path):
        logger.error(f"❌ Fichier de données introuvable : {dataset_path}")
        return False
    
    try:
        results = predictor.train_pipeline(dataset_path)
        model_loaded = True
        logger.info(f"✅ Modèle entraîné avec précision : {results['accuracy']*100:.2f}%")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'entraînement : {e}")
        return False

def predict_disease(symptoms):
    """
    Prédire la maladie à partir des symptômes avec traduction en français.
    """
    global model_loaded
    
    if not model_loaded:
        logger.warning("⚠️ Le modèle n'est pas initialisé - tentative d'initialisation")
        if not initialize_model():
            return {
                'success': False,
                'error': 'Le modèle n\'est pas disponible'
            }
    
    if not symptoms:
        return {
            'success': False,
            'error': 'Aucun symptôme détecté',
            'message': 'Veuillez décrire plus précisément vos symptômes.'
        }
    
    try:
        # Faire la prédiction
        prediction = predictor.predict_disease(symptoms)
        
        # Traduire le nom de la maladie
        disease_fr = translate_disease(prediction['disease'])
        
        # Traduire les symptômes
        symptoms_fr = translate_symptoms(symptoms)
        
        # Traduire les top 3
        top_3_translated = []
        for item in prediction['top_3']:
            top_3_translated.append({
                'disease': translate_disease(item['disease']),
                'confidence': item['confidence']
            })
        
        return {
            'success': True,
            'disease': disease_fr,
            'disease_en': prediction['disease'],  # Garder l'original pour référence
            'confidence': prediction['confidence'],
            'top_3': top_3_translated,
            'symptoms_detected': symptoms_fr
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_model_info():
    """Obtenir des informations sur le modèle chargé."""
    if not model_loaded or not predictor.is_trained:
        return {
            'is_loaded': False,
            'message': 'Le modèle n\'est pas chargé'
        }
    
    n_symptoms = len(predictor.symptom_columns) if predictor.symptom_columns else 0
    n_diseases = len(predictor.disease_classes) if predictor.disease_classes else 0
    
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