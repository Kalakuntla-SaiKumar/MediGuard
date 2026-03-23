from src.dci.dci_module import check_drug_condition_interaction


def test_dci_known_pairs_return_valid_label():
	allowed = {"None", "Low", "Moderate", "High"}
	assert check_drug_condition_interaction("metformin", "diabetes") in allowed
	assert check_drug_condition_interaction("carbamazepine", "epilepsy") in allowed
	assert check_drug_condition_interaction("ibuprofen", "ulcer") in allowed
