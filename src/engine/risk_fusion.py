# risk_fusion.py

SEVERITY_SCORES = {
    "None": 0,
    "Low": 1,
    "Moderate": 2,
    "High": 3
}

def fuse_risk(ddi_risk, dfi_risk_A, dfi_risk_B, dci_risk_A, dci_risk_B):
    """
    Combines DDI, DFI, and DCI risk signals
    using severity scoring and maximum risk prioritization.
    """

    risks = [
        ddi_risk,
        dfi_risk_A,
        dfi_risk_B,
        dci_risk_A,
        dci_risk_B
    ]

    # Convert to numeric scores
    scores = [SEVERITY_SCORES.get(risk, 0) for risk in risks]

    # Final risk = maximum severity
    max_score = max(scores)

    # Reverse mapping
    for level, score in SEVERITY_SCORES.items():
        if score == max_score:
            final_risk = level

    return final_risk