"""
Integrated Validation Runner - Comprehensive MediGuard Assessment
Runs all three validation modules and generates a master report
"""

import sys
import os
import json
import time
import io
import contextlib
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_validations():
    """Run all validation modules and collect results"""
    random_state = int(os.getenv("VALIDATION_SEED", "42"))
    min_ddi_accuracy = float(os.getenv("VALIDATION_MIN_DDI", "50"))
    min_dfi_detection = float(os.getenv("VALIDATION_MIN_DFI", "60"))
    min_dci_accuracy = float(os.getenv("VALIDATION_MIN_DCI", "60"))
    compact_mode = os.getenv("VALIDATION_COMPACT", "0").strip().lower() in {"1", "true", "yes", "on"}

    def run_step(func, *args, **kwargs):
        if compact_mode:
            with contextlib.redirect_stdout(io.StringIO()):
                return func(*args, **kwargs)
        return func(*args, **kwargs)
    
    print("\n" + "="*70)
    print(" "*15 + "MEDIGUARD INTEGRATED VALIDATION SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    if compact_mode:
        print("Mode: COMPACT (module details suppressed; summary shown)\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "random_state": random_state,
        "thresholds": {
            "ddi_min_accuracy": min_ddi_accuracy,
            "dfi_min_detection": min_dfi_detection,
            "dci_min_accuracy": min_dci_accuracy,
        },
        "validations": {}
    }
    
    # ============================================
    # RUN DDI VALIDATION
    # ============================================
    print("\n" + "█"*70)
    print("STARTING DDI VALIDATION")
    print("█"*70)
    
    try:
        from src.ddi.validate_ddi import DDIValidator
        ddi_validator = DDIValidator(random_state=random_state)
        
        run_step(ddi_validator.test_known_interactions, sample_size=15)
        run_step(ddi_validator.test_unknown_pairs, num_tests=8)
        run_step(ddi_validator.test_model_confidence, sample_size=5)
        
        ddi_report = run_step(ddi_validator.generate_report)
        results["validations"]["DDI"] = ddi_report
        
        print("\n✓ DDI Validation Complete")
    except Exception as e:
        print(f"\n✗ DDI Validation Failed: {str(e)}")
        results["validations"]["DDI"] = {"error": str(e)}
    
    time.sleep(1)
    
    # ============================================
    # RUN DFI VALIDATION
    # ============================================
    print("\n" + "█"*70)
    print("STARTING DFI VALIDATION")
    print("█"*70)
    
    try:
        from src.dfi.validate_dfi import DFIValidator
        dfi_validator = DFIValidator(random_state=random_state)
        
        run_step(dfi_validator.test_known_drugs, sample_size=20)
        run_step(dfi_validator.test_unknown_drugs, num_tests=12)
        run_step(dfi_validator.analyze_data_quality)
        
        dfi_report = run_step(dfi_validator.generate_report)
        results["validations"]["DFI"] = dfi_report
        
        print("\n✓ DFI Validation Complete")
    except Exception as e:
        print(f"\n✗ DFI Validation Failed: {str(e)}")
        results["validations"]["DFI"] = {"error": str(e)}
    
    time.sleep(1)
    
    # ============================================
    # RUN DCI VALIDATION
    # ============================================
    print("\n" + "█"*70)
    print("STARTING DCI VALIDATION")
    print("█"*70)
    
    try:
        from src.dci.validate_dci import DCIValidator
        dci_validator = DCIValidator(random_state=random_state)
        
        run_step(dci_validator.test_known_drug_condition_pairs, sample_size=25)
        run_step(dci_validator.test_unknown_combinations, num_tests=12)
        run_step(dci_validator.test_same_drug_multiple_conditions, sample_size=5)
        run_step(dci_validator.analyze_data_quality)
        
        dci_report = run_step(dci_validator.generate_report)
        results["validations"]["DCI"] = dci_report
        
        print("\n✓ DCI Validation Complete")
    except Exception as e:
        print(f"\n✗ DCI Validation Failed: {str(e)}")
        results["validations"]["DCI"] = {"error": str(e)}
    
    # ============================================
    # GENERATE MASTER REPORT
    # ============================================
    print("\n" + "="*70)
    print(" "*20 + "MASTER VALIDATION REPORT")
    print("="*70)
    
    print("\n📊 SUMMARY:\n")
    
    for module, report in results["validations"].items():
        print(f"\n{module} Module:")
        print("-" * 40)
        
        if "error" in report:
            print(f"  ✗ Error: {report['error']}")
        else:
            if module == "DDI":
                total = report.get("total_tests", 0)
                passed = report.get("passed", 0)
                known_total = report.get("known_interaction_tests", 0)
                known_passed = report.get("known_interaction_passed", 0)
                if total > 0:
                    accuracy = (passed / total) * 100
                    print(f"  Total Tests: {total}")
                    print(f"  Passed: {passed}")
                    print(f"  Failed: {report.get('failed', 0)}")
                    print(f"  Accuracy (all tests): {accuracy:.2f}%")
                if known_total > 0:
                    known_accuracy = (known_passed / known_total) * 100
                    print(f"  Known Interaction Accuracy: {known_accuracy:.2f}%")
            
            elif module == "DFI":
                tested = report.get("total_drugs_tested", 0)
                found = report.get("found_interactions", 0)
                if tested > 0:
                    detection_rate = (found / tested) * 100
                    print(f"  Total Drugs Tested: {tested}")
                    print(f"  Found Interactions: {found}")
                    print(f"  Detection Rate: {detection_rate:.2f}%")
            
            elif module == "DCI":
                total = report.get("total_tests", 0)
                correct = report.get("correct_predictions", 0)
                if total > 0:
                    accuracy = (correct / total) * 100
                    print(f"  Total Tests: {total}")
                    print(f"  Correct: {correct}")
                    print(f"  Incorrect: {report.get('incorrect_predictions', 0)}")
                    print(f"  Accuracy: {accuracy:.2f}%")
    
    # Compute gate metrics
    ddi_report = results["validations"].get("DDI", {})
    dfi_report = results["validations"].get("DFI", {})
    dci_report = results["validations"].get("DCI", {})

    ddi_accuracy = 0.0
    if ddi_report.get("known_interaction_tests", 0):
        ddi_accuracy = (
            ddi_report.get("known_interaction_passed", 0)
            / ddi_report["known_interaction_tests"]
        ) * 100
    elif ddi_report.get("total_tests", 0):
        ddi_accuracy = (ddi_report.get("passed", 0) / ddi_report["total_tests"]) * 100

    dfi_detection = 0.0
    if dfi_report.get("total_drugs_tested", 0):
        dfi_detection = (dfi_report.get("found_interactions", 0) / dfi_report["total_drugs_tested"]) * 100

    dci_accuracy = 0.0
    if dci_report.get("total_tests", 0):
        dci_accuracy = (dci_report.get("correct_predictions", 0) / dci_report["total_tests"]) * 100

    results["gate"] = {
        "ddi_accuracy": round(ddi_accuracy, 2),
        "dfi_detection": round(dfi_detection, 2),
        "dci_accuracy": round(dci_accuracy, 2),
        "ddi_pass": ddi_accuracy >= min_ddi_accuracy,
        "dfi_pass": dfi_detection >= min_dfi_detection,
        "dci_pass": dci_accuracy >= min_dci_accuracy,
    }
    results["gate"]["deployment_ready"] = (
        results["gate"]["ddi_pass"] and
        results["gate"]["dfi_pass"] and
        results["gate"]["dci_pass"]
    )

    print("\nDeployment Gate:")
    print(f"  DDI Accuracy: {ddi_accuracy:.2f}% (min {min_ddi_accuracy:.2f}%) -> {'PASS' if results['gate']['ddi_pass'] else 'FAIL'}")
    print(f"  DFI Detection: {dfi_detection:.2f}% (min {min_dfi_detection:.2f}%) -> {'PASS' if results['gate']['dfi_pass'] else 'FAIL'}")
    print(f"  DCI Accuracy: {dci_accuracy:.2f}% (min {min_dci_accuracy:.2f}%) -> {'PASS' if results['gate']['dci_pass'] else 'FAIL'}")
    print(f"  Overall: {'PASS' if results['gate']['deployment_ready'] else 'FAIL'}")

    # Save master report
    report_path = "mediguard_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print(f"\n✓ Full validation report saved: {report_path}")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70 + "\n")
    
    return results


if __name__ == "__main__":
    results = run_all_validations()
    if not results.get("gate", {}).get("deployment_ready", False):
        raise SystemExit(1)
