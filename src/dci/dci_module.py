import os
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_drug_condition_interactions.csv")

try:
    df_dci = pd.read_csv(DATA_PATH)
    logger.info(f"DCI dataset loaded successfully: {len(df_dci)} records")
except FileNotFoundError:
    logger.error(f"DCI dataset not found at {DATA_PATH}")
    df_dci = pd.DataFrame(columns=["Drug", "Condition", "Risk_Level"])


def check_drug_condition_interaction(drug, condition):
    """
    Check drug-condition interaction.
    
    Args:
        drug (str): Drug name
        condition (str): Medical condition
        
    Returns:
        str: Risk level ("None", "Low", "Moderate", "High")
    """
    if not isinstance(drug, str) or not drug.strip():
        logger.warning(f"Invalid drug input: {drug}")
        return "None"
    
    if not isinstance(condition, str) or not condition.strip():
        logger.warning(f"Invalid condition input: {condition}")
        return "None"
    
    from src.engine.drug_mapper import normalize_condition
    drug = drug.lower().strip()
    condition = normalize_condition(condition.lower().strip())

    # Try exact match first
    matches = df_dci[
        (df_dci["Drug"] == drug) &
        (df_dci["Condition"] == condition)
    ]

    # If no match, try partial condition match
    if matches.empty:
        matches = df_dci[
            (df_dci["Drug"] == drug) &
            (df_dci["Condition"].str.contains(condition, case=False, na=False))
        ]

    # If still no match, try the base term before comma qualifiers.
    if matches.empty and "," in condition:
        base_condition = condition.split(",", 1)[0].strip()
        matches = df_dci[
            (df_dci["Drug"] == drug) &
            (df_dci["Condition"].str.contains(base_condition, case=False, na=False))
        ]

    if matches.empty:
        logger.debug(f"No interaction data found for {drug} + {condition}")
        return "None"

    if "High" in matches["Risk_Level"].values:
        return "High"
    elif "Moderate" in matches["Risk_Level"].values:
        return "Moderate"
    else:
        return "Low"