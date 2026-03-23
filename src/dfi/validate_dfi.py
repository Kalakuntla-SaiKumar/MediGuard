"""
DFI Validation Module - Comprehensive testing for Drug-Food Interactions
Verifies prediction accuracy and data quality
"""

import pandas as pd
import os
from src.dfi.dfi_module import check_drug_food_interaction
import json


class DFIValidator:
    def __init__(self, random_state=42):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.dfi_path = os.path.join(self.base_dir, "data", "processed", "cleaned_drug_food_interactions.csv")
        self.df_dfi = pd.read_csv(self.dfi_path)
        self.random_state = random_state
        
        # Lowercase for comparison
        self.df_dfi["Drug"] = self.df_dfi["Drug"].str.lower()
        
        self.results = {
            "total_drugs_tested": 0,
            "found_interactions": 0,
            "not_found": 0,
            "risk_distribution": {},
            "test_details": []
        }

    def test_known_drugs(self, sample_size=20):
        """Test drugs with known interactions"""
        print("\n" + "="*60)
        print("TEST 1: Known Drugs with Food Interactions")
        print("="*60)
        
        unique_drugs = self.df_dfi["Drug"].drop_duplicates()
        n = min(sample_size, len(unique_drugs))
        sample_drugs = unique_drugs.sample(n=n, random_state=self.random_state).tolist()
        
        for drug in sample_drugs:
            risk_level = check_drug_food_interaction(drug)
            self.results["total_drugs_tested"] += 1
            
            if risk_level != "None":
                self.results["found_interactions"] += 1
            else:
                self.results["not_found"] += 1
            
            # Count risk distribution
            if risk_level not in self.results["risk_distribution"]:
                self.results["risk_distribution"][risk_level] = 0
            self.results["risk_distribution"][risk_level] += 1
            
            # Get actual interactions from data
            drug_interactions = self.df_dfi[self.df_dfi["Drug"] == drug]
            interaction_count = len(drug_interactions)
            risk_types = drug_interactions["Risk_Level"].unique()
            
            print(f"\n✓ {drug.title()}")
            print(f"  Prediction: {risk_level}")
            print(f"  Interactions in DB: {interaction_count}")
            print(f"  Risk Types: {', '.join(risk_types)}")
            
            self.results["test_details"].append({
                "drug": drug,
                "prediction": risk_level,
                "db_count": interaction_count,
                "db_risks": list(risk_types)
            })

    def test_unknown_drugs(self, num_tests=15):
        """Test drugs unlikely to have interactions"""
        print("\n" + "="*60)
        print("TEST 2: Unknown/Unlikely Drugs")
        print("="*60)
        
        test_drugs = [
            "water",
            "salt",
            "sugar",
            "rice",
            "bread",
            "unknown_drug_xyz",
            "fake_medicine",
            "vitamin_d",
            "calcium",
            "iron",
            "zinc",
            "magnesium",
            "potassium",
            "sodium",
            "glucose"
        ]
        
        for drug in test_drugs[:num_tests]:
            risk_level = check_drug_food_interaction(drug)
            self.results["total_drugs_tested"] += 1
            
            print(f"\n{drug.title()}: {risk_level}")
            
            self.results["test_details"].append({
                "drug": drug,
                "prediction": risk_level,
                "type": "unknown"
            })

    def analyze_data_quality(self):
        """Analyze DFI dataset quality"""
        print("\n" + "="*60)
        print("TEST 3: Data Quality Analysis")
        print("="*60)
        
        print(f"\nTotal Records: {len(self.df_dfi)}")
        print(f"Unique Drugs: {self.df_dfi['Drug'].nunique()}")
        print(f"\nRisk Level Distribution:")
        
        risk_dist = self.df_dfi["Risk_Level"].value_counts()
        for risk, count in risk_dist.items():
            percentage = (count / len(self.df_dfi)) * 100
            print(f"  {risk}: {count} ({percentage:.1f}%)")
        
        print(f"\nTop 10 Drugs by Interaction Count:")
        top_drugs = self.df_dfi["Drug"].value_counts().head(10)
        for drug, count in top_drugs.items():
            print(f"  {drug.title()}: {count}")

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("DFI VALIDATION REPORT")
        print("="*60)
        
        accuracy_rate = (self.results["found_interactions"] / self.results["total_drugs_tested"] * 100) if self.results["total_drugs_tested"] > 0 else 0
        
        print(f"\nTotal Drugs Tested: {self.results['total_drugs_tested']}")
        print(f"Found Interactions: {self.results['found_interactions']}")
        print(f"Not Found: {self.results['not_found']}")
        print(f"Detection Rate: {accuracy_rate:.2f}%")
        print(f"\nPredicted Risk Distribution:")
        for risk, count in self.results["risk_distribution"].items():
            print(f"  {risk}: {count}")
        
        return self.results


if __name__ == "__main__":
    validator = DFIValidator()
    
    # Run all tests
    validator.test_known_drugs(sample_size=20)
    validator.test_unknown_drugs(num_tests=12)
    validator.analyze_data_quality()
    
    # Generate report
    report = validator.generate_report()
    
    # Save report
    with open("dfi_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Report saved to dfi_validation_report.json")
