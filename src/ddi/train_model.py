import pandas as pd
import random
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ----------------------------
# Load dataset
# ----------------------------
df = pd.read_csv("dataset/db_drug_interactions.csv")

# Add positive label
df["label"] = 1

# Unique drugs
unique_drugs = list(set(df["Drug 1"]).union(set(df["Drug 2"])))

# Existing interacting pairs
existing_pairs = set(
    tuple(sorted([row["Drug 1"], row["Drug 2"]]))
    for _, row in df.iterrows()
)

# ----------------------------
# Generate negative samples
# ----------------------------
negative_samples = []
target_negatives = 50000
df_positive = df[["Drug 1", "Drug 2", "label"]].sample(n=50000, random_state=42)

while len(negative_samples) < target_negatives:
    drug_a, drug_b = random.sample(unique_drugs, 2)
    pair = tuple(sorted([drug_a, drug_b]))

    if pair not in existing_pairs:
        negative_samples.append([drug_a, drug_b, 0])

df_negative = pd.DataFrame(
    negative_samples,
    columns=["Drug 1", "Drug 2", "label"]
)

final_df = pd.concat([df_positive, df_negative], ignore_index=True)

# ----------------------------
# FEATURE ENGINEERING
# ----------------------------

# Drug frequency feature
all_drugs = pd.concat([final_df["Drug 1"], final_df["Drug 2"]])
drug_freq = all_drugs.value_counts()

final_df["Drug1_freq"] = final_df["Drug 1"].map(drug_freq)
final_df["Drug2_freq"] = final_df["Drug 2"].map(drug_freq)

# Frequency difference
final_df["freq_diff"] = abs(final_df["Drug1_freq"] - final_df["Drug2_freq"])

# Interaction degree feature
degree_map = (
    df.groupby("Drug 1")["Drug 2"].nunique()
    .add(df.groupby("Drug 2")["Drug 1"].nunique(), fill_value=0)
)

final_df["Drug1_degree"] = final_df["Drug 1"].map(degree_map).fillna(0)
final_df["Drug2_degree"] = final_df["Drug 2"].map(degree_map).fillna(0)

final_df["degree_diff"] = abs(
    final_df["Drug1_degree"] - final_df["Drug2_degree"]
)

# Encode drugs
le = LabelEncoder()
le.fit(all_drugs)

final_df["Drug1_encoded"] = le.transform(final_df["Drug 1"])
final_df["Drug2_encoded"] = le.transform(final_df["Drug 2"])

# ----------------------------
# Prepare data
# ----------------------------
X = final_df[
    [
        "Drug1_encoded",
        "Drug2_encoded",
        "Drug1_freq",
        "Drug2_freq",
        "freq_diff",
        "Drug1_degree",
        "Drug2_degree",
        "degree_diff"
    ]
]
y = final_df["label"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ----------------------------
# Logistic Regression
# ----------------------------
lr_model = LogisticRegression(max_iter=1000, class_weight="balanced")
lr_model.fit(X_train, y_train)

y_pred_lr = lr_model.predict(X_test)
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_lr))

# ----------------------------
# Random Forest (Improved)
# ----------------------------
rf_model = RandomForestClassifier(
    n_estimators=500,
    max_depth=25,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))

from sklearn.metrics import classification_report, confusion_matrix

print("\nRandom Forest Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_rf))

print("\nRandom Forest Classification Report:")
print(classification_report(y_test, y_pred_rf))

import joblib
import os

# Create models directory if not exists
os.makedirs("models", exist_ok=True)

# Save Random Forest model
joblib.dump(rf_model, "models/ddi_random_forest.pkl")
print("Model saved successfully!")

joblib.dump(le, "models/drug_label_encoder.pkl")
print("LabelEncoder saved successfully!")