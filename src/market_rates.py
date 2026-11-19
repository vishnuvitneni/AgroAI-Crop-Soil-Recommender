"""
Live Mandi & Market Rates Tracker for Crops and Vegetables
Provides current APMC/Mandi benchmark rates, MSP comparisons, and price trends.
"""

COMMODITY_PRICES = [
    # Vegetables
    {
        "id": "tomato",
        "commodity": "Tomato (Hybrid / Local)",
        "category": "Vegetables",
        "icon": "🍅",
        "modal_price": 2400,
        "min_price": 1800,
        "max_price": 3100,
        "price_per_kg": 24.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+6.2%",
        "primary_mandi": "Madanapalle (AP) / Kolar (KA) / Azadpur (Delhi)",
        "msp": None,
        "arrival_status": "Moderate arrivals, high festive demand"
    },
    {
        "id": "onion",
        "commodity": "Onion (Red / Nasik)",
        "category": "Vegetables",
        "icon": "🧅",
        "modal_price": 3200,
        "min_price": 2600,
        "max_price": 3900,
        "price_per_kg": 32.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+0.8%",
        "primary_mandi": "Lasalgaon (MH) / Pimpalgaon (MH) / Bangalore",
        "msp": None,
        "arrival_status": "Steady supply from Kharif harvest"
    },
    {
        "id": "potato",
        "commodity": "Potato (Jyoti / Chipsona)",
        "category": "Vegetables",
        "icon": "🥔",
        "modal_price": 1650,
        "min_price": 1300,
        "max_price": 2000,
        "price_per_kg": 16.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "falling",
        "change_pct": "-2.4%",
        "primary_mandi": "Agra (UP) / Farrukhabad (UP) / Hooghly (WB)",
        "msp": None,
        "arrival_status": "High cold storage releases"
    },
    {
        "id": "green_chilli",
        "commodity": "Green Chilli",
        "category": "Vegetables",
        "icon": "🌶️",
        "modal_price": 4500,
        "min_price": 3800,
        "max_price": 5400,
        "price_per_kg": 45.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+8.5%",
        "primary_mandi": "Guntur (AP) / Hubli (KA) / Byadgi",
        "msp": None,
        "arrival_status": "Strong export and domestic demand"
    },
    {
        "id": "ginger",
        "commodity": "Ginger (Adrak / Fresh)",
        "category": "Vegetables",
        "icon": "🫚",
        "modal_price": 8200,
        "min_price": 6900,
        "max_price": 9600,
        "price_per_kg": 82.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+4.1%",
        "primary_mandi": "Wayanad (KL) / Shimoga (KA) / Guwahati",
        "msp": None,
        "arrival_status": "High demand, lean seasonal arrivals"
    },
    {
        "id": "garlic",
        "commodity": "Garlic (Lahsun)",
        "category": "Vegetables",
        "icon": "🧄",
        "modal_price": 14500,
        "min_price": 12000,
        "max_price": 17500,
        "price_per_kg": 145.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+1.2%",
        "primary_mandi": "Mandsaur (MP) / Neemuch (MP) / Kota (RJ)",
        "msp": None,
        "arrival_status": "Tight supply, firm market"
    },
    {
        "id": "cabbage",
        "commodity": "Cabbage / Patta Gobhi",
        "category": "Vegetables",
        "icon": "🥬",
        "modal_price": 1200,
        "min_price": 900,
        "max_price": 1500,
        "price_per_kg": 12.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "falling",
        "change_pct": "-4.0%",
        "primary_mandi": "Pune (MH) / Nashik / Belgaum (KA)",
        "msp": None,
        "arrival_status": "Heavy local farm arrivals"
    },
    {
        "id": "okra",
        "commodity": "Okra / Bhindi / Lady Finger",
        "category": "Vegetables",
        "icon": "🌿",
        "modal_price": 3100,
        "min_price": 2400,
        "max_price": 3800,
        "price_per_kg": 31.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+0.5%",
        "primary_mandi": "Vashi (Navi Mumbai) / Hyderabad / Surat",
        "msp": None,
        "arrival_status": "Balanced supply & demand"
    },

    # Cereals & Grains
    {
        "id": "paddy_common",
        "commodity": "Paddy / Rice (Common Grade)",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "modal_price": 2350,
        "min_price": 2250,
        "max_price": 2500,
        "price_per_kg": 23.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+1.8%",
        "primary_mandi": "Khanna (Punjab) / Karnal (HR) / Gondia (MH)",
        "msp": 2300,
        "arrival_status": "Government MSP procurement active"
    },
    {
        "id": "wheat",
        "commodity": "Wheat / Gehun (Lokwan / Sharbati)",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "modal_price": 2650,
        "min_price": 2400,
        "max_price": 2900,
        "price_per_kg": 26.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+3.0%",
        "primary_mandi": "Indore (MP) / Kota (RJ) / Khanna (Punjab)",
        "msp": 2275,
        "arrival_status": "Trading above MSP on strong flour mill buying"
    },
    {
        "id": "maize",
        "commodity": "Maize / Corn (Makka)",
        "category": "Cereals & Grains",
        "icon": "🌽",
        "modal_price": 2220,
        "min_price": 2000,
        "max_price": 2450,
        "price_per_kg": 22.2,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+2.5%",
        "primary_mandi": "Davangere (KA) / Nabarangpur (OD) / Gulabbagh (BR)",
        "msp": 2090,
        "arrival_status": "Heavy demand from poultry feed & ethanol sectors"
    },
    {
        "id": "bajra",
        "commodity": "Pearl Millet / Bajra",
        "category": "Cereals & Grains",
        "icon": "🌾",
        "modal_price": 2250,
        "min_price": 2100,
        "max_price": 2450,
        "price_per_kg": 22.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+0.4%",
        "primary_mandi": "Jaipur (RJ) / Mehsana (GJ) / Agra (UP)",
        "msp": 2625,
        "arrival_status": "Active winter food consumption"
    },

    # Pulses
    {
        "id": "chickpea",
        "commodity": "Chickpea / Bengal Gram (Chana)",
        "category": "Pulses",
        "icon": "🌱",
        "modal_price": 6800,
        "min_price": 6300,
        "max_price": 7250,
        "price_per_kg": 68.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+4.2%",
        "primary_mandi": "Bikaner (RJ) / Akola (MH) / Latur (MH)",
        "msp": 5440,
        "arrival_status": "Strong festival & dal mill demand"
    },
    {
        "id": "pigeonpeas",
        "commodity": "Pigeon Pea / Tur / Arhar Dal",
        "category": "Pulses",
        "icon": "🌿",
        "modal_price": 10500,
        "min_price": 9600,
        "max_price": 11800,
        "price_per_kg": 105.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+3.7%",
        "primary_mandi": "Kalaburagi (KA) / Latur (MH) / Akola (MH)",
        "msp": 7550,
        "arrival_status": "High price due to lean domestic buffer"
    },
    {
        "id": "blackgram",
        "commodity": "Black Gram / Urad Dal",
        "category": "Pulses",
        "icon": "🫘",
        "modal_price": 8600,
        "min_price": 7900,
        "max_price": 9400,
        "price_per_kg": 86.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "-0.6%",
        "primary_mandi": "Latur (MH) / Guntur (AP) / Kota (RJ)",
        "msp": 7400,
        "arrival_status": "Steady trade flow"
    },
    {
        "id": "mungbean",
        "commodity": "Green Gram / Moong Dal",
        "category": "Pulses",
        "icon": "🌱",
        "modal_price": 8200,
        "min_price": 7500,
        "max_price": 8900,
        "price_per_kg": 82.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+0.2%",
        "primary_mandi": "Merta City (RJ) / Sumerpur (RJ) / Jalna",
        "msp": 8682,
        "arrival_status": "Purchases active at support levels"
    },

    # Cash Crops & Commercial
    {
        "id": "cotton",
        "commodity": "Cotton (Medium/Long Staple Kapas)",
        "category": "Cash Crops",
        "icon": "☁️",
        "modal_price": 7400,
        "min_price": 6800,
        "max_price": 7900,
        "price_per_kg": 74.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+2.9%",
        "primary_mandi": "Rajkot (GJ) / Warangal (TS) / Abohar (PB)",
        "msp": 7121,
        "arrival_status": "CCI procurement active, spinning mills buying"
    },
    {
        "id": "soybean",
        "commodity": "Soybean (Yellow)",
        "category": "Cash Crops",
        "icon": "🌱",
        "modal_price": 4550,
        "min_price": 4150,
        "max_price": 4900,
        "price_per_kg": 45.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "-0.5%",
        "primary_mandi": "Indore (MP) / Ujjain (MP) / Nagpur (MH)",
        "msp": 4892,
        "arrival_status": "Crushing plants active, crushing margins stable"
    },
    {
        "id": "mustard",
        "commodity": "Mustard / Sarson Seed",
        "category": "Cash Crops",
        "icon": "🌼",
        "modal_price": 5750,
        "min_price": 5300,
        "max_price": 6200,
        "price_per_kg": 57.5,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "rising",
        "change_pct": "+3.1%",
        "primary_mandi": "Jaipur (RJ) / Alwar (RJ) / Bharatpur (RJ)",
        "msp": 5650,
        "arrival_status": "Winter edible oil consumption surge"
    },
    {
        "id": "groundnut",
        "commodity": "Groundnut / Peanut (In-Shell)",
        "category": "Cash Crops",
        "icon": "🥜",
        "modal_price": 6600,
        "min_price": 5900,
        "max_price": 7300,
        "price_per_kg": 66.0,
        "unit": "₹ / Quintal (100 kg)",
        "trend": "stable",
        "change_pct": "+1.1%",
        "primary_mandi": "Gondal (GJ) / Rajkot (GJ) / Anantapur (AP)",
        "msp": 6783,
        "arrival_status": "High peanut butter & export quality demand"
    }
]

def get_all_market_rates(category=None, query=None):
    """Filter market rates by category or commodity name"""
    results = COMMODITY_PRICES
    if category and category != "All":
        results = [c for c in results if c["category"].lower() == category.lower()]
    if query and query.strip():
        q = query.strip().lower()
        results = [
            c for c in results 
            if q in c["commodity"].lower() or q in c["primary_mandi"].lower()
        ]
    return results

def get_commodity_by_id(comm_id):
    c_id = comm_id.strip().lower()
    for item in COMMODITY_PRICES:
        if item["id"] == c_id:
            return item
    return None
