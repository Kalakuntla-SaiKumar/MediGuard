"""
MediGuard Engine - Main assessment module
Combines DDI, DFI, and DCI predictions using risk fusion
"""

import joblib
import pandas as pd
import os
import logging
from src.dfi.dfi_module import check_drug_food_interaction
from src.dci.dci_module import check_drug_condition_interaction
from src.engine.risk_fusion import fuse_risk
from src.engine.drug_mapper import normalize_drug, normalize_drug_lower, normalize_condition

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# ============================================
# LOAD MODELS AND DATA
# ============================================

try:
    model_path   = os.path.join(BASE_DIR, "models", "ddi_random_forest.pkl")
    encoder_path = os.path.join(BASE_DIR, "models", "drug_label_encoder.pkl")
    rf_model      = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
    logger.info("✓ DDI Model and Encoder loaded successfully")
except Exception as e:
    logger.warning(f"⚠ DDI model not found. Falling back to rule/data-only checks: {str(e)}")
    rf_model      = None
    label_encoder = None

try:
    ddi_path = os.path.join(BASE_DIR, "data", "processed", "db_drug_interactions.csv")
    df_ddi_raw = pd.read_csv(ddi_path)

    # Build lowercase→encoder mapping from label_encoder classes
    encoder_lookup = {}
    if label_encoder is not None:
        for cls in label_encoder.classes_:
            encoder_lookup[cls.lower().strip()] = cls

    def map_to_encoder(name):
        return encoder_lookup.get(name.lower().strip(), name.strip())

    df_ddi = df_ddi_raw.copy()
    df_ddi["Drug 1"] = df_ddi["Drug 1"].apply(map_to_encoder)
    df_ddi["Drug 2"] = df_ddi["Drug 2"].apply(map_to_encoder)
    logger.info(f"✓ DDI dataset loaded: {len(df_ddi)} records")
except Exception as e:
    logger.error(f"✗ Failed to load DDI dataset: {str(e)}")
    df_ddi = pd.DataFrame(columns=["Drug 1", "Drug 2"])

try:
    all_drugs  = pd.concat([df_ddi["Drug 1"], df_ddi["Drug 2"]])
    drug_freq  = all_drugs.value_counts()
    degree_map = (
        df_ddi.groupby("Drug 1")["Drug 2"].nunique()
        .add(df_ddi.groupby("Drug 2")["Drug 1"].nunique(), fill_value=0)
    )
    logger.info(f"✓ Feature maps built: {len(drug_freq)} unique drugs")
except Exception as e:
    logger.warning(f"⚠ Could not build feature maps: {str(e)}")
    drug_freq  = {}
    degree_map = {}


# ============================================
# DDI PREDICTION
# ============================================

DDI_FEATURE_COLUMNS = [
    "drug1_encoded",
    "drug2_encoded",
    "drug1_freq",
    "drug2_freq",
    "freq_diff",
    "drug1_degree",
    "drug2_degree",
    "degree_diff",
]

def compute_ddi_features(drug1, drug2):
    if label_encoder is None:
        return None

    drug1 = drug1.strip()
    drug2 = drug2.strip()

    if drug1 not in label_encoder.classes_ or drug2 not in label_encoder.classes_:
        logger.debug(f"Drug(s) not in encoder: {drug1}, {drug2}")
        return None

    try:
        drug1_encoded = label_encoder.transform([drug1])[0]
        drug2_encoded = label_encoder.transform([drug2])[0]
        drug1_freq    = drug_freq.get(drug1, 0)
        drug2_freq    = drug_freq.get(drug2, 0)
        freq_diff     = abs(drug1_freq - drug2_freq)
        drug1_degree  = degree_map.get(drug1, 0)
        drug2_degree  = degree_map.get(drug2, 0)
        degree_diff   = abs(drug1_degree - drug2_degree)

        return [drug1_encoded, drug2_encoded,
                drug1_freq, drug2_freq, freq_diff,
                drug1_degree, drug2_degree, degree_diff]
    except Exception as e:
        logger.error(f"Error computing features: {str(e)}")
        return None


def format_ddi_features(features, model=None):
    """Build a 1-row DataFrame with consistent feature names for sklearn inference."""
    active_model = model or rf_model
    columns = getattr(active_model, "feature_names_in_", DDI_FEATURE_COLUMNS)
    return pd.DataFrame([features], columns=list(columns))


def predict_ddi(drug1, drug2):
    if rf_model is None:
        return "None"

    # Accept raw/common inputs and map them to encoder-compatible labels.
    drug1 = normalize_drug(drug1)
    drug2 = normalize_drug(drug2)

    features = compute_ddi_features(drug1, drug2)
    if features is None:
        return "None"

    try:
        feature_frame = format_ddi_features(features, rf_model)
        prediction  = rf_model.predict(feature_frame)[0]
        probability = rf_model.predict_proba(feature_frame)[0][1]

        if prediction == 1:
            if probability > 0.75:   return "High"
            elif probability > 0.65: return "Moderate"
            else:                    return "Low"
        else:
            return "None"
    except Exception as e:
        logger.error(f"DDI prediction error: {str(e)}")
        return "None"


# ============================================
# MAIN ASSESSMENT FUNCTION
# ============================================

def mediguard_assess(drug1, drug2, condition):
    """
    Perform comprehensive medication safety assessment.
    Automatically maps brand/common names to generic names.
    """
    logger.info(f"Starting assessment: {drug1} + {drug2} for condition: {condition}")

    if not all(isinstance(x, str) for x in [drug1, drug2, condition]):
        return {
            "error": "All inputs must be strings",
            "ddi_risk": "None", "dfi_risk_drug1": "None",
            "dfi_risk_drug2": "None", "dci_risk_drug1": "None",
            "dci_risk_drug2": "None", "overall_risk": "None"
        }

    # Normalize: DDI encoder needs Title Case, DFI/DCI need lowercase
    drug1_ddi  = normalize_drug(drug1)        # e.g. 'Warfarin', 'Acetylsalicylic acid'
    drug2_ddi  = normalize_drug(drug2)
    drug1_dfi  = normalize_drug_lower(drug1)  # e.g. 'warfarin', 'acetaminophen'
    drug2_dfi  = normalize_drug_lower(drug2)
    condition_norm = normalize_condition(condition)

    logger.info(f"DDI names: '{drug1_ddi}' + '{drug2_ddi}'")
    logger.info(f"DFI/DCI names: '{drug1_dfi}' + '{drug2_dfi}', condition: '{condition_norm}'")

    try:
        ddi_risk   = predict_ddi(drug1_ddi, drug2_ddi)
        dfi_risk_A = check_drug_food_interaction(drug1_dfi)
        dfi_risk_B = check_drug_food_interaction(drug2_dfi)
        dci_risk_A = check_drug_condition_interaction(drug1_dfi, condition_norm)
        dci_risk_B = check_drug_condition_interaction(drug2_dfi, condition_norm)

        fusion_result = fuse_risk(ddi_risk, dfi_risk_A, dfi_risk_B, dci_risk_A, dci_risk_B)
        final_risk    = fusion_result["Final_Risk"]

        logger.info(f"Assessment complete. Overall risk: {final_risk}")

        return {
            "drug1": drug1,
            "drug2": drug2,
            "condition": condition,
            "drug1_mapped": drug1_ddi,
            "drug2_mapped": drug2_ddi,
            "ddi_risk":      ddi_risk,
            "dfi_risk_drug1": dfi_risk_A,
            "dfi_risk_drug2": dfi_risk_B,
            "dci_risk_drug1": dci_risk_A,
            "dci_risk_drug2": dci_risk_B,
            "overall_risk":  final_risk
        }

    except Exception as e:
        logger.error(f"Assessment error: {str(e)}")
        return {
            "error": str(e),
            "ddi_risk": "None", "dfi_risk_drug1": "None",
            "dfi_risk_drug2": "None", "dci_risk_drug1": "None",
            "dci_risk_drug2": "None", "overall_risk": "None"
        }