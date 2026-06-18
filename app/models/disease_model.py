# app/models/disease_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import logging

# Configuration du logging pour suivre ce qui se passe
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiseasePredictor:
    """
    Classe qui encapsule tout le processus de prédiction des maladies.
    
    Elle fait 3 choses principales :
    1. Charger et préparer les données
    2. Entraîner un modèle de machine learning
    3. Faire des prédictions sur de nouveaux symptômes
    """
    
    def __init__(self):
        """
        Constructeur de la classe.
        Initialise les attributs qui seront utilisés plus tard.
        """
        # self.model : le classifieur RandomForest
        self.model = None
        
        # self.label_encoder : convertit les noms des maladies en nombres
        # Exemple : "Grippe" -> 0, "Rhume" -> 1, etc.
        self.label_encoder = LabelEncoder()
        
        # self.symptom_columns : liste des noms des colonnes de symptômes
        # Exemple : ['itching', 'skin_rash', 'nodal_skin_eruptions', ...]
        self.symptom_columns = None
        
        # self.disease_classes : liste des noms des maladies
        # Exemple : ['Fungal infection', 'Allergy', 'GERD', ...]
        self.disease_classes = None
        
        # self.feature_importance : importance de chaque symptôme
        self.feature_importance = None
        
        # self.is_trained : indicateur si le modèle est entraîné
        self.is_trained = False
    
    def load_data(self, dataset_path='data/training_cleaned.csv'):
        """
        Charger les données depuis un fichier CSV.
        
        Args:
            dataset_path (str): Chemin vers le fichier CSV
            
        Returns:
            X (DataFrame): Les symptômes (variables indépendantes)
            y (Series): Les maladies (variable cible)
        """
        logger.info(f"📂 Chargement des données depuis {dataset_path}")
        
        # 1. Charger le CSV avec pandas
        # pd.read_csv() lit le fichier et crée un DataFrame
        df = pd.read_csv(dataset_path)
        logger.info(f"✅ Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # 2. Identifier les colonnes de symptômes
        # On prend toutes les colonnes SAUF la dernière ('prognosis')
        # df.columns[:-1] = toutes les colonnes sauf la dernière
        self.symptom_columns = df.columns[:-1].tolist()
        logger.info(f"📋 {len(self.symptom_columns)} symptômes détectés")
        
        # 3. Séparer les variables
        # X contient les symptômes (entrées du modèle)
        # y contient les maladies (sorties du modèle)
        X = df[self.symptom_columns]
        y = df.iloc[:, -1]  # Dernière colonne = 'prognosis'
        
        # 4. Enregistrer les noms des maladies pour plus tard
        self.disease_classes = y.unique().tolist()
        logger.info(f"🏥 {len(self.disease_classes)} maladies différentes")
        
        return X, y
    
    def preprocess_data(self, X, y):
        """
        Préparer les données pour l'entraînement.
        
        Args:
            X: symptômes
            y: maladies
            
        Returns:
            X_train, X_test, y_train, y_test: Données divisées pour entraînement/test
        """
        logger.info("🔧 Prétraitement des données...")
        
        # 1. Encoder les maladies (texte -> nombres)
        # Les modèles de ML ne peuvent pas travailler avec du texte directement
        # Il faut convertir "Grippe" en 0, "Rhume" en 1, etc.
        y_encoded = self.label_encoder.fit_transform(y)
        logger.info(f"✅ Maladies encodées : {len(self.label_encoder.classes_)} classes")
        
        # 2. Diviser en ensemble d'entraînement et de test
        # train_test_split : sépare les données aléatoirement
        # test_size=0.2 : 20% des données pour le test
        # random_state=42 : pour que la division soit reproductible
        X_train, X_test, y_train, y_test = train_test_split(
            X, 
            y_encoded, 
            test_size=0.2, 
            random_state=42,
            stratify=y_encoded  # Garde la même proportion de maladies dans train et test
        )
        
        logger.info(f"✅ Division : {len(X_train)} entraînement, {len(X_test)} test")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train, y_train):
        """
        Entraîner le modèle Random Forest.
        
        Random Forest est un ensemble d'arbres de décision.
        Chaque arbre vote et la classe la plus votée est choisie.
        
        Args:
            X_train: symptômes d'entraînement
            y_train: maladies encodées d'entraînement
        """
        logger.info("🌳 Entraînement du modèle Random Forest...")
        
        # Créer le modèle Random Forest
        # n_estimators=100 : 100 arbres de décision
        # max_depth=20 : profondeur maximale de chaque arbre (limite la complexité)
        # random_state=42 : pour reproductibilité
        # n_jobs=-1 : utilise tous les processeurs disponibles
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        # Entraîner le modèle
        # fit() = apprendre à partir des données
        self.model.fit(X_train, y_train)
        
        # Enregistrer l'importance des caractéristiques
        # feature_importances_ : quel symptôme est le plus important pour la prédiction
        self.feature_importance = pd.DataFrame({
            'symptom': self.symptom_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.is_trained = True
        logger.info("✅ Modèle entraîné avec succès")
    
    def evaluate_model(self, X_test, y_test):
        """
        Évaluer les performances du modèle sur les données de test.
        
        Args:
            X_test: symptômes de test
            y_test: maladies encodées de test
            
        Returns:
            dict: Métriques de performance
        """
        logger.info("📊 Évaluation du modèle...")
        
        # 1. Faire des prédictions
        y_pred = self.model.predict(X_test)
        
        # 2. Calculer la précision
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"✅ Précision : {accuracy*100:.2f}%")
        
        # 3. Afficher le rapport de classification détaillé
        # Affiche précision, rappel, F1-score par classe
        report = classification_report(
            y_test, 
            y_pred, 
            target_names=self.label_encoder.classes_
        )
        print("\n📋 Rapport de classification :")
        print(report)
        
        # 4. Matrice de confusion
        # Montre combien de fois chaque classe a été confondue
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm
        }
    
    def predict_disease(self, symptoms_list):
        """
        Prédire la maladie à partir d'une liste de symptômes.
        
        C'est la fonction principale que notre chatbot va utiliser.
        
        Args:
            symptoms_list (list): Liste des symptômes détectés
                                  Exemple : ['itching', 'skin_rash']
            
        Returns:
            dict: Résultat de la prédiction avec maladie et probabilités
        """
        if not self.is_trained:
            raise ValueError("⚠️ Le modèle n'est pas entraîné !")
        
        if not symptoms_list:
            return {
                'disease': 'Aucun symptôme détecté',
                'confidence': 0,
                'top_3': []
            }
        
        # 1. Créer un vecteur de symptômes (valeurs 0 ou 1)
        # On initialise un tableau de zéros de la même taille que le nombre de symptômes
        symptom_vector = np.zeros(len(self.symptom_columns))
        
        # Pour chaque symptôme détecté, on met 1 à la position correspondante
        for i, symptom in enumerate(self.symptom_columns):
            if symptom in symptoms_list:
                symptom_vector[i] = 1
        
        # 2. Faire la prédiction
        # model.predict([symptom_vector]) retourne la classe prédite
        prediction = self.model.predict([symptom_vector])[0]
        
        # 3. Convertir le nombre en nom de maladie
        disease = self.label_encoder.inverse_transform([prediction])[0]
        
        # 4. Obtenir les probabilités pour chaque maladie
        # predict_proba() retourne les probabilités pour chaque classe
        probabilities = self.model.predict_proba([symptom_vector])[0]
        confidence = max(probabilities) * 100
        
        # 5. Obtenir les 3 maladies les plus probables
        # argsort trie les indices par valeurs croissantes
        # [::-1] inverse pour avoir les plus grandes en premier
        top_indices = np.argsort(probabilities)[-3:][::-1]
        
        top_3 = []
        for idx in top_indices:
            disease_name = self.label_encoder.inverse_transform([idx])[0]
            prob = probabilities[idx] * 100
            top_3.append({
                'disease': disease_name,
                'confidence': prob
            })
        
        return {
            'disease': disease,
            'confidence': confidence,
            'top_3': top_3
        }
    
    def save_model(self, model_path='models/disease_model.joblib'):
        """
        Sauvegarder le modèle entraîné pour une utilisation ultérieure.
        
        Args:
            model_path (str): Chemin où sauvegarder le modèle
        """
        if not self.is_trained:
            raise ValueError("⚠️ Le modèle doit être entraîné avant d'être sauvegardé")
        
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Sauvegarder le modèle, l'encodeur et les colonnes
        # joblib est plus efficace que pickle pour les modèles ML
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder,
            'symptom_columns': self.symptom_columns,
            'disease_classes': self.disease_classes,
            'feature_importance': self.feature_importance
        }, model_path)
        
        logger.info(f"💾 Modèle sauvegardé dans {model_path}")
    
    def load_model(self, model_path='models/disease_model.joblib'):
        """
        Charger un modèle pré-entraîné.
        
        Args:
            model_path (str): Chemin du modèle à charger
            
        Returns:
            bool: True si chargé avec succès
        """
        try:
            # Charger le dictionnaire sauvegardé
            saved_data = joblib.load(model_path)
            
            # Restaurer les attributs
            self.model = saved_data['model']
            self.label_encoder = saved_data['label_encoder']
            self.symptom_columns = saved_data['symptom_columns']
            self.disease_classes = saved_data['disease_classes']
            
            if 'feature_importance' in saved_data:
                self.feature_importance = saved_data['feature_importance']
            
            self.is_trained = True
            logger.info(f"✅ Modèle chargé depuis {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle : {e}")
            return False
    
    def train_pipeline(self, dataset_path='data/training_cleaned.csv'):
        """
        Pipeline complet d'entraînement.
        
        C'est la fonction qui exécute toutes les étapes :
        1. Charger les données
        2. Les préparer
        3. Entraîner le modèle
        4. Évaluer le modèle
        5. Sauvegarder le modèle
        
        Args:
            dataset_path (str): Chemin du dataset
            
        Returns:
            dict: Résultats de l'évaluation
        """
        logger.info("🚀 Début du pipeline d'entraînement...")
        
        # Étape 1 : Charger les données
        X, y = self.load_data(dataset_path)
        
        # Étape 2 : Prétraiter les données
        X_train, X_test, y_train, y_test = self.preprocess_data(X, y)
        
        # Étape 3 : Entraîner le modèle
        self.train_model(X_train, y_train)
        
        # Étape 4 : Évaluer le modèle
        results = self.evaluate_model(X_test, y_test)
        
        # Étape 5 : Sauvegarder le modèle
        self.save_model()
        
        logger.info("✅ Pipeline terminé !")
        return results