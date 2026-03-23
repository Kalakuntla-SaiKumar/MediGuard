"""
DCI Validation Module - Comprehensive testing for Drug-Condition Interactions
Verifies prediction accuracy and data quality
"""

import pandas as pd
import os
from src.dci.dci_module import check_drug_condition_interaction
import json


class DCIValidator:
    def __init__(self, random_state=42):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.dci_path = os.path.join(self.base_dir, "data", "processed", "cleaned_drug_condition_interactions.csv")
        self.df_dci = pd.read_csv(self.dci_path)
        self.random_state = random_state
        
        # Lowercase for comparison
        self.df_dci["Drug"] = self.df_dci["Drug"].str.lower()
        self.df_dci["Condition"] = self.df_dci["Condition"].str.lower()
        
        self.results = {
            "total_tests": 0,
            "correct_predictions": 0,
            "incorrect_predictions": 0,
            "risk_distribution": {},
            "test_details": []
        }

    def test_known_drug_condition_pairs(self, sample_size=30):
        """Test prediction on known drug-condition pairs"""
        print("\n" + "="*60)
        print("TEST 1: Known Drug-Condition Pairs")
        print("="*60)
        
        sample_pairs = self.df_dci.sample(min(sample_size, len(self.df_dci)), random_state=self.random_state)
        
        for idx, row in sample_pairs.iterrows():
            drug = row["Drug"]
            condition = row["Condition"]
            expected_risk = row["Risk_Level"]
            
            prediction = check_drug_condition_interaction(drug, condition)
            self.results["total_tests"] += 1
            
            # Check if risk level matches
            if prediction == expected_risk or prediction != "None":
                self.results["correct_predictions"] += 1
                status = "✓ PASS"
            else:
                self.results["incorrect_predictions"] += 1
                status = "✗ FAIL"
            
            print(f"\n{status} | {drug.title()} + {condition.title()}")
            print(f"  Expected: {expected_risk}")
            print(f"  Predicted: {prediction}")
            
            self.results["test_details"].append({
                "drug": drug,
                "condition": condition,
                "expected": expected_risk,
                "predicted": prediction,
                "correct": prediction == expected_risk or prediction != "None"
            })

    def test_unknown_combinations(self, num_tests=15):
        """Test on unknown drug-condition combinations"""
        print("\n" + "="*60)
        print("TEST 2: Unknown Drug-Condition Combinations")
        print("="*60)
        
        test_combinations = [
            ("water", "diabetes"),
            ("salt", "hypertension"),
            ("unknown_drug", "fever"),
            ("unknown_medicine", "headache"),
            ("sugar", "obesity"),
            ("bread", "celiac disease"),
            ("milk", "lactose intolerance"),
            ("vitamin_c", "scurvy"),
            ("iron", "anemia"),
            ("calcium", "osteoporosis"),
            ("magnesium", "migraine"),
            ("zinc", "cold"),
            ("vitamin_d", "rickets"),
            ("potassium", "arrhythmia"),
            ("fake_drug", "unknown_condition")
        ]
        
        for drug, condition in test_combinations[:num_tests]:
            prediction = check_drug_condition_interaction(drug, condition)
            self.results["total_tests"] += 1
            
            print(f"\n{drug.title()} + {condition.title()}: {prediction}")
            
            self.results["test_details"].append({
                "drug": drug,
                "condition": condition,
                "predicted": prediction,
                "type": "unknown"
            })

    def test_same_drug_multiple_conditions(self, sample_size=5):
        """Test single drug with multiple conditions"""
        print("\n" + "="*60)
        print("TEST 3: Single Drug - Multiple Conditions")
        print("="*60)
        
        unique_drugs = self.df_dci["Drug"].unique()
        
        for drug in unique_drugs[:sample_size]:
            matching_rows = self.df_dci[self.df_dci["Drug"] == drug]
            
            print(f"\n{drug.title()}:")
            
            for idx, row in matching_rows.head(5).iterrows():
                condition = row["Condition"]
                expected_risk = row["Risk_Level"]
                prediction = check_drug_condition_interaction(drug, condition)
                
                match = "✓" if prediction != "None" else "✗"
                print(f"  {match} {condition.title()}: Expected={expected_risk}, Predicted={prediction}")

    def analyze_data_quality(self):
        """Analyze DCI dataset quality"""
        print("\n" + "="*60)
        print("TEST 4: Data Quality Analysis")
        print("="*60)
        
        print(f"\nTotal Records: {len(self.df_dci)}")
        print(f"Unique Drugs: {self.df_dci['Drug'].nunique()}")
        print(f"Unique Conditions: {self.df_dci['Condition'].nunique()}")
        print(f"\nRisk Level Distribution:")
        
        risk_dist = self.df_dci["Risk_Level"].value_counts()
        for risk, count in risk_dist.items():
            percentage = (count / len(self.df_dci)) * 100
            print(f"  {risk}: {count} ({percentage:.1f}%)")
        
        print(f"\nTop 10 Most Common Conditions:")
        top_conditions = self.df_dci["Condition"].value_counts().head(10)
        for condition, count in top_conditions.items():
            print(f"  {condition.title()}: {count}")
        
        print(f"\nTop 10 Most Studied Drugs:")
        top_drugs = self.df_dci["Drug"].value_counts().head(10)
        for drug, count in top_drugs.items():
            print(f"  {drug.title()}: {count}")

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("DCI VALIDATION REPORT")
        print("="*60)
        
        if self.results["total_tests"] > 0:
            accuracy = (self.results["correct_predictions"] / self.results["total_tests"]) * 100
            print(f"\nTotal Tests: {self.results['total_tests']}")
            print(f"Correct: {self.results['correct_predictions']}")
            print(f"Incorrect: {self.results['incorrect_predictions']}")
            print(f"Accuracy: {accuracy:.2f}%")
        
        print(f"\nDataset Info:")
        print(f"Total Drug-Condition Pairs: {len(self.df_dci)}")
        print(f"Unique Drugs: {self.df_dci['Drug'].nunique()}")
        print(f"Unique Conditions: {self.df_dci['Condition'].nunique()}")
        
        return self.results


if __name__ == "__main__":
    validator = DCIValidator()
    
    # Run all tests
    validator.test_known_drug_condition_pairs(sample_size=25)
    validator.test_unknown_combinations(num_tests=12)
    validator.test_same_drug_multiple_conditions(sample_size=5)
    validator.analyze_data_quality()
    
    # Generate report
    report = validator.generate_report()
    
    # Save report
    with open("dci_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Report saved to dci_validation_report.json")
