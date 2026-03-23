"""
Run this script once to extract food/supplement names from your DFI dataset.
Output: data/processed/food_list.json

Usage: python extract_foods.py  (from project root)
"""

import pandas as pd
import re
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_drug_food_interactions.csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "food_list.json")

# Load dataset
df = pd.read_csv(CSV_PATH)
texts = df["Interaction_Text"].dropna().str.lower().tolist()

# ── Patterns to extract food/supplement mentions ──
# These patterns match common ways foods appear in interaction text
EXTRACT_PATTERNS = [
    r"avoid\s+([\w\s,]+?)(?:\.|,|\band\b|$)",
    r"do not (?:eat|drink|take|consume|use)\s+([\w\s]+?)(?:\.|,|$)",
    r"(?:eating|drinking|consuming|taking)\s+([\w\s]+?)(?:\s+may|\s+can|\s+could|\.|,|$)",
    r"(?:with|and)\s+([\w\s]+?)\s+(?:juice|products|foods|supplements|extract)",
    r"examples? (?:include|are)[:\s]+([\w\s,]+?)(?:\.|$)",
    r"such as\s+([\w\s,]+?)(?:\.|$)",
    r"including\s+([\w\s,]+?)(?:\.|$)",
]

# Known food/supplement terms to look for directly
KNOWN_FOODS = [
    # Common interaction foods
    "alcohol", "grapefruit", "grapefruit juice", "milk", "dairy", "caffeine",
    "coffee", "tea", "green tea", "black tea", "spinach", "kale", "broccoli",
    "lettuce", "cabbage", "brussels sprouts", "salt", "sodium",
    "garlic", "ginger", "turmeric", "licorice",
    "cranberry", "cranberry juice", "pomelo", "bitter orange", "orange juice",
    "apple juice", "grape juice", "high fat meal", "fatty foods",
    "high fiber foods", "fiber", "bran", "oats", "tyramine",
    "aged cheese", "cured meats", "fermented foods", "soy sauce",
    "sauerkraut", "beer", "wine", "whiskey", "cola", "energy drinks",
    "bananas", "avocado", "tomatoes", "leafy greens", "bilberry",
    "danshen", "ginkgo biloba", "coenzyme q10",
    # Indian foods and drinks
    "rice", "white rice", "brown rice", "chapati", "roti", "paratha",
    "dal", "lentils", "rajma", "kidney beans", "chickpeas", "chana",
    "curd", "yogurt", "dahi", "buttermilk", "lassi", "chaas",
    "paneer", "ghee", "coconut oil", "mustard oil", "sesame oil",
    "coconut milk", "coconut water",
    "methi", "fenugreek", "fenugreek seeds", "methi leaves",
    "amla", "Indian gooseberry", "ashwagandha", "triphala", "neem",
    "tulsi", "basil", "curry leaves", "ajwain", "carom seeds",
    "cumin", "jeera", "coriander", "dhania", "fennel", "saunf",
    "cardamom", "elaichi", "cinnamon", "dalchini", "cloves",
    "black pepper", "red chilli", "green chilli",
    "tamarind", "imli", "kokum",
    "bitter gourd", "karela", "drumstick", "moringa",
    "papaya", "raw papaya", "pineapple", "mango", "raw mango",
    "jackfruit", "guava", "pomegranate", "watermelon",
    "onion", "raw onion", "garlic", "ginger",
    "potato", "sweet potato", "yam",
    "plantain", "raw banana",
    "soybean", "soy products", "tofu",
    "groundnuts", "peanuts", "cashews", "almonds", "walnuts",
    "sesame seeds", "til", "flaxseeds", "alsi",
    "jaggery", "sugar", "honey", "refined sugar",
    "pickle", "achar", "papad", "salted foods",
    "chai", "masala chai", "kadha", "herbal kadha",
    "fruit juice", "sugarcane juice", "coconut water",
    "sambar", "rasam", "idli", "dosa",
    "high sodium foods", "processed foods", "fried foods",
    # Chicken and meat
    "chicken", "grilled chicken", "fried chicken", "chicken curry",
    "chicken soup", "chicken liver",
    # South Indian foods
    "idli", "dosa", "masala dosa", "puri", "poori", "bhatura",
    "upma", "pongal", "vada", "medu vada", "uttapam",
    "sambar", "rasam", "coconut chutney", "tomato chutney",
    # North Indian foods
    "naan", "paratha", "aloo paratha", "poha", "khichdi",
    "biryani", "pulao", "chole", "pav bhaji",
    # Snacks and sweets
    "halwa", "ladoo", "barfi", "jalebi", "gulab jamun",
    "namkeen", "chakli", "murukku", "mixture",
    # More proteins
    "eggs", "boiled eggs", "fish", "mutton", "lamb",
    "prawns", "shrimp", "tofu", "paneer",
    # More fruits
    "orange", "apple", "grapes", "strawberry", "kiwi",
    "lemon", "lime", "raw mango", "dried fruits",
    "vitamin k rich foods", "iron rich foods", "calcium rich foods",
    "antacids", "calcium supplements", "iron supplements",
]

found = set()

# Method 1: Direct keyword matching in texts
for text in texts:
    for food in KNOWN_FOODS:
        if food in text:
            found.add(food)

# Method 2: Pattern extraction
for text in texts:
    for pattern in EXTRACT_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Split by comma and clean up
            items = [m.strip().strip('.').strip(',') for m in match.split(',')]
            for item in items:
                item = item.strip()
                # Filter: must be 2-40 chars, not just numbers, not too generic
                if 2 < len(item) < 40 and not item.isdigit():
                    # Remove common non-food words
                    skip_words = ['the', 'this', 'that', 'these', 'those', 'with', 
                                  'and', 'or', 'any', 'all', 'other', 'certain',
                                  'anticoagulant', 'antiplatelet', 'activity', 'effects',
                                  'supplements', 'medications', 'drugs', 'it', 'them']
                    if item not in skip_words and len(item.split()) <= 4:
                        found.add(item)

# Clean and filter garbage
BAD_STARTS = ['and ', 'or ', 'as ', 'a ', 'the ', 'with ', 'to ', 'of ', 'in ', 'for ']
BAD_WORDS = ['death', 'occur', 'cramping', 'headache', 'nausea', 'vomiting', 'diarrhea',
             'effect', 'activity', 'medication', 'drug', 'dose', 'patient', 'interaction',
             'monitor', 'drinking', 'eating', 'taking', 'using', 'concomitant',
             'treatment', 'therapy', 'symptom', 'adverse', 'toxicity', 'absorption',
             'clearance', 'metabolism', 'plasma', 'serum', 'blood', 'level',
             'inhibit', 'induce', 'increase', 'decrease', 'reduce', 'elevate']

# Also filter items that look like drug names (end in common drug suffixes)
DRUG_SUFFIXES = ['mab', 'nib', 'xib', 'zole', 'pine', 'pril', 'sartan', 'statin',
                 'mycin', 'cillin', 'cycline', 'oxacin', 'prazole', 'olol',
                 'with food', 'with alcohol', 'with meal']

clean = set()
for f in found:
    f = f.strip().lower()
    # Strip trailing noise words
    for noise in [' containing', ' fortified', ' products', ' rich foods',
                  ' supplements', ' extract', ' juice products', ' and high fiber',
                  ' and calcium', ' and garlic', ' and ginkgo biloba',
                  ' containing magnesium', ' containing aluminum', ' sequestrants',
                  ' acid sequestrants']:
        if f.endswith(noise):
            f = f[:-len(noise)].strip()
    if len(f) < 3 or len(f) > 30: continue
    if any(f.startswith(b) for b in BAD_STARTS): continue
    if any(b in f for b in BAD_WORDS): continue
    # Skip known non-food items
    NON_FOODS = ['bile acid', 'sequestrant', 'aluminum', 'antacid', 'laxative',
                 'mineral oil', 'charcoal', 'resin', 'chelat', 'pectin bound']
    if any(nf in f for nf in NON_FOODS): continue
    if any(f.endswith(s) for s in DRUG_SUFFIXES): continue
    if f[0].isdigit(): continue
    words = f.split()
    if len(words) > 3: continue  # skip long phrases
    if all(w in ['and','or','the','a','an','with','of','in'] for w in words): continue
    clean.add(f)

# Always include known foods
clean.update(KNOWN_FOODS)

food_list = sorted([f.title() for f in clean])

# Save
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, 'w') as f:
    json.dump(food_list, f, indent=2)

print(f"✓ Extracted {len(food_list)} food/supplement items")
print(f"✓ Saved to {OUT_PATH}")
print("\nSample items:")
for item in food_list[:20]:
    print(f"  - {item}")