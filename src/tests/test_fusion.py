from src.engine.risk_fusion import fuse_risk


def test_fusion_high_path():
	out = fuse_risk("Moderate", "Low", "None", "High", "None")
	assert out["Final_Risk"] == "High"


def test_fusion_low_path():
	out = fuse_risk("Low", "Low", "None", "None", "None")
	assert out["Final_Risk"] == "Low"


def test_fusion_none_path():
	out = fuse_risk("None", "None", "None", "None", "None")
	assert out["Final_Risk"] == "None"