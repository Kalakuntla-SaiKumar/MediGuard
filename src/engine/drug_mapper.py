"""
Drug Name Mapper
Maps common/brand names to exact names used in the DDI encoder (Title Case)
"""

DRUG_NAME_MAP = {
    # Paracetamol / Acetaminophen
    'paracetamol': 'Acetaminophen',
    'dolo': 'Acetaminophen',
    'crocin': 'Acetaminophen',
    'tylenol': 'Acetaminophen',
    'calpol': 'Acetaminophen',
    'panadol': 'Acetaminophen',
    'febrex': 'Acetaminophen',
    'acetaminophen': 'Acetaminophen',

    # Aspirin
    'aspirin': 'Acetylsalicylic acid',
    'ecosprin': 'Acetylsalicylic acid',
    'disprin': 'Acetylsalicylic acid',
    'acetylsalicylic acid': 'Acetylsalicylic acid',

    # Ibuprofen
    'ibuprofen': 'Ibuprofen',
    'brufen': 'Ibuprofen',
    'advil': 'Ibuprofen',
    'nurofen': 'Ibuprofen',
    'combiflam': 'Ibuprofen',

    # Warfarin
    'warfarin': 'Warfarin',
    'coumadin': 'Warfarin',
    'warf': 'Warfarin',

    # Metformin
    'metformin': 'Metformin',
    'glycomet': 'Metformin',
    'glucophage': 'Metformin',
    'metformin hcl': 'Metformin',

    # Tramadol
    'tramadol': 'Tramadol',
    'ultram': 'Tramadol',
    'tramazac': 'Tramadol',

    # Atorvastatin
    'atorvastatin': 'Atorvastatin',
    'lipitor': 'Atorvastatin',
    'atorva': 'Atorvastatin',

    # Amlodipine
    'amlodipine': 'Amlodipine',
    'norvasc': 'Amlodipine',
    'amlip': 'Amlodipine',

    # Lisinopril
    'lisinopril': 'Lisinopril',
    'prinivil': 'Lisinopril',
    'zestril': 'Lisinopril',

    # Metoprolol
    'metoprolol': 'Metoprolol',
    'lopressor': 'Metoprolol',
    'betaloc': 'Metoprolol',

    # Omeprazole
    'omeprazole': 'Omeprazole',
    'prilosec': 'Omeprazole',
    'omez': 'Omeprazole',

    # Pantoprazole
    'pantoprazole': 'Pantoprazole',
    'pan': 'Pantoprazole',
    'pantop': 'Pantoprazole',

    # Simvastatin
    'simvastatin': 'Simvastatin',
    'zocor': 'Simvastatin',

    # Losartan
    'losartan': 'Losartan',
    'cozaar': 'Losartan',
    'losar': 'Losartan',

    # Amoxicillin
    'amoxicillin': 'Amoxicillin',
    'amoxil': 'Amoxicillin',
    'trimox': 'Amoxicillin',

    # Azithromycin
    'azithromycin': 'Azithromycin',
    'zithromax': 'Azithromycin',
    'azee': 'Azithromycin',
    'azithral': 'Azithromycin',

    # Ciprofloxacin
    'ciprofloxacin': 'Ciprofloxacin',
    'cipro': 'Ciprofloxacin',
    'ciplox': 'Ciprofloxacin',

    # Gabapentin
    'gabapentin': 'Gabapentin',
    'neurontin': 'Gabapentin',
    'gabapin': 'Gabapentin',

    # Sertraline
    'sertraline': 'Sertraline',
    'zoloft': 'Sertraline',
    'serta': 'Sertraline',

    # Fluoxetine
    'fluoxetine': 'Fluoxetine',
    'prozac': 'Fluoxetine',
    'fludac': 'Fluoxetine',

    # Clopidogrel
    'clopidogrel': 'Clopidogrel',
    'plavix': 'Clopidogrel',
    'clopilet': 'Clopidogrel',

    # Insulin
    'insulin': 'Insulin',
    'humulin': 'Insulin',
    'lantus': 'Insulin',

    # Prednisolone
    'prednisolone': 'Prednisolone',
    'wysolone': 'Prednisolone',

    # Dexamethasone
    'dexamethasone': 'Dexamethasone',
    'decadron': 'Dexamethasone',

    # Morphine
    'morphine': 'Morphine',

    # Codeine
    'codeine': 'Codeine',

    # Diazepam
    'diazepam': 'Diazepam',
    'valium': 'Diazepam',

    # Lorazepam
    'lorazepam': 'Lorazepam',
    'ativan': 'Lorazepam',

    # Alprazolam
    'alprazolam': 'Alprazolam',
    'xanax': 'Alprazolam',
    'alprax': 'Alprazolam',

    # Risperidone
    'risperidone': 'Risperidone',
    'risperdal': 'Risperidone',

    # Quetiapine
    'quetiapine': 'Quetiapine',
    'seroquel': 'Quetiapine',

    # Carbamazepine
    'carbamazepine': 'Carbamazepine',
    'tegretol': 'Carbamazepine',
    'mazetol': 'Carbamazepine',

    # Valproic acid
    'valproic acid': 'Valproic acid',
    'depakote': 'Valproic acid',
    'valparin': 'Valproic acid',
    'sodium valproate': 'Valproic acid',
    'valproate': 'Valproic acid',

    # Phenytoin
    'phenytoin': 'Phenytoin',
    'dilantin': 'Phenytoin',
    'eptoin': 'Phenytoin',

    # Lamotrigine
    'lamotrigine': 'Lamotrigine',
    'lamictal': 'Lamotrigine',
    'lamitor': 'Lamotrigine',

    # Levothyroxine
    'levothyroxine': 'Levothyroxine',
    'synthroid': 'Levothyroxine',
    'eltroxin': 'Levothyroxine',
    'thyronorm': 'Levothyroxine',

    # Methotrexate
    'methotrexate': 'Methotrexate',
    'rheumatrex': 'Methotrexate',
    'folitrax': 'Methotrexate',

    # Cyclosporine
    'cyclosporine': 'Cyclosporine',
    'cyclosporin': 'Cyclosporine',
    'neoral': 'Cyclosporine',
    'sandimmune': 'Cyclosporine',

    # Tacrolimus
    'tacrolimus': 'Tacrolimus',
    'prograf': 'Tacrolimus',

    # Digoxin
    'digoxin': 'Digoxin',
    'lanoxin': 'Digoxin',

    # Furosemide
    'furosemide': 'Furosemide',
    'lasix': 'Furosemide',
    'frusemide': 'Furosemide',

    # Spironolactone
    'spironolactone': 'Spironolactone',
    'aldactone': 'Spironolactone',

    # Hydrochlorothiazide
    'hydrochlorothiazide': 'Hydrochlorothiazide',
    'hctz': 'Hydrochlorothiazide',

    # Ramipril
    'ramipril': 'Ramipril',
    'altace': 'Ramipril',
    'cardace': 'Ramipril',

    # Captopril
    'captopril': 'Captopril',
    'capoten': 'Captopril',
}

# Condition name mapping (to dataset format)
CONDITION_NAME_MAP = {
    'high blood pressure': 'hypertension',
    'bp': 'hypertension',
    'fits': 'epilepsy',
    'fit': 'epilepsy',
    'fitting': 'epilepsy',
    'blood cancer': 'leukemia',
    'heart attack': 'myocardial reperfusion injury',
    'heart problem': 'heart failure',
    'heart disease': 'heart diseases',
    'cardiovascular disease': 'heart diseases',
    'irregular heartbeat': 'arrhythmias, cardiac',
    'cardiac arrest': 'arrhythmias, cardiac',
    'liver problem': 'liver diseases',
    'liver damage': 'chemical and drug induced liver injury',
    'fatty liver': 'liver diseases',
    'lung cancer': 'lung neoplasms',
    'stomach cancer': 'stomach neoplasms',
    'skin problem': 'skin diseases',
    'rash': 'skin diseases',
    'swelling': 'edema',
    'water retention': 'edema',
    'lung swelling': 'pulmonary edema',
    'breathlessness': 'acute lung injury',
    'shaking': 'tremor',
    'shivering': 'tremor',
    'weight issues': 'weight gain',
    'obesity': 'weight gain',
    'low blood pressure': 'hypotension',
    'slow heart rate': 'bradycardia',
    'hepatitis': 'hepatitis, chronic',
    'diabetes': 'insulin resistance',
    'high sugar': 'hyperglycemia',
    'blood sugar': 'hyperglycemia',
    'scar tissue': 'fibrosis',
    'pain sensitivity': 'hyperalgesia',
    'back pain': 'scoliosis',
    'spinal problem': 'scoliosis',
    'movement problem': 'movement disorders',
    'parkinsons': 'movement disorders',
    'huntington': 'huntington disease',
    'lymph cancer': 'lymphoma',
    'breast cancer': 'triple negative breast neoplasms',
}


def normalize_drug(name):
    """Map common/brand drug name to exact encoder name"""
    if not name:
        return name
    # Check map first (handles brand names and lowercase)
    lower = name.lower().strip()
    if lower in DRUG_NAME_MAP:
        return DRUG_NAME_MAP[lower]
    # If not in map, try Title Case as fallback
    return name.strip().title()


def normalize_condition(condition: str) -> str:
    """Map common condition names to dataset-compatible medical terms."""
    if not condition:
        return condition

    CONDITION_MAP = {
        # Keep this mapped to `heart diseases` so Warfarin + heart disease resolves in DCI.
        "heart disease": "heart diseases",
        "heart problem": "heart diseases",
        "heart attack": "myocardial infarction",
        "heart failure": "heart failure",
        "high bp": "hypertension",
        "high blood pressure": "hypertension",
        "bp": "hypertension",
        "low blood pressure": "hypotension",
        "irregular heartbeat": "arrhythmias, cardiac",
        "arrhythmia": "arrhythmias, cardiac",
        "chest pain": "angina pectoris",
        "stroke": "stroke",
        "blood clot": "thrombosis",
        "water retention": "edema",
        "diabetes": "diabetes mellitus",
        "sugar": "diabetes mellitus",
        "high sugar": "diabetes mellitus",
        "type 2 diabetes": "diabetes mellitus, type 2",
        "type 1 diabetes": "diabetes mellitus, type 1",
        "high blood sugar": "hyperglycemia",
        "low blood sugar": "hypoglycemia",
        "kidney problem": "acute kidney injury",
        "kidney disease": "renal insufficiency, chronic",
        "kidney failure": "renal insufficiency, chronic",
        "ckd": "renal insufficiency, chronic",
        "renal failure": "renal insufficiency, chronic",
        "liver problem": "liver diseases",
        "liver disease": "liver diseases",
        "hepatitis": "hepatitis, chronic",
        "cirrhosis": "liver cirrhosis",
        "asthma": "asthma",
        "copd": "pulmonary disease, chronic obstructive",
        "lung disease": "lung diseases",
        "epilepsy": "epilepsy",
        "seizure": "seizures",
        "seizures": "seizures",
        "fits": "seizures",
        "migraine": "migraine disorders",
        "parkinson": "parkinson disease",
        "parkinsons": "parkinson disease",
        "alzheimer": "alzheimer disease",
        "dementia": "dementia",
        "tremor": "tremor",
        "depression": "depressive disorder",
        "anxiety": "anxiety disorders",
        "bipolar": "bipolar disorder",
        "schizophrenia": "schizophrenia",
        "insomnia": "sleep initiation and maintenance disorders",
        "adhd": "attention deficit disorder with hyperactivity",
        "stomach ulcer": "peptic ulcer",
        "ulcer": "peptic ulcer",
        "acid reflux": "gastroesophageal reflux",
        "gerd": "gastroesophageal reflux",
        "ibs": "irritable bowel syndrome",
        "crohns": "crohn disease",
        "colitis": "colitis",
        "thyroid": "thyroid diseases",
        "hypothyroid": "hypothyroidism",
        "hyperthyroid": "hyperthyroidism",
        "underactive thyroid": "hypothyroidism",
        "overactive thyroid": "hyperthyroidism",
        "cancer": "neoplasms",
        "blood cancer": "leukemia",
        "leukemia": "leukemia",
        "lymphoma": "lymphoma",
        "breast cancer": "breast neoplasms",
        "lung cancer": "lung neoplasms",
        "arthritis": "arthritis",
        "rheumatoid arthritis": "arthritis, rheumatoid",
        "ra": "arthritis, rheumatoid",
        "osteoporosis": "osteoporosis",
        "gout": "gout",
        "anemia": "anemia",
        "low hemoglobin": "anemia",
        "high cholesterol": "hypercholesterolemia",
        "cholesterol": "hypercholesterolemia",
        "psoriasis": "psoriasis",
        "eczema": "dermatitis, atopic",
        "allergy": "hypersensitivity",
        "allergies": "hypersensitivity",
        "hiv": "hiv infections",
        "tuberculosis": "tuberculosis",
        "tb": "tuberculosis",
        "obesity": "obesity",
        "overweight": "obesity",
        "lupus": "lupus erythematosus, systemic",
        "inflammation": "inflammation",
        "glaucoma": "glaucoma",
        "cataract": "cataract",
        "pregnancy": "pregnancy",
        "pain": "pain",
        "chronic pain": "chronic pain",
    }

    lower = condition.lower().strip()
    if lower in CONDITION_MAP:
        return CONDITION_MAP[lower]

    for key, val in CONDITION_MAP.items():
        if key in lower or lower in key:
            return val

    # Preserve existing curated mappings as fallback.
    return CONDITION_NAME_MAP.get(lower, lower)


def normalize_drug_lower(name):
    """Map common/brand drug name to lowercase generic name (for DFI/DCI datasets)"""
    if not name:
        return name
    lower = name.lower().strip()
    mapped = DRUG_NAME_MAP.get(lower)
    if mapped:
        return mapped.lower()
    return lower