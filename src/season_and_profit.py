"""
Seasonal Crop Calendar & Land Area / Yield / Profit Estimator
Helps farmers plan sowing schedules, seed rates, expected yield, and net farm profits.
"""

SEASON_DATA = {
    "kharif": {
        "name": "Kharif Season (Monsoon / Summer)",
        "icon": "🌧️",
        "sowing_period": "June – July (With onset of South-West Monsoon)",
        "harvest_period": "September – November",
        "climate_character": "Warm, high humidity, abundant rainfall",
        "key_crops": [
            {"id": "rice", "name": "Paddy / Rice", "icon": "🌾", "duration": "110-140 days", "water_need": "High", "profit_potential": "High"},
            {"id": "cotton", "name": "Cotton (Kapas)", "icon": "☁️", "duration": "160-180 days", "water_need": "Medium", "profit_potential": "Very High"},
            {"id": "maize", "name": "Maize (Corn)", "icon": "🌽", "duration": "90-105 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "soybean", "name": "Soybean", "icon": "🌱", "duration": "90-100 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "pigeonpeas", "name": "Pigeon Pea (Tur/Arhar)", "icon": "🌿", "duration": "150-180 days", "water_need": "Low-Medium", "profit_potential": "Very High"},
            {"id": "groundnut", "name": "Groundnut / Peanut", "icon": "🥜", "duration": "105-120 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "jute", "name": "Jute (Golden Fiber)", "icon": "🌾", "duration": "120-135 days", "water_need": "High", "profit_potential": "Medium"}
        ]
    },
    "rabi": {
        "name": "Rabi Season (Winter)",
        "icon": "❄️",
        "sowing_period": "October – December (Post-monsoon retreat)",
        "harvest_period": "February – April",
        "climate_character": "Cold winter vegetative stage, warm dry harvest",
        "key_crops": [
            {"id": "wheat", "name": "Wheat (Gehun)", "icon": "🌾", "duration": "120-135 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "mustard", "name": "Mustard (Sarson)", "icon": "🌼", "duration": "100-115 days", "water_need": "Low", "profit_potential": "Very High"},
            {"id": "chickpea", "name": "Chickpea (Chana)", "icon": "🌱", "duration": "100-120 days", "water_need": "Low", "profit_potential": "High"},
            {"id": "potato", "name": "Potato", "icon": "🥔", "duration": "85-105 days", "water_need": "Medium", "profit_potential": "Very High"},
            {"id": "lentil", "name": "Lentil (Masoor)", "icon": "🥣", "duration": "110-125 days", "water_need": "Low", "profit_potential": "Medium"},
            {"id": "onion", "name": "Rabi Onion", "icon": "🧅", "duration": "130-150 days", "water_need": "Medium", "profit_potential": "Very High"}
        ]
    },
    "zaid": {
        "name": "Zaid Season (Spring / Summer)",
        "icon": "☀️",
        "sowing_period": "March – April",
        "harvest_period": "May – June (Before monsoon breaks)",
        "climate_character": "Long sunny days, warm temperatures, low rainfall",
        "key_crops": [
            {"id": "watermelon", "name": "Watermelon", "icon": "🍉", "duration": "75-90 days", "water_need": "Medium", "profit_potential": "Very High"},
            {"id": "muskmelon", "name": "Muskmelon / Cantaloupe", "icon": "🍈", "duration": "70-85 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "mungbean", "name": "Moong (Green Gram)", "icon": "🌱", "duration": "60-70 days", "water_need": "Low", "profit_potential": "High"},
            {"id": "okra", "name": "Okra (Bhindi)", "icon": "🌿", "duration": "60-90 days", "water_need": "Medium", "profit_potential": "High"},
            {"id": "cucumber", "name": "Cucumber (Kheera)", "icon": "🥒", "duration": "50-65 days", "water_need": "Medium", "profit_potential": "High"}
        ]
    }
}

# Agronomic benchmarks per Acre (1 Acre = 0.4047 Hectare)
CROP_BUDGET_BENCHMARKS = {
    "rice": {
        "name": "Paddy / Rice",
        "seed_rate_kg_per_acre": 16.0,
        "spacing": "20 cm x 15 cm",
        "water_irrigations": "15-20 cycles (or continuous flooding)",
        "yield_qtl_per_acre": 24.0,  # 24 Quintals / Acre
        "avg_cost_per_acre": 22000,   # Seeds + Fert + Labor + Transplanting
        "mandi_rate_per_qtl": 2350,   # ₹2,350/Qtl
        "duration_days": "120-135 days"
    },
    "wheat": {
        "name": "Wheat",
        "seed_rate_kg_per_acre": 40.0,
        "spacing": "22.5 cm row spacing",
        "water_irrigations": "4-6 irrigations at critical stages",
        "yield_qtl_per_acre": 20.0,
        "avg_cost_per_acre": 17000,
        "mandi_rate_per_qtl": 2650,
        "duration_days": "120-130 days"
    },
    "cotton": {
        "name": "Cotton (Bt)",
        "seed_rate_kg_per_acre": 1.8,  # Packets (approx 900g-1.8kg)
        "spacing": "90 cm x 60 cm (or 120 x 45 cm)",
        "water_irrigations": "5-8 irrigations (critical at boll formation)",
        "yield_qtl_per_acre": 12.0,
        "avg_cost_per_acre": 26000,
        "mandi_rate_per_qtl": 7400,
        "duration_days": "160-180 days"
    },
    "maize": {
        "name": "Maize (Hybrid)",
        "seed_rate_kg_per_acre": 8.0,
        "spacing": "60 cm x 20 cm",
        "water_irrigations": "4-6 irrigations (sensitive at tasseling)",
        "yield_qtl_per_acre": 28.0,
        "avg_cost_per_acre": 18500,
        "mandi_rate_per_qtl": 2220,
        "duration_days": "95-105 days"
    },
    "tomato": {
        "name": "Tomato (Hybrid)",
        "seed_rate_kg_per_acre": 0.15,  # 150 grams hybrid seedlings
        "spacing": "60 cm x 45 cm (staked)",
        "water_irrigations": "Regular drip / 8-12 irrigations",
        "yield_qtl_per_acre": 140.0, # 14 tonnes / acre
        "avg_cost_per_acre": 45000,
        "mandi_rate_per_qtl": 2400,
        "duration_days": "110-130 days"
    },
    "onion": {
        "name": "Onion",
        "seed_rate_kg_per_acre": 4.0,
        "spacing": "15 cm x 10 cm",
        "water_irrigations": "10-12 light irrigations",
        "yield_qtl_per_acre": 100.0,
        "avg_cost_per_acre": 35000,
        "mandi_rate_per_qtl": 3200,
        "duration_days": "125-140 days"
    },
    "chickpea": {
        "name": "Chickpea (Chana)",
        "seed_rate_kg_per_acre": 30.0,
        "spacing": "30 cm x 10 cm",
        "water_irrigations": "1-2 irrigations (branching & pod formation)",
        "yield_qtl_per_acre": 8.5,
        "avg_cost_per_acre": 13000,
        "mandi_rate_per_qtl": 6800,
        "duration_days": "100-115 days"
    },
    "mustard": {
        "name": "Mustard (Sarson)",
        "seed_rate_kg_per_acre": 2.0,
        "spacing": "30 cm x 10 cm",
        "water_irrigations": "2-3 irrigations",
        "yield_qtl_per_acre": 9.0,
        "avg_cost_per_acre": 11000,
        "mandi_rate_per_qtl": 5750,
        "duration_days": "100-115 days"
    },
    "watermelon": {
        "name": "Watermelon",
        "seed_rate_kg_per_acre": 1.2,
        "spacing": "2.0 m x 0.6 m (in furrows)",
        "water_irrigations": "6-9 irrigations (drip recommended)",
        "yield_qtl_per_acre": 160.0, # 16 tonnes / acre
        "avg_cost_per_acre": 32000,
        "mandi_rate_per_qtl": 1400,
        "duration_days": "75-90 days"
    },
    "pigeonpeas": {
        "name": "Pigeon Pea (Tur)",
        "seed_rate_kg_per_acre": 6.0,
        "spacing": "90 cm x 20 cm",
        "water_irrigations": "Rainfed or 2 supplementary irrigations",
        "yield_qtl_per_acre": 7.5,
        "avg_cost_per_acre": 14000,
        "mandi_rate_per_qtl": 10500,
        "duration_days": "150-170 days"
    }
}

def estimate_farm_budget(crop_key, land_size_val, unit="acre"):
    """
    Computes required seed quantity, harvest yield, revenue, cultivation cost, and estimated net profit.
    Units:
    - 1 Acre = 1.0 Acre
    - 1 Hectare = 2.471 Acres
    - 1 Gunta = 0.025 Acre (40 Guntas = 1 Acre)
    """
    crop_id = crop_key.lower().strip()
    bench = CROP_BUDGET_BENCHMARKS.get(crop_id, CROP_BUDGET_BENCHMARKS["rice"])
    
    val = float(land_size_val)
    unit_str = unit.lower()
    
    if unit_str == "hectare":
        acres = val * 2.471
    elif unit_str == "gunta":
        acres = val / 40.0
    else:
        acres = val  # default acre
        
    acres = max(0.01, acres)
    
    total_seed_kg = round(bench["seed_rate_kg_per_acre"] * acres, 2)
    expected_yield_qtl = round(bench["yield_qtl_per_acre"] * acres, 1)
    expected_yield_tonnes = round(expected_yield_qtl / 10.0, 1)
    
    gross_revenue = round(expected_yield_qtl * bench["mandi_rate_per_qtl"])
    total_cost = round(bench["avg_cost_per_acre"] * acres)
    net_profit = round(gross_revenue - total_cost)
    
    roi_percent = round((net_profit / total_cost * 100) if total_cost > 0 else 0, 1)
    
    return {
        "crop_key": crop_id,
        "crop_name": bench["name"],
        "input_land_size": land_size_val,
        "unit": unit.title(),
        "calculated_acres": round(acres, 2),
        "seed_required_kg": total_seed_kg,
        "seed_rate_required": f"{total_seed_kg} kg seeds",
        "plant_spacing": bench["spacing"],
        "spacing_cm": bench["spacing"],
        "irrigation_plan": bench["water_irrigations"],
        "water_requirement": bench["water_irrigations"],
        "expected_yield_qtl": expected_yield_qtl,
        "expected_yield_quintals": expected_yield_qtl,
        "expected_yield_tonnes": expected_yield_tonnes,
        "mandi_rate_applied": bench["mandi_rate_per_qtl"],
        "mandi_price_per_quintal": bench["mandi_rate_per_qtl"],
        "gross_revenue_inr": gross_revenue,
        "cultivation_cost_inr": total_cost,
        "net_profit_inr": net_profit,
        "estimated_net_profit_inr": net_profit,
        "roi_percent": roi_percent,
        "roi_percentage": roi_percent,
        "crop_duration": bench["duration_days"],
        "duration_days": bench["duration_days"],
        "season_name": "Optimal Season",
        "profit_tip": f"Follow direct Mandi sale and balanced NPK fertilizer protocol to achieve peak returns of ₹{net_profit:,}."
    }

def get_seasonal_crops_data():
    return SEASON_DATA
