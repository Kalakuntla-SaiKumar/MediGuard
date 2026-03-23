"""
DDI Validation Module - Comprehensive testing for Drug-Drug Interactions
Verifies prediction accuracy, model loading, and data quality
"""

import pandas as pd
import os
from src.engine.mediguard_engine import predict_ddi, compute_ddi_features, format_ddi_features
from src.engine.drug_mapper import normalize_drug
import json


class DDIValidator:
    def __init__(self, random_state=42):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.ddi_path = os.path.join(self.base_dir, "data", "processed", "db_drug_interactions.csv")
        self.df_ddi = pd.read_csv(self.ddi_path)
        self.random_state = random_state
        
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "unknown_drugs": 0,
            "known_interaction_tests": 0,
            "known_interaction_passed": 0,
            "unknown_pair_tests": 0,
            "unknown_pair_none_predictions": 0,
            "test_details": []
        }

    def test_known_interactions(self, sample_size=20):
        """Test prediction on known interacting drug pairs"""
        print("\n" + "="*60)
        print("TEST 1: Known Drug Interactions")
        print("="*60)
        
        sample_pairs = self.df_ddi.sample(min(sample_size, len(self.df_ddi)), random_state=self.random_state)
        
        for idx, row in sample_pairs.iterrows():
            drug1 = row["Drug 1"]
            drug2 = row["Drug 2"]
            description = row["Interaction Description"]
            
            try:
                prediction = predict_ddi(drug1, drug2)
                self.results["total_tests"] += 1
                self.results["known_interaction_tests"] += 1
                
                # Known interaction should NOT be "None"
                if prediction != "None":
                    self.results["passed"] += 1
                    self.results["known_interaction_passed"] += 1
                    status = "✓ PASS"
                else:
                    self.results["failed"] += 1
                    status = "✗ FAIL"
                
                print(f"\n{status} | {drug1.title()} <-> {drug2.title()}")
                print(f"     Prediction: {prediction}")
                print(f"     Description: {description[:70]}...")
                
                self.results["test_details"].append({
                    "type": "known_interaction",
                    "drug1": drug1,
                    "drug2": drug2,
                    "prediction": prediction,
                    "status": "pass" if prediction != "None" else "fail"
                })
                
            except Exception as e:
                self.results["unknown_drugs"] += 1
                print(f"\n⚠ SKIP | {drug1.title()} <-> {drug2.title()}: {str(e)}")

    def test_unknown_pairs(self, num_tests=10):
        """Test on non-interacting or unknown drug pairs"""
        print("\n" + "="*60)
        print("TEST 2: Unknown/Non-Interacting Pairs")
        print("="*60)
        
        test_pairs = [
            ("aspirin", "glucose"),
            ("water", "salt"),
            ("vitamin-c", "orange-juice"),
            ("paracetamol", "milk"),
            ("ibuprofen", "bread"),
            ("metformin", "rice"),
            ("lisinopril", "sugar"),
            ("amoxicillin", "honey"),
            ("omeprazole", "tea"),
            ("simvastatin", "yogurt"),
        ]
        
        for drug1, drug2 in test_pairs[:num_tests]:
            try:
                prediction = predict_ddi(drug1, drug2)
                self.results["total_tests"] += 1
                self.results["unknown_pair_tests"] += 1
                if prediction == "None":
                    self.results["unknown_pair_none_predictions"] += 1
                
                print(f"\n{drug1.title()} <-> {drug2.title()}: {prediction}")
                
                self.results["test_details"].append({
                    "type": "unknown_pair",
                    "drug1": drug1,
                    "drug2": drug2,
                    "prediction": prediction,
                    "status": "tested"
                })
                
            except Exception as e:
                self.results["unknown_drugs"] += 1
                print(f"\n⚠ {drug1.title()} <-> {drug2.title()}: {str(e)}")

    def test_model_confidence(self, sample_size=5):
        """Test model confidence scores"""
        print("\n" + "="*60)
        print("TEST 3: Model Confidence Analysis")
        print("="*60)
        
        sample_pairs = self.df_ddi.sample(min(sample_size, len(self.df_ddi)), random_state=self.random_state + 1)
        
        for idx, row in sample_pairs.iterrows():
            drug1 = normalize_drug(row["Drug 1"])
            drug2 = normalize_drug(row["Drug 2"])
            
            try:
                features = compute_ddi_features(drug1, drug2)
                
                if features is not None:
                    import joblib
                    rf_model = joblib.load(os.path.join(self.base_dir, "models", "ddi_random_forest.pkl"))
                    feature_frame = format_ddi_features(features, rf_model)
                    probability = rf_model.predict_proba(feature_frame)[0][1]
                    
                    print(f"\n{drug1.title()} <-> {drug2.title()}")
                    print(f"  Interaction Probability: {probability:.2%}")
                    
            except Exception as e:
                pass

    def generate_report(self):
        """Generate accuracy report"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        if self.results["total_tests"] > 0:
            accuracy = (self.results["passed"] / self.results["total_tests"]) * 100
            print(f"\nTotal Tests: {self.results['total_tests']}")
            print(f"Passed: {self.results['passed']}")
            print(f"Failed: {self.results['failed']}")
            print(f"Unknown Drugs: {self.results['unknown_drugs']}")
            print(f"Overall Accuracy (all tests): {accuracy:.2f}%")

        known_total = self.results.get("known_interaction_tests", 0)
        if known_total > 0:
            known_accuracy = (self.results["known_interaction_passed"] / known_total) * 100
            print(f"Known Interaction Accuracy: {known_accuracy:.2f}%")

        unknown_total = self.results.get("unknown_pair_tests", 0)
        if unknown_total > 0:
            unknown_none_rate = (self.results["unknown_pair_none_predictions"] / unknown_total) * 100
            print(f"Unknown-Pair None Rate: {unknown_none_rate:.2f}%")
        
        print("\nDataset Info:")
        print(f"Total Interaction Pairs: {len(self.df_ddi)}")
        print(f"Unique Drugs: {len(set(pd.concat([self.df_ddi['Drug 1'], self.df_ddi['Drug 2']])))}")
        
        return self.results


if __name__ == "__main__":
    validator = DDIValidator()
    
    # Run all tests
    validator.test_known_interactions(sample_size=15)
    validator.test_unknown_pairs(num_tests=8)
    validator.test_model_confidence(sample_size=5)
    
    # Generate report
    report = validator.generate_report()
    
    # Save report
    with open("ddi_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Report saved to ddi_validation_report.json")
