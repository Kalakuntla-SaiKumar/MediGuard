from src.dfi.dfi_module import check_drug_food_interaction


def test_dfi_known_and_unknown_labels():
	allowed = {"None", "Low", "Moderate", "High"}
	assert check_drug_food_interaction("warfarin") in allowed
	assert check_drug_food_interaction("metformin") in allowed
	assert check_drug_food_interaction("aspirin") in allowed
	assert check_drug_food_interaction("randomdrug") in allowed