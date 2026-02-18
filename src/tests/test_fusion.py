from risk_fusion import fuse_risk

print(fuse_risk("Moderate", "Low", "None", "High", "None"))
print(fuse_risk("Low", "Low", "None", "None", "None"))
print(fuse_risk("None", "None", "None", "None", "None"))