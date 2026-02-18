import pandas as pd

# Load CTD file (no header)
df = pd.read_csv(
    "dataset/CTD_chemicals_diseases.tsv.gz",
    sep="\t",
    compression="gzip",
    comment="#",
    header=None
)

# Select required columns by index
df = df[[0, 3, 5]]

# Rename columns
df.columns = ["Drug", "Condition", "Evidence"]

# Remove rows without evidence
df = df[df["Evidence"].notna()]

# Lowercase for consistency
df["Drug"] = df["Drug"].str.lower()
df["Condition"] = df["Condition"].str.lower()

# Risk classification logic
def classify_risk(evidence):
    evidence = str(evidence).lower()
    if "therapeutic" in evidence:
        return "Low"
    elif "marker/mechanism" in evidence:
        return "Moderate"
    else:
        return "High"

df["Risk_Level"] = df["Evidence"].apply(classify_risk)

# Keep only needed columns
df = df[["Drug", "Condition", "Risk_Level"]].drop_duplicates()

# Save cleaned file
df.to_csv("dataset/cleaned_drug_condition_interactions.csv", index=False)

print("DCI cleaned and saved successfully!")
print("Total rows:", len(df))
print(df.head())