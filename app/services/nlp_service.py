# app/services/nlp_service.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import logging

logger = logging.getLogger(__name__)

# 1. Télécharger les ressources NLTK (une seule fois)
# NLTK a besoin de données pour fonctionner
# punkt = modèle de tokenisation pour le français
# stopwords = liste des mots inutiles (le, la, de, etc.)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("📥 Téléchargement des ressources NLTK...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

# 2. Initialiser le stemmer pour le français
# Le stemming réduit les mots à leur racine
# Exemple : "douleur" -> "doul", "douloureux" -> "doul"
stemmer = SnowballStemmer('french')

# 3. Dictionnaire de mapping : français -> anglais (pour le dataset)
# Notre dataset est en anglais, donc on doit traduire les symptômes
SYMPTOM_MAPPING = {
    # Symptômes dermatologiques
    'démangeaison': 'itching',
    'démangeaisons': 'itching',
    'grattage': 'itching',
    'éruption cutanée': 'skin_rash',
    'rougeur': 'skin_rash',
    'bouton': 'skin_rash',
    
    # Symptômes respiratoires
    'éternuement': 'continuous_sneezing',
    'éternuements': 'continuous_sneezing',
    'toux': 'cough',
    'tousse': 'cough',
    'respiration': 'breathlessness',
    'essoufflement': 'breathlessness',
    'nez qui coule': 'runny_nose',
    'rhume': 'runny_nose',
    'congestion': 'congestion',
    
    # Symptômes généraux
    'fièvre': 'fever',
    'frisson': 'chills',
    'frissons': 'chills',
    'fatigue': 'fatigue',
    'épuisement': 'fatigue',
    'nausée': 'nausea',
    'nausées': 'nausea',
    'vomissement': 'vomiting',
    'vomissements': 'vomiting',
    
    # Douleurs
    'douleur': 'pain',
    'douleurs': 'pain',
    'mal': 'pain',
    'maux': 'pain',
    'articulation': 'joint_pain',
    'articulations': 'joint_pain',
    'muscle': 'muscle_pain',
    'musculaire': 'muscle_pain',
    'tête': 'headache',
    'céphalée': 'headache',
    'migraine': 'headache',
    'ventre': 'stomach_pain',
    'estomac': 'stomach_pain',
    
    # Symptômes digestifs
    'acidité': 'acidity',
    'brûlure': 'acidity',
    'ulcère': 'ulcers_on_tongue',
    'aphte': 'ulcers_on_tongue',
    'diarrhée': 'diarrhoea',
    'constipation': 'constipation',
    
    # Symptômes cutanés
    'peau': 'skin_rash',
    'éruption': 'skin_rash',
    'bouton': 'nodal_skin_eruptions',
    
    # Ajoutez d'autres mappings selon vos besoins
}

# 4. Liste des mots de symptômes pour la détection
# On extrait les clés du mapping pour faciliter la recherche
SYMPTOM_KEYWORDS = list(SYMPTOM_MAPPING.keys())

def preprocess_text(text):
    """
    Nettoyer et préparer le texte pour l'analyse.
    
    Étapes :
    1. Mettre en minuscules
    2. Supprimer la ponctuation
    3. Séparer en mots (tokenization)
    4. Supprimer les mots inutiles (stopwords)
    5. Réduire les mots à leur racine (stemming)
    
    Args:
        text (str): Texte brut de l'utilisateur
        
    Returns:
        list: Liste des mots prétraités
    """
    logger.debug(f"📝 Prétraitement du texte : {text}")
    
    # Étape 1 : Mettre en minuscules
    # Tous les mots en minuscules pour uniformiser
    text = text.lower()
    
    # Étape 2 : Supprimer la ponctuation
    # On garde uniquement les lettres, chiffres et espaces
    # re.sub() remplace tout ce qui n'est pas un mot par une espace
    text = re.sub(r'[^\w\s]', '', text)
    
    # Étape 3 : Tokenization
    # word_tokenize() divise le texte en mots
    # Exemple : "J'ai mal à la tête" -> ['J'ai', 'mal', 'à', 'la', 'tête']
    tokens = word_tokenize(text, language='french')
    
    # Étape 4 : Supprimer les stopwords
    # Les stopwords sont des mots qui n'ajoutent pas de sens
    # Exemple : 'le', 'la', 'de', 'à', etc.
    stop_words = set(stopwords.words('french'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Étape 5 : Stemming
    # On réduit les mots à leur racine
    # Exemple : 'douleur' et 'douloureux' deviennent 'doul'
    tokens = [stemmer.stem(token) for token in tokens]
    
    logger.debug(f"✅ Mots extraits : {tokens}")
    return tokens

def extract_symptoms(text):
    """
    Extraire les symptômes du texte de l'utilisateur.
    
    Comment ça marche ?
    1. On prétraite le texte
    2. On regarde quels mots correspondent à des symptômes
    3. On les traduit en anglais pour le modèle
    
    Args:
        text (str): Texte de l'utilisateur
        
    Returns:
        list: Liste des symptômes en anglais
    """
    # Étape 1 : Prétraiter le texte
    tokens = preprocess_text(text)
    
    # Étape 2 : Détecter les symptômes
    detected_symptoms = []
    
    # Pour chaque mot, vérifier s'il correspond à un symptôme
    for token in tokens:
        # Vérifier si le token est un symptôme connu
        if token in SYMPTOM_KEYWORDS:
            # Traduire en anglais
            english_symptom = SYMPTOM_MAPPING[token]
            detected_symptoms.append(english_symptom)
        else:
            # Vérifier si un symptôme est contenu dans le token
            for symptom_fr, symptom_en in SYMPTOM_MAPPING.items():
                # Exemple : si "douleur" est dans "douloureux"
                if symptom_fr in token or token in symptom_fr:
                    detected_symptoms.append(symptom_en)
                    break
    
    # Étape 3 : Supprimer les doublons
    # Un symptôme peut être détecté plusieurs fois
    detected_symptoms = list(set(detected_symptoms))
    
    logger.info(f"🔍 Symptômes détectés : {detected_symptoms}")
    return detected_symptoms

def process_symptoms(user_message):
    """
    Fonction principale pour traiter le message de l'utilisateur.
    
    C'est celle qui sera appelée par la route Flask.
    
    Args:
        user_message (str): Message de l'utilisateur
        
    Returns:
        list: Liste des symptômes détectés
    """
    # Vider le message des mots inutiles et extraire les symptômes
    symptoms = extract_symptoms(user_message)
    
    # Si aucun symptôme n'est détecté, retourner une liste vide
    if not symptoms:
        logger.warning("⚠️ Aucun symptôme détecté dans le message")
    
    return symptoms

# Fonction supplémentaire pour améliorer la détection
def get_symptom_context(symptoms_list):
    """
    Obtenir le contexte pour chaque symptôme détecté.
    
    Utile pour savoir où se situe le symptôme dans le corps.
    
    Args:
        symptoms_list (list): Liste des symptômes
        
    Returns:
        dict: Contextes des symptômes
    """
    context = {}
    symptom_categories = {
        'skin': ['itching', 'skin_rash', 'nodal_skin_eruptions'],
        'respiratory': ['cough', 'breathlessness', 'runny_nose', 'congestion'],
        'general': ['fever', 'chills', 'fatigue', 'sweating'],
        'digestive': ['nausea', 'vomiting', 'stomach_pain', 'acidity'],
        'pain': ['headache', 'joint_pain', 'muscle_pain', 'stomach_pain'],
        'neurological': ['dizziness', 'headache', 'nausea']
    }
    
    for symptom in symptoms_list:
        for category, symptoms in symptom_categories.items():
            if symptom in symptoms:
                context[symptom] = category
                break
    
    return context