import json
import pandas as pd

# Load JSON file
with open("dataset/Drug to Food interactions Dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

for item in data:
    drug = item["name"].lower()
    interactions = item.get("food_interactions", [])
    
    for interaction in interactions:
        rows.append({
            "Drug": drug,
            "Interaction_Text": interaction.lower()
        })

df_dfi = pd.DataFrame(rows)

# ----------------------------
# Extract Risk Level
# ----------------------------

def classify_severity(text):
    if "avoid" in text:
        return "High"
    elif "limit" in text or "caution" in text:
        return "Moderate"
    else:
        return "Low"

df_dfi["Risk_Level"] = df_dfi["Interaction_Text"].apply(classify_severity)

# Remove duplicates (important)
df_dfi = df_dfi.drop_duplicates()

# Save as CSV
df_dfi.to_csv("dataset/cleaned_drug_food_interactions.csv", index=False)

print("DFI cleaned and saved successfully!")
print(df_dfi.head())
print("Total rows:", len(df_dfi))