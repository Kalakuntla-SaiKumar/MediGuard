"""
Run this script once to generate a comprehensive drug-food interaction lookup.
Output: data/processed/drug_food_lookup.json

Usage: python generate_dfi_lookup.py (from project root)
"""

import json
import os

# ─────────────────────────────────────────────────────────────
# COMPREHENSIVE DRUG-FOOD INTERACTION DATABASE
# Format: (drug, food, risk, mechanism)
# Sources: Clinical pharmacology guidelines, FDA, WHO drug interaction data
# ─────────────────────────────────────────────────────────────

INTERACTIONS = [

    # ══════════════════════════════════════════════════
    # WARFARIN / ANTICOAGULANTS
    # ══════════════════════════════════════════════════
    ("warfarin", "spinach", "High", "Spinach is very high in Vitamin K which directly reduces warfarin's anticoagulant effect"),
    ("warfarin", "kale", "High", "Kale is extremely high in Vitamin K — significantly reduces warfarin effectiveness"),
    ("warfarin", "chicken liver", "High", "Chicken liver is very high in Vitamin K, reducing warfarin's anticoagulant effect"),
    ("warfarin", "beef liver", "High", "Beef liver is very high in Vitamin K, reducing warfarin's anticoagulant effect"),
    ("warfarin", "liver", "High", "Liver is very high in Vitamin K, directly antagonizing warfarin"),
    ("warfarin", "broccoli", "High", "Broccoli is very high in Vitamin K — reduces warfarin effectiveness significantly"),
    ("warfarin", "cabbage", "High", "Cabbage contains high Vitamin K — reduces warfarin's anticoagulant effect"),
    ("warfarin", "brussels sprouts", "High", "Very high Vitamin K content reduces warfarin effectiveness"),
    ("warfarin", "lettuce", "Moderate", "Contains moderate Vitamin K — can affect warfarin levels"),
    ("warfarin", "green tea", "Moderate", "Contains Vitamin K and may affect warfarin metabolism"),
    ("warfarin", "alcohol", "High", "Alcohol alters warfarin metabolism — increases bleeding risk significantly"),
    ("warfarin", "beer", "High", "Alcohol in beer alters warfarin metabolism — increases bleeding risk"),
    ("warfarin", "wine", "High", "Alcohol in wine alters warfarin metabolism — increases bleeding risk"),
    ("warfarin", "grapefruit", "Moderate", "Grapefruit inhibits CYP3A4 which can increase warfarin levels"),
    ("warfarin", "grapefruit juice", "Moderate", "Grapefruit juice inhibits CYP3A4 which can increase warfarin levels"),
    ("warfarin", "cranberry juice", "High", "Cranberry juice can potentiate warfarin effect — increases bleeding risk"),
    ("warfarin", "cranberry", "High", "Cranberry can potentiate warfarin effect — significantly increases INR"),
    ("warfarin", "garlic", "Moderate", "Garlic has antiplatelet properties — increases bleeding risk with warfarin"),
    ("warfarin", "ginger", "Moderate", "Ginger has antiplatelet properties — can increase warfarin effect"),
    ("warfarin", "turmeric", "Moderate", "Turmeric has anticoagulant properties — can potentiate warfarin"),
    ("warfarin", "avocado", "Moderate", "Avocado contains Vitamin K and may reduce warfarin effectiveness"),
    ("warfarin", "mango", "Moderate", "Mango may increase warfarin effect through unknown mechanism"),
    ("warfarin", "papaya", "High", "Papaya contains papain which potentiates warfarin — increases bleeding risk"),
    ("warfarin", "flaxseed", "Moderate", "Flaxseeds have anticoagulant properties — can potentiate warfarin"),
    ("warfarin", "fish oil", "Moderate", "Fish oil has antiplatelet effects — increases bleeding risk with warfarin"),
    ("warfarin", "omega-3", "Moderate", "Omega-3 fatty acids have antiplatelet effects — potentiates warfarin"),
    ("warfarin", "vitamin e", "Moderate", "High dose Vitamin E can potentiate warfarin anticoagulant effect"),
    ("warfarin", "onion", "Moderate", "Onion has antiplatelet properties — may increase bleeding risk"),
    ("warfarin", "methi", "Moderate", "Fenugreek has anticoagulant properties — can potentiate warfarin"),
    ("warfarin", "fenugreek", "Moderate", "Fenugreek has anticoagulant properties — can potentiate warfarin"),
    ("warfarin", "coconut water", "Low", "Coconut water is generally safe but monitor INR if consumed regularly"),
    ("warfarin", "biryani", "Low", "Biryani itself has no direct warfarin interaction — spices are at normal food quantities"),
    ("warfarin", "rice", "None", "Rice has no significant interaction with warfarin"),
    ("warfarin", "chicken", "None", "Plain chicken has no significant interaction with warfarin"),

    # ══════════════════════════════════════════════════
    # STATINS (Atorvastatin, Simvastatin, Lovastatin)
    # ══════════════════════════════════════════════════
    ("atorvastatin", "grapefruit", "High", "Grapefruit inhibits CYP3A4 — significantly increases atorvastatin blood levels, risk of myopathy"),
    ("atorvastatin", "grapefruit juice", "High", "Grapefruit juice inhibits CYP3A4 — increases atorvastatin levels, muscle damage risk"),
    ("atorvastatin", "alcohol", "High", "Alcohol combined with atorvastatin increases risk of liver damage"),
    ("atorvastatin", "pomelo", "High", "Pomelo contains furanocoumarins like grapefruit — inhibits CYP3A4"),
    ("simvastatin", "grapefruit", "High", "Grapefruit inhibits CYP3A4 — greatly increases simvastatin levels, rhabdomyolysis risk"),
    ("simvastatin", "grapefruit juice", "High", "Grapefruit juice greatly increases simvastatin blood levels — muscle damage risk"),
    ("simvastatin", "alcohol", "High", "Alcohol with simvastatin increases liver damage risk"),
    ("simvastatin", "pomelo", "High", "Pomelo inhibits CYP3A4 like grapefruit — increases simvastatin toxicity"),
    ("simvastatin", "large meals", "Low", "High fat meals may slightly increase simvastatin absorption"),
    ("lovastatin", "grapefruit", "High", "Grapefruit inhibits CYP3A4 metabolism of lovastatin — toxicity risk"),
    ("lovastatin", "grapefruit juice", "High", "Grapefruit juice significantly increases lovastatin blood levels"),
    ("rosuvastatin", "alcohol", "Moderate", "Alcohol increases risk of liver toxicity with rosuvastatin"),
    ("rosuvastatin", "antacids", "Moderate", "Antacids containing aluminum/magnesium reduce rosuvastatin absorption by 50%"),

    # ══════════════════════════════════════════════════
    # ACE INHIBITORS (Lisinopril, Ramipril, Captopril)
    # ══════════════════════════════════════════════════
    ("lisinopril", "potassium rich foods", "High", "ACE inhibitors increase potassium levels — high potassium foods risk dangerous hyperkalemia"),
    ("lisinopril", "bananas", "Moderate", "Bananas are high in potassium — ACE inhibitors can cause hyperkalemia"),
    ("lisinopril", "avocado", "Moderate", "Avocado is high in potassium — risk of hyperkalemia with ACE inhibitors"),
    ("lisinopril", "salt substitutes", "High", "Salt substitutes contain potassium chloride — dangerous hyperkalemia risk"),
    ("lisinopril", "alcohol", "Moderate", "Alcohol enhances blood pressure lowering effect — risk of hypotension"),
    ("ramipril", "bananas", "Moderate", "Bananas are high in potassium — ACE inhibitors increase hyperkalemia risk"),
    ("ramipril", "potassium rich foods", "High", "High potassium foods increase hyperkalemia risk with ACE inhibitors"),
    ("ramipril", "alcohol", "Moderate", "Alcohol enhances hypotensive effect — dizziness and fainting risk"),
    ("captopril", "food", "Low", "Food reduces captopril absorption by 30-40% — best taken on empty stomach"),
    ("captopril", "potassium rich foods", "High", "High potassium foods increase hyperkalemia risk with captopril"),

    # ══════════════════════════════════════════════════
    # BETA BLOCKERS (Metoprolol, Atenolol, Propranolol)
    # ══════════════════════════════════════════════════
    ("metoprolol", "alcohol", "High", "Alcohol enhances metoprolol's blood pressure lowering effect — severe hypotension risk"),
    ("metoprolol", "natural licorice", "High", "Licorice causes sodium retention and hypertension, opposing metoprolol's effect"),
    ("metoprolol", "licorice", "High", "Licorice causes sodium retention opposing metoprolol's antihypertensive effect"),
    ("metoprolol", "high fat meal", "Low", "High fat meals increase metoprolol absorption — slightly higher blood levels"),
    ("metoprolol", "biryani", "None", "Biryani has no significant interaction with metoprolol"),
    ("propranolol", "alcohol", "High", "Alcohol enhances hypotensive effect of propranolol — dangerous blood pressure drop"),
    ("propranolol", "licorice", "High", "Licorice opposes propranolol's antihypertensive effect"),
    ("propranolol", "high fat meal", "Low", "High fat meals increase propranolol absorption by up to 50%"),
    ("atenolol", "alcohol", "Moderate", "Alcohol enhances blood pressure lowering effect of atenolol"),
    ("atenolol", "antacids", "Moderate", "Antacids containing aluminum reduce atenolol absorption"),

    # ══════════════════════════════════════════════════
    # METFORMIN / DIABETES MEDICATIONS
    # ══════════════════════════════════════════════════
    ("metformin", "alcohol", "High", "Alcohol increases risk of lactic acidosis — potentially fatal combination"),
    ("metformin", "beer", "High", "Alcohol in beer increases lactic acidosis risk with metformin"),
    ("metformin", "wine", "High", "Alcohol in wine significantly increases lactic acidosis risk"),
    ("metformin", "karela", "Moderate", "Karela (bitter gourd) lowers blood sugar — hypoglycemia risk with metformin"),
    ("metformin", "bitter gourd", "Moderate", "Bitter gourd lowers blood sugar — hypoglycemia risk when combined"),
    ("metformin", "fenugreek", "Moderate", "Fenugreek lowers blood glucose — additive hypoglycemic effect"),
    ("metformin", "methi", "Moderate", "Fenugreek lowers blood glucose — additive hypoglycemic effect with metformin"),
    ("metformin", "large meal", "Low", "Take metformin with food to reduce gastrointestinal side effects"),
    ("metformin", "sugar", "Moderate", "High sugar foods worsen glycemic control in diabetic patients"),
    ("metformin", "jaggery", "Moderate", "High sugar content worsens glycemic control"),
    ("glipizide", "alcohol", "High", "Alcohol causes disulfiram-like reaction and severe hypoglycemia with sulfonylureas"),
    ("glimepiride", "alcohol", "High", "Alcohol can cause severe hypoglycemia and flushing with glimepiride"),
    ("insulin", "alcohol", "High", "Alcohol masks hypoglycemia symptoms and worsens insulin-induced low blood sugar"),
    ("insulin", "karela", "High", "Bitter gourd adds hypoglycemic effect — severe low blood sugar risk"),

    # ══════════════════════════════════════════════════
    # ANTIBIOTICS
    # ══════════════════════════════════════════════════
    ("ciprofloxacin", "milk", "High", "Dairy products containing calcium chelate ciprofloxacin — reduces absorption by up to 50%"),
    ("ciprofloxacin", "dairy", "High", "Calcium in dairy chelates ciprofloxacin — significantly reduces antibiotic absorption"),
    ("ciprofloxacin", "curd", "High", "Calcium in curd chelates ciprofloxacin — take 2 hours before or after dairy"),
    ("ciprofloxacin", "antacids", "High", "Antacids with calcium/magnesium chelate ciprofloxacin — greatly reduce absorption"),
    ("ciprofloxacin", "calcium", "High", "Calcium chelates ciprofloxacin reducing absorption significantly"),
    ("ciprofloxacin", "iron", "High", "Iron chelates fluoroquinolones — reduces ciprofloxacin absorption"),
    ("ciprofloxacin", "caffeine", "High", "Ciprofloxacin inhibits caffeine metabolism — caffeine toxicity risk"),
    ("ciprofloxacin", "coffee", "High", "Coffee caffeine levels increase significantly with ciprofloxacin — palpitations, anxiety"),
    ("amoxicillin", "alcohol", "Low", "Alcohol has minimal direct interaction but may reduce recovery from infection"),
    ("amoxicillin", "food", "None", "Food does not significantly affect amoxicillin absorption"),
    ("azithromycin", "antacids", "Moderate", "Aluminum/magnesium antacids reduce azithromycin absorption"),
    ("azithromycin", "alcohol", "Moderate", "Alcohol may reduce immune function and slow recovery"),
    ("tetracycline", "milk", "High", "Calcium in milk chelates tetracycline — reduces absorption by 65%"),
    ("tetracycline", "dairy", "High", "Dairy products chelate tetracycline — take on completely empty stomach"),
    ("tetracycline", "iron", "High", "Iron chelates tetracycline — take 2-3 hours apart"),
    ("tetracycline", "calcium", "High", "Calcium chelates tetracycline reducing absorption drastically"),
    ("doxycycline", "milk", "Moderate", "Dairy reduces doxycycline absorption moderately — take with water"),
    ("doxycycline", "iron", "High", "Iron chelates doxycycline — take 2-3 hours apart from iron"),
    ("doxycycline", "antacids", "High", "Antacids chelate doxycycline — avoid or take 2 hours apart"),
    ("metronidazole", "alcohol", "High", "Alcohol causes severe disulfiram-like reaction — nausea, vomiting, flushing"),
    ("metronidazole", "beer", "High", "Any alcohol causes severe disulfiram reaction — avoid completely"),
    ("metronidazole", "wine", "High", "Alcohol in wine causes disulfiram-like reaction with metronidazole"),

    # ══════════════════════════════════════════════════
    # ANTIDEPRESSANTS / SSRIs
    # ══════════════════════════════════════════════════
    ("sertraline", "alcohol", "High", "Alcohol worsens depression and increases sedation with sertraline"),
    ("sertraline", "grapefruit", "Moderate", "Grapefruit inhibits CYP3A4 — may increase sertraline blood levels"),
    ("fluoxetine", "alcohol", "High", "Alcohol increases sedation and CNS depression with fluoxetine"),
    ("fluoxetine", "grapefruit", "Moderate", "Grapefruit may increase fluoxetine levels via CYP3A4 inhibition"),
    ("fluoxetine", "st johns wort", "High", "St John's Wort with SSRIs causes serotonin syndrome — dangerous"),

    # ══════════════════════════════════════════════════
    # MAO INHIBITORS
    # ══════════════════════════════════════════════════
    ("phenelzine", "aged cheese", "High", "Aged cheese is very high in tyramine — MAOIs cause hypertensive crisis"),
    ("phenelzine", "cheddar", "High", "Cheddar is high in tyramine — dangerous hypertensive crisis with MAOIs"),
    ("phenelzine", "red wine", "High", "Red wine contains tyramine — MAOIs cause severe hypertensive crisis"),
    ("phenelzine", "beer", "High", "Beer contains tyramine — dangerous hypertensive crisis with MAOIs"),
    ("phenelzine", "soy sauce", "High", "Soy sauce is very high in tyramine — MAOIs cause hypertensive crisis"),
    ("phenelzine", "pickled foods", "High", "Pickled/fermented foods are high in tyramine — hypertensive crisis risk"),
    ("phenelzine", "achar", "High", "Pickled foods high in tyramine — dangerous with MAO inhibitors"),
    ("phenelzine", "cured meats", "High", "Cured meats contain tyramine — MAOIs cause dangerous blood pressure spike"),
    ("phenelzine", "banana", "Moderate", "Bananas contain some tyramine — moderate risk with MAO inhibitors"),
    ("phenelzine", "avocado", "Moderate", "Avocado contains some tyramine — moderate risk with MAO inhibitors"),
    ("phenelzine", "caffeine", "Moderate", "Caffeine has stimulant effects that may interact with MAO inhibitors"),

    # ══════════════════════════════════════════════════
    # CALCIUM CHANNEL BLOCKERS
    # ══════════════════════════════════════════════════
    ("amlodipine", "grapefruit", "High", "Grapefruit inhibits CYP3A4 — significantly increases amlodipine levels"),
    ("amlodipine", "grapefruit juice", "High", "Grapefruit juice increases amlodipine blood levels causing excessive hypotension"),
    ("amlodipine", "alcohol", "Moderate", "Alcohol enhances blood pressure lowering effect — hypotension risk"),
    ("nifedipine", "grapefruit", "High", "Grapefruit greatly increases nifedipine levels via CYP3A4 inhibition"),
    ("nifedipine", "grapefruit juice", "High", "Grapefruit juice increases nifedipine levels causing severe hypotension"),
    ("verapamil", "grapefruit", "High", "Grapefruit inhibits verapamil metabolism — toxicity risk"),
    ("verapamil", "alcohol", "Moderate", "Alcohol enhances verapamil's blood pressure lowering effect"),
    ("diltiazem", "grapefruit", "High", "Grapefruit inhibits diltiazem metabolism — increases blood levels"),
    ("diltiazem", "alcohol", "Moderate", "Alcohol increases diltiazem's hypotensive effect"),

    # ══════════════════════════════════════════════════
    # THYROID MEDICATIONS
    # ══════════════════════════════════════════════════
    ("levothyroxine", "soy", "High", "Soy products reduce levothyroxine absorption — take 4 hours apart"),
    ("levothyroxine", "tofu", "High", "Soy in tofu reduces levothyroxine absorption significantly"),
    ("levothyroxine", "calcium", "High", "Calcium supplements/foods reduce levothyroxine absorption"),
    ("levothyroxine", "milk", "Moderate", "Calcium in milk reduces levothyroxine absorption — take on empty stomach"),
    ("levothyroxine", "coffee", "Moderate", "Coffee reduces levothyroxine absorption — take 30 min before coffee"),
    ("levothyroxine", "iron", "High", "Iron chelates levothyroxine — reduces absorption significantly"),
    ("levothyroxine", "high fiber foods", "Moderate", "High fiber reduces levothyroxine absorption — take on empty stomach"),
    ("levothyroxine", "walnuts", "Moderate", "Walnuts can reduce levothyroxine absorption"),

    # ══════════════════════════════════════════════════
    # BLOOD PRESSURE MEDICATIONS
    # ══════════════════════════════════════════════════
    ("losartan", "potassium rich foods", "High", "ARBs increase potassium levels — high potassium foods cause dangerous hyperkalemia"),
    ("losartan", "bananas", "Moderate", "Bananas high in potassium — hyperkalemia risk with losartan"),
    ("losartan", "salt substitutes", "High", "Salt substitutes contain potassium — dangerous hyperkalemia with losartan"),
    ("losartan", "alcohol", "Moderate", "Alcohol enhances losartan's blood pressure lowering effect"),
    ("losartan", "licorice", "High", "Licorice causes sodium retention opposing losartan's antihypertensive effect"),
    ("furosemide", "licorice", "High", "Licorice causes potassium loss worsening furosemide-induced hypokalemia"),
    ("furosemide", "alcohol", "Moderate", "Alcohol enhances diuretic effect and hypotensive effect"),
    ("hydrochlorothiazide", "licorice", "High", "Licorice worsens hypokalemia caused by thiazide diuretics"),
    ("hydrochlorothiazide", "alcohol", "Moderate", "Alcohol enhances antihypertensive and diuretic effects"),

    # ══════════════════════════════════════════════════
    # PAIN MEDICATIONS / NSAIDs
    # ══════════════════════════════════════════════════
    ("ibuprofen", "alcohol", "High", "Alcohol combined with ibuprofen increases risk of stomach bleeding"),
    ("ibuprofen", "beer", "High", "Alcohol increases gastrointestinal bleeding risk with ibuprofen"),
    ("ibuprofen", "coffee", "Moderate", "Caffeine in coffee can worsen ibuprofen-related stomach irritation"),
    ("aspirin", "alcohol", "High", "Alcohol significantly increases risk of GI bleeding with aspirin"),
    ("aspirin", "grapefruit", "Low", "Minor interaction — grapefruit has minimal effect on aspirin"),
    ("paracetamol", "alcohol", "High", "Alcohol significantly increases hepatotoxicity risk with paracetamol"),
    ("paracetamol", "beer", "High", "Alcohol in beer greatly increases liver damage risk with paracetamol"),
    ("paracetamol", "wine", "High", "Alcohol in wine increases liver damage risk with paracetamol"),
    ("tramadol", "alcohol", "High", "Alcohol enhances CNS depression and respiratory depression with tramadol"),
    ("tramadol", "grapefruit", "Moderate", "Grapefruit inhibits tramadol metabolism — increases blood levels"),
    ("codeine", "alcohol", "High", "Alcohol enhances CNS depression and respiratory depression with codeine"),

    # ══════════════════════════════════════════════════
    # ANTIEPILEPTICS
    # ══════════════════════════════════════════════════
    ("carbamazepine", "grapefruit", "High", "Grapefruit inhibits CYP3A4 — greatly increases carbamazepine toxicity risk"),
    ("carbamazepine", "grapefruit juice", "High", "Grapefruit juice significantly increases carbamazepine blood levels"),
    ("carbamazepine", "alcohol", "High", "Alcohol increases CNS depression and lowers seizure threshold"),
    ("valproic acid", "alcohol", "High", "Alcohol enhances CNS depression and liver toxicity with valproate"),
    ("phenytoin", "alcohol", "High", "Chronic alcohol use reduces phenytoin levels — seizure risk"),
    ("phenytoin", "calcium", "Moderate", "High calcium intake may reduce phenytoin absorption"),
    ("lamotrigine", "alcohol", "Moderate", "Alcohol may lower seizure threshold with lamotrigine"),

    # ══════════════════════════════════════════════════
    # IMMUNOSUPPRESSANTS
    # ══════════════════════════════════════════════════
    ("cyclosporine", "grapefruit", "High", "Grapefruit significantly increases cyclosporine levels — toxicity risk"),
    ("cyclosporine", "grapefruit juice", "High", "Grapefruit juice greatly increases cyclosporine blood levels"),
    ("cyclosporine", "st johns wort", "High", "St John's Wort induces CYP3A4 — drastically reduces cyclosporine levels"),
    ("tacrolimus", "grapefruit", "High", "Grapefruit inhibits tacrolimus metabolism — toxicity and rejection risk"),
    ("tacrolimus", "grapefruit juice", "High", "Grapefruit juice greatly increases tacrolimus levels"),

    # ══════════════════════════════════════════════════
    # BENZODIAZEPINES / SEDATIVES
    # ══════════════════════════════════════════════════
    ("diazepam", "alcohol", "High", "Alcohol greatly enhances CNS depression with diazepam — respiratory depression risk"),
    ("diazepam", "grapefruit", "Moderate", "Grapefruit inhibits diazepam metabolism — increases sedation"),
    ("lorazepam", "alcohol", "High", "Alcohol potentiates lorazepam sedation — dangerous respiratory depression"),
    ("alprazolam", "alcohol", "High", "Alcohol greatly enhances alprazolam CNS depression"),
    ("alprazolam", "grapefruit", "High", "Grapefruit inhibits CYP3A4 — greatly increases alprazolam blood levels"),

    # ══════════════════════════════════════════════════
    # ANTIPSYCHOTICS
    # ══════════════════════════════════════════════════
    ("risperidone", "alcohol", "High", "Alcohol enhances CNS depression and sedation with risperidone"),
    ("quetiapine", "alcohol", "High", "Alcohol significantly enhances quetiapine sedation and CNS depression"),
    ("quetiapine", "grapefruit", "High", "Grapefruit inhibits quetiapine metabolism — increases blood levels"),
    ("olanzapine", "alcohol", "High", "Alcohol enhances CNS depression with olanzapine"),
    ("olanzapine", "caffeine", "Moderate", "Caffeine may reduce olanzapine effectiveness"),

    # ══════════════════════════════════════════════════
    # IRON SUPPLEMENTS
    # ══════════════════════════════════════════════════
    ("iron", "milk", "High", "Calcium in milk binds iron — take iron 2 hours before or after dairy"),
    ("iron", "coffee", "High", "Tannins in coffee bind iron — reduces absorption by up to 80%"),
    ("iron", "tea", "High", "Tannins in tea bind iron — significantly reduces iron absorption"),
    ("iron", "black tea", "High", "Black tea tannins severely reduce iron absorption"),
    ("iron", "calcium", "High", "Calcium competes with iron for absorption — take separately"),
    ("iron", "antacids", "High", "Antacids reduce stomach acid needed for iron absorption"),
    ("iron", "eggs", "Moderate", "Phosphoproteins in eggs may reduce iron absorption"),
    ("iron", "orange juice", "None", "Vitamin C in orange juice actually enhances iron absorption"),
    ("iron", "vitamin c", "None", "Vitamin C enhances non-heme iron absorption — beneficial combination"),

    # ══════════════════════════════════════════════════
    # CALCIUM SUPPLEMENTS
    # ══════════════════════════════════════════════════
    ("calcium", "iron", "High", "Calcium inhibits iron absorption — take at different times"),
    ("calcium", "high fiber foods", "Moderate", "High fiber may reduce calcium absorption slightly"),
    ("calcium", "spinach", "Moderate", "Oxalates in spinach bind calcium — reduces absorption"),
    ("calcium", "coffee", "Moderate", "Caffeine increases calcium excretion through urine"),

    # ══════════════════════════════════════════════════
    # ANTI-TB MEDICATIONS
    # ══════════════════════════════════════════════════
    ("isoniazid", "alcohol", "High", "Alcohol greatly increases hepatotoxicity risk with isoniazid"),
    ("isoniazid", "cheese", "High", "Isoniazid inhibits MAO — aged cheese causes hypertensive crisis"),
    ("isoniazid", "aged cheese", "High", "Aged cheese high in tyramine — isoniazid inhibits MAO causing crisis"),
    ("isoniazid", "tuna", "High", "Fish high in histamine — isoniazid inhibits histamine metabolism causing flushing"),
    ("isoniazid", "high fat meal", "Low", "High fat meals may reduce isoniazid absorption — take on empty stomach"),
    ("rifampicin", "alcohol", "High", "Alcohol combined with rifampicin greatly increases hepatotoxicity"),

    # ══════════════════════════════════════════════════
    # ANTIFUNGALS
    # ══════════════════════════════════════════════════
    ("fluconazole", "alcohol", "High", "Alcohol increases liver damage risk with fluconazole"),
    ("ketoconazole", "alcohol", "High", "Alcohol increases hepatotoxicity risk with ketoconazole"),
    ("ketoconazole", "grapefruit", "High", "Grapefruit inhibits ketoconazole metabolism"),
    ("itraconazole", "grapefruit juice", "High", "Grapefruit juice can affect itraconazole levels"),
    ("itraconazole", "cola", "Moderate", "Acidic beverages like cola increase itraconazole absorption"),

    # ══════════════════════════════════════════════════
    # PROTON PUMP INHIBITORS
    # ══════════════════════════════════════════════════
    ("omeprazole", "alcohol", "Moderate", "Alcohol may worsen acid reflux that omeprazole is treating"),
    ("omeprazole", "grapefruit", "Low", "Grapefruit has minimal clinically significant effect on omeprazole"),
    ("pantoprazole", "alcohol", "Moderate", "Alcohol worsens GERD symptoms that pantoprazole treats"),

    # ══════════════════════════════════════════════════
    # CORTICOSTEROIDS
    # ══════════════════════════════════════════════════
    ("prednisolone", "alcohol", "High", "Alcohol with corticosteroids increases GI bleeding and ulcer risk"),
    ("prednisolone", "grapefruit", "Moderate", "Grapefruit may increase prednisolone levels via CYP3A4 inhibition"),
    ("prednisolone", "high sodium foods", "High", "High sodium worsens fluid retention caused by corticosteroids"),
    ("prednisolone", "salt", "Moderate", "Excess salt worsens corticosteroid-induced fluid retention and hypertension"),
    ("prednisolone", "sugar", "High", "Corticosteroids raise blood sugar — high sugar foods worsen hyperglycemia"),
    ("dexamethasone", "alcohol", "High", "Alcohol with dexamethasone increases GI ulcer and bleeding risk"),
    ("dexamethasone", "high sodium foods", "High", "High sodium worsens dexamethasone-induced fluid retention"),

    # ══════════════════════════════════════════════════
    # DIGOXIN
    # ══════════════════════════════════════════════════
    ("digoxin", "licorice", "High", "Licorice causes potassium loss (hypokalemia) increasing digoxin toxicity risk"),
    ("digoxin", "high fiber foods", "Moderate", "High fiber reduces digoxin absorption — take separately"),
    ("digoxin", "st johns wort", "High", "St John's Wort reduces digoxin levels by inducing P-glycoprotein"),

    # ══════════════════════════════════════════════════
    # CLOPIDOGREL
    # ══════════════════════════════════════════════════
    ("clopidogrel", "grapefruit", "High", "Grapefruit inhibits CYP2C19 which activates clopidogrel — reduces effectiveness"),
    ("clopidogrel", "grapefruit juice", "High", "Grapefruit juice reduces clopidogrel activation — increases clot risk"),
    ("clopidogrel", "alcohol", "Moderate", "Alcohol with clopidogrel increases bleeding risk"),

]

# ─────────────────────────────────────────────────────────────
# Build lookup dictionary
# ─────────────────────────────────────────────────────────────
lookup = {}
for drug, food, risk, mechanism in INTERACTIONS:
    key = f"{drug.lower()}+{food.lower()}"
    key_rev = f"{food.lower()}+{drug.lower()}"
    entry = {"risk": risk, "mechanism": mechanism}
    lookup[key] = entry
    lookup[key_rev] = entry

print(f"✓ Built {len(INTERACTIONS)} drug-food interaction pairs")
print(f"✓ Total lookup keys: {len(lookup)}")

# Save
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "data", "processed", "drug_food_lookup.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(lookup, f, indent=2)
print(f"✓ Saved to {out_path}")