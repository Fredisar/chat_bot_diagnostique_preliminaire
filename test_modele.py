# test_model.py
"""
Script de test pour vérifier que le modèle fonctionne correctement.
Exécutez ce fichier indépendamment avant de lancer Flask.
"""

from app.models.disease_model import DiseasePredictor
from app.services.nlp_service import process_symptoms
import logging

logging.basicConfig(level=logging.INFO)

def test_model():
    print("=" * 60)
    print("🧪 TEST DU MODÈLE DE PRÉDICTION")
    print("=" * 60)
    
    # 1. Créer le prédicteur
    predictor = DiseasePredictor()
    
    # 2. Entraîner le modèle
    print("\n📚 Entraînement du modèle...")
    results = predictor.train_pipeline('data/training_cleaned.csv')
    
    print(f"\n✅ Précision : {results['accuracy']*100:.2f}%")
    
    # 3. Tester avec différents messages
    test_messages = [
        "J'ai des démangeaisons et une éruption cutanée",
        "J'ai de la fièvre, des frissons et mal à la tête",
        "Je tousse beaucoup et j'ai du mal à respirer",
        "J'ai mal au ventre et des nausées",
        "Je suis très fatigué et j'ai des courbatures"
    ]
    
    print("\n" + "=" * 60)
    print("🔬 TESTS DE PRÉDICTION")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i} : {message}")
        
        # Extraire les symptômes
        symptoms = process_symptoms(message)
        print(f"   Symptômes détectés : {symptoms}")
        
        # Prédire
        if symptoms:
            prediction = predictor.predict_disease(symptoms)
            print(f"   Maladie : {prediction['disease']}")
            print(f"   Confiance : {prediction['confidence']:.1f}%")
            
            if len(prediction['top_3']) > 1:
                print("   Top 3 :")
                for j, item in enumerate(prediction['top_3'], 1):
                    print(f"      {j}. {item['disease']} ({item['confidence']:.1f}%)")
        else:
            print("   ⚠️ Aucun symptôme détecté")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés !")

if __name__ == "__main__":
    test_model()