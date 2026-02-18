import pandas as pd

# Load cleaned DCI dataset
df_dci = pd.read_csv("dataset/cleaned_drug_condition_interactions.csv")

def check_drug_condition_interaction(drug, condition):
    drug = drug.lower()
    condition = condition.lower()

    matches = df_dci[
        (df_dci["Drug"] == drug) &
        (df_dci["Condition"] == condition)
    ]

    if matches.empty:
        return "None"

    if "High" in matches["Risk_Level"].values:
        return "High"
    elif "Moderate" in matches["Risk_Level"].values:
        return "Moderate"
    else:
        return "Low"