from src.engine.mediguard_engine import mediguard_assess

result = mediguard_assess(
    "warfarin",
    "aspirin",
    "ulcer"
)

print(result)