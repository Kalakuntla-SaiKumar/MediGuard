import pandas as pd

# Load cleaned DFI dataset once
df_dfi = pd.read_csv("dataset/cleaned_drug_food_interactions.csv")

def check_drug_food_interaction(drug):
    drug = drug.lower()
    matches = df_dfi[df_dfi["Drug"] == drug]
    
    if matches.empty:
        return "None"
    
    if "High" in matches["Risk_Level"].values:
        return "High"
    elif "Moderate" in matches["Risk_Level"].values:
        return "Moderate"
    else:
        return "Low"