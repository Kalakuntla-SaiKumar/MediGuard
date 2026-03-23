import os
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_drug_food_interactions.csv")

try:
    df_dfi = pd.read_csv(DATA_PATH)
    df_dfi["Drug"] = df_dfi["Drug"].str.lower().str.strip()
    df_dfi["Interaction_Text"] = df_dfi["Interaction_Text"].str.strip()
    logger.info(f"DFI dataset loaded: {len(df_dfi)} records")
except FileNotFoundError:
    logger.error(f"DFI dataset not found at {DATA_PATH}")
    df_dfi = pd.DataFrame(columns=["Drug", "Interaction_Text", "Risk_Level"])


def check_drug_food_interaction(drug):
    """Returns risk level string"""
    if not isinstance(drug, str) or not drug.strip():
        return "None"
    drug = drug.lower().strip()
    matches = df_dfi[df_dfi["Drug"] == drug]
    if matches.empty:
        return "None"
    if "High" in matches["Risk_Level"].values:
        return "High"
    elif "Moderate" in matches["Risk_Level"].values:
        return "Moderate"
    else:
        return "Low"


def get_drug_food_details(drug):
    """Returns full interaction details: risk + all interaction texts"""
    if not isinstance(drug, str) or not drug.strip():
        return {"risk": "None", "interactions": []}
    drug = drug.lower().strip()
    matches = df_dfi[df_dfi["Drug"] == drug]
    if matches.empty:
        return {"risk": "None", "interactions": []}

    if "High" in matches["Risk_Level"].values:
        risk = "High"
    elif "Moderate" in matches["Risk_Level"].values:
        risk = "Moderate"
    else:
        risk = "Low"

    interactions = []
    for _, row in matches.iterrows():
        interactions.append({
            "text": row["Interaction_Text"],
            "risk": row["Risk_Level"]
        })

    return {"risk": risk, "interactions": interactions}