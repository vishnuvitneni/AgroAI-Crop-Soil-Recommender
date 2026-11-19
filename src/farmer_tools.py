"""
Farmer Problem Solving Toolkit:
1. Fertilizer Bag Dosage Calculator
2. Crop Pest & Disease Diagnostic Doctor
3. Kisan Helplines & Government Assistance Directory
"""
import math

# Standard ICAR N-P-K recommendations (kg per hectare)
CROP_FERT_GUIDELINES = {
    "rice": {"name": "Paddy / Rice", "n": 120, "p": 60, "k": 40},
    "wheat": {"name": "Wheat", "n": 120, "p": 60, "k": 40},
    "maize": {"name": "Maize / Corn", "n": 120, "p": 60, "k": 50},
    "cotton": {"name": "Cotton", "n": 100, "p": 50, "k": 50},
    "sugarcane": {"name": "Sugarcane", "n": 250, "p": 100, "k": 120},
    "tomato": {"name": "Tomato", "n": 100, "p": 80, "k": 60},
    "potato": {"name": "Potato", "n": 150, "p": 100, "k": 100},
    "chickpea": {"name": "Chickpea / Chana", "n": 20, "p": 50, "k": 20},
    "banana": {"name": "Banana", "n": 200, "p": 80, "k": 250},
    "chilli": {"name": "Chilli", "n": 120, "p": 60, "k": 60}
}

PEST_DISEASE_CATALOG = [
    {
        "id": "yellow_leaves",
        "symptom": "Yellowing of older leaves starting from leaf tips and V-shape drying",
        "crop_affected": "Paddy, Maize, Wheat, Vegetables",
        "diagnosis": "Nitrogen (N) Deficiency / Chlorosis",
        "severity": "Moderate",
        "organic_remedy": "Foliar spray of 5% Jeevamrutha or 2% Vermiwash. Apply cow dung compost.",
        "chemical_remedy": "Foliar spray of 2% Urea solution (20g Urea in 1 liter water) or top-dress 15-20 kg Urea per acre with light irrigation.",
        "prevention": "Perform soil testing and apply balanced NPK at sowing."
    },
    {
        "id": "leaf_blast",
        "symptom": "Spindle-shaped or diamond spots with grey centers and brown margins on leaves",
        "crop_affected": "Rice / Paddy, Finger Millet (Ragi)",
        "diagnosis": "Leaf Blast (Pyricularia oryzae fungal infection)",
        "severity": "High / Critical",
        "organic_remedy": "Foliar spray of Pseudomonas fluorescens (5g/liter) or sour buttermilk spray (5%).",
        "chemical_remedy": "Spray Tricyclazole 75% WP @ 0.6g/liter OR Isoprothiolane 40% EC @ 1.5ml/liter immediately.",
        "prevention": "Avoid excess nitrogen fertilizer during cloudy, humid weather. Use blast-resistant seed varieties."
    },
    {
        "id": "leaf_curl",
        "symptom": "Upward or downward leaf curling, crinkling, stunted growth, and yellow mottling",
        "crop_affected": "Chilli, Tomato, Papaya, Cotton",
        "diagnosis": "Chilli Leaf Curl Virus (transmitted by Thrips and Whiteflies)",
        "severity": "High",
        "organic_remedy": "Install yellow and blue sticky traps (15-20 traps/acre). Spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil 10,000 ppm @ 2ml/liter.",
        "chemical_remedy": "Control vector insects by spraying Diafenthiuron 50% WP @ 1.25g/liter OR Fipronil 5% SC @ 2ml/liter.",
        "prevention": "Erect tall barrier crops (Maize/Jowar) on field borders to block incoming whitefly vectors."
    },
    {
        "id": "stem_borer",
        "symptom": "Central shoot withers and dries up ('Dead Heart' in vegetative stage, 'White Earhead' at flowering)",
        "crop_affected": "Rice, Maize, Sugarcane",
        "diagnosis": "Yellow Stem Borer (Scirpophaga incertulas)",
        "severity": "Critical",
        "organic_remedy": "Set up Pheromone traps @ 5 per acre. Release Trichogramma japonicum egg parasitoids @ 40,000/acre.",
        "chemical_remedy": "Apply Chlorantraniliprole 0.4% G (Ferterra) @ 4 kg/acre in standing water OR spray Chlorantraniliprole 18.5% SC (Coragen) @ 0.3ml/liter.",
        "prevention": "Clip seedling leaf tips before transplanting to remove egg masses. Avoid delayed transplanting."
    },
    {
        "id": "powdery_mildew",
        "symptom": "White, talcum-powder like powdery growth covering upper and lower leaf surfaces",
        "crop_affected": "Grapes, Mango, Peas, Cucurbits, Pulses",
        "diagnosis": "Powdery Mildew (Erysiphe / Oidium fungal spores)",
        "severity": "Moderate to High",
        "organic_remedy": "Spray Baking soda (Sodium bicarbonate) solution (5g/liter + 2ml liquid soap) or 10% cow milk spray in sunlight.",
        "chemical_remedy": "Spray Wettable Sulfur 80% WP @ 2.5g/liter OR Hexaconazole 5% EC @ 1ml/liter.",
        "prevention": "Ensure good field aeration, canopy pruning, and avoid dense shading."
    },
    {
        "id": "root_rot_wilt",
        "symptom": "Sudden wilting of healthy plants in patches, vascular browning, and root decay",
        "crop_affected": "Cotton, Chickpea, Pigeon Pea, Tomato",
        "diagnosis": "Fusarium Wilt / Rhizoctonia Root Rot (Soil-borne pathogen)",
        "severity": "Critical",
        "organic_remedy": "Soil drenching with Trichoderma viride bio-fungicide (10g/liter mixed with well-rotted FYM).",
        "chemical_remedy": "Drench roots with Carbendazim 50% WP @ 2g/liter OR Copper Oxychloride 50% WP @ 3g/liter around base of plants.",
        "prevention": "Ensure field drainage to eliminate waterlogging. Practice 3-year crop rotation with non-host cereals."
    }
]

GOVT_HELPLINES = [
    {
        "service": "Kisan Call Centre (Govt of India)",
        "phone": "1800-180-1551",
        "type": "Toll-Free Agricultural Advice in 22 Regional Languages (6 AM - 10 PM)",
        "icon": "📞"
    },
    {
        "service": "PM-Kisan Samman Nidhi Helpline",
        "phone": "155261 / 011-24300606",
        "type": "Direct DBT installment & eligibility inquiries",
        "icon": "🏛️"
    },
    {
        "service": "PM Fasal Bima Yojana (Crop Insurance)",
        "phone": "1800-200-5142",
        "type": "Crop loss claim registration within 72 hours of natural calamity",
        "icon": "🛡️"
    },
    {
        "service": "National Seeds Corporation Helpline",
        "phone": "011-25846292",
        "type": "Certified breeder/foundation seed availability",
        "icon": "🌱"
    }
]

def calculate_fertilizer_bags(crop_key, land_size_val, unit="acre"):
    """
    Calculates exact commercial fertilizer bags (Urea, DAP, MOP) required.
    1 Acre = 0.4046 Hectare.
    Urea Bag = 45 kg (contains 46% N)
    DAP Bag = 50 kg (contains 18% N, 46% P2O5)
    MOP Bag = 50 kg (contains 60% K2O)
    """
    crop = CROP_FERT_GUIDELINES.get(crop_key.lower(), CROP_FERT_GUIDELINES["rice"])
    
    # Standardize area to hectares
    area_ha = float(land_size_val) if unit.lower() == "hectare" else float(land_size_val) * 0.4047
    
    req_n = crop["n"] * area_ha
    req_p = crop["p"] * area_ha
    req_k = crop["k"] * area_ha
    
    # 1. DAP provides all Phosphorus:
    # 50 kg DAP has 23 kg P2O5 (46%) and 9 kg N (18%)
    dap_kg = req_p / 0.46
    dap_bags = round(dap_kg / 50.0, 1)
    n_from_dap = dap_kg * 0.18
    
    # 2. Urea provides remaining Nitrogen:
    # 45 kg Urea has 20.7 kg N (46%)
    remaining_n = max(0.0, req_n - n_from_dap)
    urea_kg = remaining_n / 0.46
    urea_bags = round(urea_kg / 45.0, 1)
    
    # 3. MOP provides Potassium:
    # 50 kg MOP has 30 kg K2O (60%)
    mop_kg = req_k / 0.60
    mop_bags = round(mop_kg / 50.0, 1)
    
    return {
        "crop_name": crop["name"],
        "land_size": land_size_val,
        "unit": unit.title(),
        "nutrients_needed": {
            "N_kg": round(req_n, 1),
            "P_kg": round(req_p, 1),
            "K_kg": round(req_k, 1)
        },
        "bags_required": {
            "dap": {"bags": dap_bags, "kg": round(dap_kg, 1), "bag_weight": "50 kg bag", "timing": "100% Basal at sowing / transplanting"},
            "urea": {"bags": urea_bags, "kg": round(urea_kg, 1), "bag_weight": "45 kg bag", "timing": "Apply in 2 equal splits (Tillering & Panicle/Flowering stage)"},
            "mop": {"bags": mop_bags, "kg": round(mop_kg, 1), "bag_weight": "50 kg bag", "timing": "100% Basal or 50% Basal + 50% at Panicle initiation"}
        },
        "safety_tip": "Always apply Urea after weeding and when soil has optimal moisture. Avoid applying synthetic fertilizer during heavy rain."
    }

def get_pest_and_disease_guide(query=None):
    """Search or return crop disease symptoms and remedies"""
    if not query or not query.strip():
        return PEST_DISEASE_CATALOG
    q = query.strip().lower()
    return [
        p for p in PEST_DISEASE_CATALOG
        if q in p["symptom"].lower() or q in p["diagnosis"].lower() or q in p["crop_affected"].lower()
    ]

def get_helplines():
    return GOVT_HELPLINES
