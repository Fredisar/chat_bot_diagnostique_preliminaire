# app/services/translations.py
"""
Dictionnaire de traduction des maladies de l'anglais vers le français
"""

DISEASE_TRANSLATIONS = {
    # Maladies courantes
    'Fungal infection': 'Infection fongique',
    'Allergy': 'Allergie',
    'GERD': 'Reflux gastro-œsophagien',
    'Chronic cholestasis': 'Cholestase chronique',
    'Drug Reaction': 'Réaction médicamenteuse',
    'Peptic ulcer disease': 'Ulcère gastroduodénal',
    'AIDS': 'SIDA',
    'Diabetes': 'Diabète',
    'Gastroenteritis': 'Gastro-entérite',
    'Bronchial Asthma': 'Asthme bronchique',
    'Hypertension': 'Hypertension',
    'Migraine': 'Migraine',
    'Cervical spondylosis': 'Spondylose cervicale',
    'Paralysis (brain hemorrhage)': 'Paralysie (hémorragie cérébrale)',
    'Jaundice': 'Jaunisse',
    'Malaria': 'Paludisme',
    'Chicken pox': 'Varicelle',
    'Dengue': 'Dengue',
    'Typhoid': 'Fièvre typhoïde',
    'hepatitis A': 'Hépatite A',
    'Hepatitis B': 'Hépatite B',
    'Hepatitis C': 'Hépatite C',
    'Hepatitis D': 'Hépatite D',
    'Hepatitis E': 'Hépatite E',
    'Alcoholic hepatitis': 'Hépatite alcoolique',
    'Tuberculosis': 'Tuberculose',
    'Common Cold': 'Rhume',
    'Pneumonia': 'Pneumonie',
    'Dimorphic hemorrhoids(piles)': 'Hémorroïdes',
    'Heart attack': 'Crise cardiaque',
    'Varicose veins': 'Varices',
    'Hypothyroidism': 'Hypothyroïdie',
    'Hyperthyroidism': 'Hyperthyroïdie',
    'Hypoglycemia': 'Hypoglycémie',
    'Osteoarthristis': 'Arthrose',
    'Arthritis': 'Arthrite',
    'Vertigo': 'Vertige',
    'Acne': 'Acné',
    'Urinary tract infection': 'Infection urinaire',
    'Psoriasis': 'Psoriasis',
    'Impetigo': 'Impétigo',
    
    # Symptômes (pour les retours utilisateur)
    'itching': 'Démangeaison',
    'skin_rash': 'Éruption cutanée',
    'nodal_skin_eruptions': 'Éruptions nodulaires',
    'continuous_sneezing': 'Éternuements continus',
    'shivering': 'Frissons',
    'chills': 'Frissons',
    'joint_pain': 'Douleur articulaire',
    'stomach_pain': 'Douleur d\'estomac',
    'acidity': 'Acidité',
    'ulcers_on_tongue': 'Ulcères sur la langue',
    'cough': 'Toux',
    'fever': 'Fièvre',
    'headache': 'Mal de tête',
    'fatigue': 'Fatigue',
    'nausea': 'Nausée',
    'vomiting': 'Vomissement',
    'breathlessness': 'Essoufflement',
    'runny_nose': 'Nez qui coule',
    'sore_throat': 'Mal de gorge',
    'muscle_pain': 'Douleur musculaire',
}

def translate_disease(disease_name):
    """
    Traduire un nom de maladie de l'anglais vers le français
    
    Args:
        disease_name (str): Nom de la maladie en anglais
        
    Returns:
        str: Nom traduit en français
    """
    if not disease_name:
        return disease_name
    
    # Traduction exacte
    if disease_name in DISEASE_TRANSLATIONS:
        return DISEASE_TRANSLATIONS[disease_name]
    
    # Si pas de traduction, retourner le nom original
    return disease_name

def translate_symptoms(symptoms_list):
    """
    Traduire une liste de symptômes de l'anglais vers le français
    
    Args:
        symptoms_list (list): Liste des symptômes en anglais
        
    Returns:
        list: Liste des symptômes traduits en français
    """
    if not symptoms_list:
        return []
    
    translated = []
    for symptom in symptoms_list:
        if symptom in DISEASE_TRANSLATIONS:
            translated.append(DISEASE_TRANSLATIONS[symptom])
        else:
            translated.append(symptom)
    
    return translated