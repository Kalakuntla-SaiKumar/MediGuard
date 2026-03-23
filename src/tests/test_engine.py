from src.engine.mediguard_engine import mediguard_assess, predict_ddi


def test_mediguard_assess_shape():
    result = mediguard_assess("warfarin", "aspirin", "ulcer")
    required_keys = {
        "drug1",
        "drug2",
        "condition",
        "drug1_mapped",
        "drug2_mapped",
        "ddi_risk",
        "dfi_risk_drug1",
        "dfi_risk_drug2",
        "dci_risk_drug1",
        "dci_risk_drug2",
        "overall_risk",
    }
    assert required_keys.issubset(result.keys())


def test_predict_ddi_known_pair_not_none():
    risk = predict_ddi("warfarin", "aspirin")
    assert risk in {"Low", "Moderate", "High", "None"}
    assert risk != "None"