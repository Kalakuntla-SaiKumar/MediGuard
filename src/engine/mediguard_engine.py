import joblib
import pandas as pd
from src.dfi.dfi_module import check_drug_food_interaction
from src.dci.dci_module import check_drug_condition_interaction
from src.engine.risk_fusion import fuse_risk

# Load model and encoder
rf_model = joblib.load("models/ddi_random_forest.pkl")
label_encoder = joblib.load("models/drug_label_encoder.pkl")

# Load original DDI dataset to rebuild frequency/degree maps
df_ddi = pd.read_csv("dataset/db_drug_interactions.csv")

# Build frequency map
all_drugs = pd.concat([df_ddi["Drug 1"], df_ddi["Drug 2"]])
drug_freq = all_drugs.value_counts()

# Build degree map
degree_map = (
    df_ddi.groupby("Drug 1")["Drug 2"].nunique()
    .add(df_ddi.groupby("Drug 2")["Drug 1"].nunique(), fill_value=0)
)

def compute_ddi_features(drug1, drug2):
    drug1 = drug1.lower()
    drug2 = drug2.lower()

    # Encode drugs
    if drug1 not in label_encoder.classes_ or drug2 not in label_encoder.classes_:
        return None

    drug1_encoded = label_encoder.transform([drug1])[0]
    drug2_encoded = label_encoder.transform([drug2])[0]

    # Frequency features
    drug1_freq = drug_freq.get(drug1, 0)
    drug2_freq = drug_freq.get(drug2, 0)
    freq_diff = abs(drug1_freq - drug2_freq)

    # Degree features
    drug1_degree = degree_map.get(drug1, 0)
    drug2_degree = degree_map.get(drug2, 0)
    degree_diff = abs(drug1_degree - drug2_degree)

    return [
        drug1_encoded,
        drug2_encoded,
        drug1_freq,
        drug2_freq,
        freq_diff,
        drug1_degree,
        drug2_degree,
        degree_diff
    ]

def predict_ddi(drug1, drug2):
    features = compute_ddi_features(drug1, drug2)

    if features is None:
        return "None"

    prediction = rf_model.predict([features])[0]
    probability = rf_model.predict_proba([features])[0][1]

    if prediction == 1:
        if probability > 0.85:
            return "High"
        elif probability > 0.65:
            return "Moderate"
        else:
            return "Low"
    else:
        return "None"

def mediguard_assess(drug1, drug2, condition):

    # DDI risk
    ddi_risk = predict_ddi(drug1, drug2)

    # DFI risk
    dfi_risk_A = check_drug_food_interaction(drug1)
    dfi_risk_B = check_drug_food_interaction(drug2)

    # DCI risk
    dci_risk_A = check_drug_condition_interaction(drug1, condition)
    dci_risk_B = check_drug_condition_interaction(drug2, condition)

    final_risk = fuse_risk(
        ddi_risk,
        dfi_risk_A,
        dfi_risk_B,
        dci_risk_A,
        dci_risk_B
    )

    return {
        "DDI": ddi_risk,
        "DFI_A": dfi_risk_A,
        "DFI_B": dfi_risk_B,
        "DCI_A": dci_risk_A,
        "DCI_B": dci_risk_B,
        "Final_Risk": final_risk
    }