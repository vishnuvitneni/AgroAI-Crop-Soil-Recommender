"""
Crop Recommendation, Agronomic Fertilizer Dosage & Economic Advisory Engine for AgroAI
Implements:
1. Gaussian Naive Bayes ML prediction with probability distributions
2. Precision Agronomic Fertilizer Dosage & Bag Calculator (Urea, DAP, MOP, Lime/Gypsum)
3. Crop Commercial Economics & Yield Return Projection (Revenue, Costs, Net Profit, ROI)
4. Side-by-Side Crop Comparison & Suitability Matrix
5. Soil Health Diagnostics & Soil Conditioning Advisory
"""
import os
import json
import math

# Resolve base project directory dynamically
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == "src":
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
else:
    BASE_DIR = CURRENT_DIR

DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_model.json")

# Detailed Crop Information Dictionary
CROP_DETAILS = {
    "rice": {
        "title": "Rice (Oryza sativa)",
        "category": "Cereal / Staple Grain",
        "icon": "🌾",
        "water_req": "High (Standing water required during vegetative phase)",
        "soil_type": "Clayey or heavy alluvial soil with high water retention",
        "fertilizer_tip": "Apply Nitrogen (Urea) in 3 split doses: basal, tillering, and panicle initiation. Ensure adequate Zinc.",
        "growing_season": "Kharif (Monsoon / Summer)",
        "description": "Thrives in warm, humid climates with heavy rainfall or abundant flood irrigation."
    },
    "maize": {
        "title": "Maize / Corn (Zea mays)",
        "category": "Cereal / Grain",
        "icon": "🌽",
        "water_req": "Moderate (Sensitive to both waterlogging and severe drought)",
        "soil_type": "Well-drained fertile loamy or alluvial soil",
        "fertilizer_tip": "Balanced N-P-K (120:60:40 kg/ha). Zinc application significantly boosts cob weight.",
        "growing_season": "Kharif and Rabi",
        "description": "Highly versatile crop with high biomass and nutrient uptake. Ensure good drainage."
    },
    "chickpea": {
        "title": "Chickpea / Bengal Gram (Cicer arietinum)",
        "category": "Pulse / Legume",
        "icon": "🌱",
        "water_req": "Low (Drought-tolerant, sensitive to excess moisture)",
        "soil_type": "Deep well-drained sandy loam to clay loam",
        "fertilizer_tip": "As a legume, it fixes nitrogen. Apply Starter N (20 kg/ha) and high Phosphorus (DAP) for strong root nodules.",
        "growing_season": "Rabi (Winter)",
        "description": "Excellent winter pulse that enriches soil nitrogen naturally."
    },
    "kidneybeans": {
        "title": "Kidney Beans / Rajma (Phaseolus vulgaris)",
        "category": "Pulse / Legume",
        "icon": "🫘",
        "water_req": "Moderate (Regular light watering, cannot tolerate waterlogging)",
        "soil_type": "Light, friable, well-aerated rich loamy soil",
        "fertilizer_tip": "Poor nodulator compared to other pulses; requires higher external Nitrogen (80-100 kg/ha) along with Phosphorus.",
        "growing_season": "Spring / Rabi (Cool climate)",
        "description": "High-value legume requiring cool temperatures and rich organic matter."
    },
    "pigeonpeas": {
        "title": "Pigeon Peas / Tur / Arhar (Cajanus cajan)",
        "category": "Pulse / Legume",
        "icon": "🌿",
        "water_req": "Low to Moderate (Deep taproot allows high drought tolerance)",
        "soil_type": "Deep loamy or black cotton soil",
        "fertilizer_tip": "Apply Phosphorus (DAP/SSP) at sowing. Inoculate with Rhizobium culture.",
        "growing_season": "Kharif",
        "description": "Deep-rooted long-duration pulse that breaks soil subsoil compaction."
    },
    "mothbeans": {
        "title": "Moth Beans (Vigna aconitifolia)",
        "category": "Arid Pulse",
        "icon": "🍃",
        "water_req": "Very Low (Exceptional drought resilience)",
        "soil_type": "Sandy, light, well-drained soil",
        "fertilizer_tip": "Low fertilizer requirement. Minimal Starter N and single dose Phosphorus.",
        "growing_season": "Kharif (Arid / Semi-Arid)",
        "description": "Ideal for arid and desert-adjacent dryland farming."
    },
    "mungbean": {
        "title": "Mung Bean / Green Gram (Vigna radiata)",
        "category": "Short-Duration Pulse",
        "icon": "🌱",
        "water_req": "Low to Moderate",
        "soil_type": "Well-drained fertile loam",
        "fertilizer_tip": "Starter N with DAP (Phosphorus) and Sulfur for high protein grain formation.",
        "growing_season": "Zaid / Summer or Kharif (60-70 days maturity)",
        "description": "Fast-growing catch crop perfect for short cropping windows and green manuring."
    },
    "blackgram": {
        "title": "Black Gram / Urad (Vigna mungo)",
        "category": "Pulse / Legume",
        "icon": "🫘",
        "water_req": "Low to Moderate",
        "soil_type": "Loamy to heavy clay loam",
        "fertilizer_tip": "Foliar spray of 2% DAP at flower initiation enhances pod setting.",
        "growing_season": "Kharif / Summer",
        "description": "Rich in protein and phosphoric acid, widely cultivated in crop rotation."
    },
    "lentil": {
        "title": "Lentil / Masoor (Lens culinaris)",
        "category": "Rabi Pulse",
        "icon": "🥣",
        "water_req": "Low (Sensitive to waterlogging)",
        "soil_type": "Sandy loam to light clay with neutral pH",
        "fertilizer_tip": "Apply 20 kg N + 40 kg P2O5 per hectare at sowing.",
        "growing_season": "Rabi (Winter)",
        "description": "Cold-hardy pulse requiring dry, crisp weather during maturity."
    },
    "pomegranate": {
        "title": "Pomegranate (Punica granatum)",
        "category": "Fruit / Horticultural Crop",
        "icon": "🍎",
        "water_req": "Moderate (Drip irrigation recommended; sensitive to excess humidity during ripening)",
        "soil_type": "Well-drained deep loamy to slightly alkaline soil",
        "fertilizer_tip": "High Potassium during fruit development enhances aril color and sweetness.",
        "growing_season": "Perennial orchard (Ambe, Mrig, or Hasta bahar)",
        "description": "High-value commercial fruit that thrives in semi-arid and warm climates."
    },
    "banana": {
        "title": "Banana (Musa acuminata)",
        "category": "Fruit / Commercial Plantation",
        "icon": "🍌",
        "water_req": "Very High (Needs frequent irrigation, 1800-2000 mm annual equivalent)",
        "soil_type": "Deep, rich fertile loamy soil with high organic matter",
        "fertilizer_tip": "Heavy feeder of Potassium and Nitrogen. Apply fertilizers in 4-5 split doses monthly.",
        "growing_season": "11-12 months perennial cycle",
        "description": "Rapidly growing tropical fruit requiring warm humid weather and abundant nutrients."
    },
    "mango": {
        "title": "Mango (Mangifera indica)",
        "category": "Fruit / Perennial Orchard",
        "icon": "🥭",
        "water_req": "Moderate (Needs dry spell before flowering to induce flower buds)",
        "soil_type": "Deep alluvial, loamy or red soil with minimum 2m root depth",
        "fertilizer_tip": "Apply Farm Yard Manure (FYM) with SSP and MOP post-harvest in monsoon.",
        "growing_season": "Perennial summer harvest",
        "description": "The 'King of Fruits', performing well across tropical and subtropical plains."
    },
    "grapes": {
        "title": "Grapes (Vitis vinifera)",
        "category": "Vineyard / Cash Fruit",
        "icon": "🍇",
        "water_req": "Moderate (Controlled drip irrigation; avoid rain during berry ripening)",
        "soil_type": "Well-drained gravelly loam or sandy loam with good aeration",
        "fertilizer_tip": "Balanced N during canopy development; high Potassium and Calcium during veraison for berry crispness.",
        "growing_season": "Perennial vine (Pruned for summer harvest)",
        "description": "High-capital precision fruit grown on trellis systems in semi-arid zones."
    },
    "watermelon": {
        "title": "Watermelon (Citrullus lanatus)",
        "category": "Cucurbit / Summer Cash Crop",
        "icon": "🍉",
        "water_req": "Moderate (Regular irrigation during vine growth; reduce watering near harvest to boost sugar)",
        "soil_type": "Sandy loam, riverbed alluvium with excellent drainage",
        "fertilizer_tip": "Apply balanced NPK at vine spreading; increase Potassium during fruit bulking.",
        "growing_season": "Zaid / Summer (80-95 days duration)",
        "description": "Warm-season high-sugar fruit ideal for riverbeds and well-drained sandy fields."
    },
    "muskmelon": {
        "title": "Muskmelon / Cantaloupe (Cucumis melo)",
        "category": "Cucurbit / Summer Cash Crop",
        "icon": "🍈",
        "water_req": "Low to Moderate",
        "soil_type": "Light sandy loam with neutral to slightly alkaline pH",
        "fertilizer_tip": "Foliar micronutrient spray (Boron & Calcium) prevents fruit cracking.",
        "growing_season": "Zaid / Spring-Summer",
        "description": "Thrives in hot, dry climates with bright sunshine for high brix sweetness."
    },
    "apple": {
        "title": "Apple (Malus domestica)",
        "category": "Temperate Fruit / Orchard",
        "icon": "🍏",
        "water_req": "Moderate to High (1000-1250 mm distributed rainfall)",
        "soil_type": "Deep, fertile, well-drained loamy soil rich in organic matter",
        "fertilizer_tip": "Requires high Potassium for fruit sizing and Calcium to prevent bitter pit disorder.",
        "growing_season": "High-altitude temperate perennial (Winter chilling required)",
        "description": "Premier temperate commercial tree requiring 800-1200 chilling hours below 7°C."
    },
    "orange": {
        "title": "Orange / Citrus (Citrus sinensis)",
        "category": "Citrus / Horticultural Orchard",
        "icon": "🍊",
        "water_req": "Moderate (Regular watering; sensitive to standing water and waterlogging)",
        "soil_type": "Well-drained light loamy soil without hard subsoil pan",
        "fertilizer_tip": "Apply Zinc, Iron, and Manganese foliar sprays alongside standard N-K dressing.",
        "growing_season": "Subtropical / Tropical perennial",
        "description": "Major citrus fruit producing delicious, vitamin C-rich juice."
    },
    "papaya": {
        "title": "Papaya (Carica papaya)",
        "category": "Tropical Fruit / Quick Cash",
        "icon": "🥭",
        "water_req": "Moderate (Regular light watering; strictly intolerant to root rot from waterlogging)",
        "soil_type": "Porous, rich loam with quick surface and subsoil drainage",
        "fertilizer_tip": "Frequent monthly application of balanced NPK + Boron for continuous fruit setting.",
        "growing_season": "Year-round in warm tropical climate (Starts harvest in 9-10 months)",
        "description": "Fast-yielding commercial crop producing high tonnage per acre."
    },
    "coconut": {
        "title": "Coconut (Cocos nucifera)",
        "category": "Plantation / Palm",
        "icon": "🥥",
        "water_req": "High (Even distribution of rainfall or coastal water table)",
        "soil_type": "Coastal sand, alluvial, or red sandy loam",
        "fertilizer_tip": "Very high Potassium and Chlorine requirement. Common salt (NaCl) and MOP promote vigorous frond growth.",
        "growing_season": "Perennial coastal palm",
        "description": "The 'Tree of Life' flourishing in warm, humid coastal and tropical plains."
    },
    "cotton": {
        "title": "Cotton (Gossypium hirsutum)",
        "category": "Fiber / Cash Crop",
        "icon": "☁️",
        "water_req": "Moderate (Needs 500-750 mm rainfall or timely canal irrigation)",
        "soil_type": "Deep black cotton soils (Vertisols) or alluvial loam",
        "fertilizer_tip": "Apply Nitrogen in splits; Potassium prevents premature leaf reddening (leaf blight).",
        "growing_season": "Kharif (Warm season, minimum 180-200 frost-free days)",
        "description": "Major commercial cash crop requiring warm days and sunny weather during boll opening."
    },
    "jute": {
        "title": "Jute / Golden Fiber (Corchorus)",
        "category": "Bast Fiber",
        "icon": "🌾",
        "water_req": "High (Abundant monsoon rainfall and standing water for retting)",
        "soil_type": "New alluvial silt deposits near floodplains",
        "fertilizer_tip": "Nitrogen is key for vegetative fiber elongation; top dress Urea after initial weeding.",
        "growing_season": "Kharif / Pre-monsoon sowing",
        "description": "Eco-friendly natural golden fiber crop thriving in warm, humid river deltas."
    },
    "coffee": {
        "title": "Coffee (Coffea arabica / canephora)",
        "category": "Beverage / Plantation",
        "icon": "☕",
        "water_req": "High (Well-distributed rainfall with 2-3 months dry spell for blossom)",
        "soil_type": "Deep, porous, slightly acidic volcanic or forest loam rich in organic matter",
        "fertilizer_tip": "Regular application of compost, rock phosphate, and split N-K doses under shade trees.",
        "growing_season": "Perennial shade-grown plantation (Hill slopes)",
        "description": "Shade-loving hill crop grown at 800-1800m altitude with cool, moist climate."
    }
}

# Agronomic Reference Data & Economics for all 22 Crops
# RDF: Recommended Dose of Fertilizers (kg/ha) for Nitrogen (N), Phosphorus (P2O5), Potassium (K2O)
AGRONOMIC_PROFILES = {
    "rice": {
        "rdf_n": 120, "rdf_p": 60, "rdf_k": 40,
        "duration_days": 120,
        "yield_qtl_per_acre": 24.0, # 2.4 tonnes/acre
        "market_price_inr": 2300,  # MSP / benchmark per quintal
        "cultivation_cost_inr": 22000, # seed, labor, irrigation per acre
        "water_demand_mm": 1200,
        "optimal_ph": [5.5, 7.0],
        "risk_level": "Low"
    },
    "maize": {
        "rdf_n": 120, "rdf_p": 60, "rdf_k": 50,
        "duration_days": 105,
        "yield_qtl_per_acre": 28.0,
        "market_price_inr": 2225,
        "cultivation_cost_inr": 18000,
        "water_demand_mm": 600,
        "optimal_ph": [5.8, 7.2],
        "risk_level": "Low"
    },
    "chickpea": {
        "rdf_n": 25, "rdf_p": 50, "rdf_k": 25,
        "duration_days": 100,
        "yield_qtl_per_acre": 9.0,
        "market_price_inr": 5440,
        "cultivation_cost_inr": 14000,
        "water_demand_mm": 350,
        "optimal_ph": [6.0, 7.5],
        "risk_level": "Low"
    },
    "kidneybeans": {
        "rdf_n": 90, "rdf_p": 60, "rdf_k": 40,
        "duration_days": 115,
        "yield_qtl_per_acre": 8.0,
        "market_price_inr": 8500,
        "cultivation_cost_inr": 19000,
        "water_demand_mm": 500,
        "optimal_ph": [5.5, 6.8],
        "risk_level": "Moderate"
    },
    "pigeonpeas": {
        "rdf_n": 25, "rdf_p": 50, "rdf_k": 25,
        "duration_days": 160,
        "yield_qtl_per_acre": 8.5,
        "market_price_inr": 7000,
        "cultivation_cost_inr": 15000,
        "water_demand_mm": 650,
        "optimal_ph": [6.5, 7.8],
        "risk_level": "Low"
    },
    "mothbeans": {
        "rdf_n": 20, "rdf_p": 40, "rdf_k": 20,
        "duration_days": 75,
        "yield_qtl_per_acre": 4.5,
        "market_price_inr": 6500,
        "cultivation_cost_inr": 9000,
        "water_demand_mm": 250,
        "optimal_ph": [6.5, 8.2],
        "risk_level": "Low"
    },
    "mungbean": {
        "rdf_n": 20, "rdf_p": 40, "rdf_k": 20,
        "duration_days": 65,
        "yield_qtl_per_acre": 5.5,
        "market_price_inr": 8558,
        "cultivation_cost_inr": 11000,
        "water_demand_mm": 300,
        "optimal_ph": [6.2, 7.2],
        "risk_level": "Low"
    },
    "blackgram": {
        "rdf_n": 20, "rdf_p": 40, "rdf_k": 20,
        "duration_days": 75,
        "yield_qtl_per_acre": 6.0,
        "market_price_inr": 6950,
        "cultivation_cost_inr": 12000,
        "water_demand_mm": 350,
        "optimal_ph": [6.0, 7.5],
        "risk_level": "Low"
    },
    "lentil": {
        "rdf_n": 20, "rdf_p": 40, "rdf_k": 20,
        "duration_days": 110,
        "yield_qtl_per_acre": 6.5,
        "market_price_inr": 6425,
        "cultivation_cost_inr": 12500,
        "water_demand_mm": 350,
        "optimal_ph": [6.0, 7.5],
        "risk_level": "Low"
    },
    "pomegranate": {
        "rdf_n": 250, "rdf_p": 125, "rdf_k": 250,
        "duration_days": 180,
        "yield_qtl_per_acre": 45.0, # 4.5 tonnes/acre
        "market_price_inr": 7500,
        "cultivation_cost_inr": 70000,
        "water_demand_mm": 800,
        "optimal_ph": [6.5, 7.8],
        "risk_level": "Moderate"
    },
    "banana": {
        "rdf_n": 200, "rdf_p": 60, "rdf_k": 300,
        "duration_days": 330,
        "yield_qtl_per_acre": 250.0, # 25 tonnes/acre
        "market_price_inr": 1600,
        "cultivation_cost_inr": 85000,
        "water_demand_mm": 1800,
        "optimal_ph": [6.0, 7.5],
        "risk_level": "Moderate"
    },
    "mango": {
        "rdf_n": 150, "rdf_p": 80, "rdf_k": 150,
        "duration_days": 120,
        "yield_qtl_per_acre": 50.0,
        "market_price_inr": 3500,
        "cultivation_cost_inr": 45000,
        "water_demand_mm": 900,
        "optimal_ph": [5.5, 7.5],
        "risk_level": "Low"
    },
    "grapes": {
        "rdf_n": 160, "rdf_p": 100, "rdf_k": 240,
        "duration_days": 150,
        "yield_qtl_per_acre": 90.0,
        "market_price_inr": 4500,
        "cultivation_cost_inr": 95000,
        "water_demand_mm": 700,
        "optimal_ph": [6.5, 7.5],
        "risk_level": "High"
    },
    "watermelon": {
        "rdf_n": 100, "rdf_p": 50, "rdf_k": 60,
        "duration_days": 85,
        "yield_qtl_per_acre": 120.0,
        "market_price_inr": 900,
        "cultivation_cost_inr": 30000,
        "water_demand_mm": 500,
        "optimal_ph": [6.0, 7.0],
        "risk_level": "Moderate"
    },
    "muskmelon": {
        "rdf_n": 80, "rdf_p": 50, "rdf_k": 50,
        "duration_days": 80,
        "yield_qtl_per_acre": 85.0,
        "market_price_inr": 1200,
        "cultivation_cost_inr": 28000,
        "water_demand_mm": 450,
        "optimal_ph": [6.0, 7.2],
        "risk_level": "Moderate"
    },
    "apple": {
        "rdf_n": 120, "rdf_p": 60, "rdf_k": 140,
        "duration_days": 140,
        "yield_qtl_per_acre": 60.0,
        "market_price_inr": 6000,
        "cultivation_cost_inr": 75000,
        "water_demand_mm": 1000,
        "optimal_ph": [5.8, 6.8],
        "risk_level": "Moderate"
    },
    "orange": {
        "rdf_n": 140, "rdf_p": 70, "rdf_k": 140,
        "duration_days": 180,
        "yield_qtl_per_acre": 55.0,
        "market_price_inr": 3800,
        "cultivation_cost_inr": 50000,
        "water_demand_mm": 900,
        "optimal_ph": [6.0, 7.5],
        "risk_level": "Moderate"
    },
    "papaya": {
        "rdf_n": 200, "rdf_p": 200, "rdf_k": 250,
        "duration_days": 270,
        "yield_qtl_per_acre": 220.0,
        "market_price_inr": 1100,
        "cultivation_cost_inr": 65000,
        "water_demand_mm": 1300,
        "optimal_ph": [6.0, 7.0],
        "risk_level": "Moderate"
    },
    "coconut": {
        "rdf_n": 140, "rdf_p": 70, "rdf_k": 240,
        "duration_days": 365,
        "yield_qtl_per_acre": 5000, # nuts per acre
        "market_price_inr": 25,   # per nut
        "cultivation_cost_inr": 40000,
        "water_demand_mm": 1500,
        "optimal_ph": [5.5, 7.5],
        "risk_level": "Low"
    },
    "cotton": {
        "rdf_n": 120, "rdf_p": 60, "rdf_k": 60,
        "duration_days": 170,
        "yield_qtl_per_acre": 11.0,
        "market_price_inr": 7122,
        "cultivation_cost_inr": 26000,
        "water_demand_mm": 700,
        "optimal_ph": [6.5, 8.0],
        "risk_level": "Moderate"
    },
    "jute": {
        "rdf_n": 80, "rdf_p": 40, "rdf_k": 40,
        "duration_days": 120,
        "yield_qtl_per_acre": 12.0,
        "market_price_inr": 5050,
        "cultivation_cost_inr": 20000,
        "water_demand_mm": 1200,
        "optimal_ph": [6.0, 7.2],
        "risk_level": "Low"
    },
    "coffee": {
        "rdf_n": 140, "rdf_p": 90, "rdf_k": 140,
        "duration_days": 240,
        "yield_qtl_per_acre": 8.0,
        "market_price_inr": 18000, # Clean coffee
        "cultivation_cost_inr": 55000,
        "water_demand_mm": 1400,
        "optimal_ph": [5.5, 6.5],
        "risk_level": "Moderate"
    }
}

class CropAdvisoryEngine:
    def __init__(self, model_file=None):
        self.model_file = model_file or DEFAULT_MODEL_PATH
        self.meta = None
        self.load()
        
    def load(self):
        if not os.path.exists(self.model_file):
            try:
                try:
                    from src.train import main as train_model
                except ImportError:
                    from train import main as train_model
                train_model()
            except Exception as e:
                raise FileNotFoundError(f"Model file {self.model_file} not found and auto-training failed: {e}")

        with open(self.model_file, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
            
    def get_crop_catalog(self):
        """Return list of all supported crops with metadata for search"""
        profiles = self.meta.get("crop_profiles", {})
        catalog = []
        for crop_id, details in CROP_DETAILS.items():
            ideal = profiles.get(crop_id, {})
            agro = AGRONOMIC_PROFILES.get(crop_id, {})
            catalog.append({
                "id": crop_id,
                "title": details.get("title", crop_id.title()),
                "category": details.get("category", "Crop"),
                "icon": details.get("icon", "🌱"),
                "description": details.get("description", ""),
                "water_req": details.get("water_req", ""),
                "soil_type": details.get("soil_type", ""),
                "fertilizer_tip": details.get("fertilizer_tip", ""),
                "growing_season": details.get("growing_season", ""),
                "ideal_profile": ideal,
                "duration_days": agro.get("duration_days", 120),
                "yield_per_acre": agro.get("yield_qtl_per_acre", 15.0),
                "risk_level": agro.get("risk_level", "Moderate")
            })
        return catalog

    def analyze_crop_compatibility(self, crop_name, n, p, k, temperature, humidity, ph, rainfall):
        """Analyze how well user's current soil & climate match a specific searched crop"""
        crop_id = crop_name.lower().strip()
        profiles = self.meta.get("crop_profiles", {})
        if crop_id not in profiles:
            return None
            
        ideal = profiles[crop_id]
        details = CROP_DETAILS.get(crop_id, {})
        agro = AGRONOMIC_PROFILES.get(crop_id, {})
        
        user_vals = {
            "N": n, "P": p, "K": k,
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall
        }
        
        weights = {
            "rainfall": 0.22,
            "humidity": 0.18,
            "temperature": 0.18,
            "ph": 0.14,
            "N": 0.10,
            "P": 0.09,
            "K": 0.09
        }
        
        feature_ranges = {
            "N": 140.0, "P": 140.0, "K": 200.0,
            "temperature": 35.0, "humidity": 90.0, "ph": 6.5, "rainfall": 280.0
        }
        
        gaps = []
        penalty = 0.0
        for feat, w in weights.items():
            u_val = user_vals[feat]
            i_val = ideal[feat]
            diff = u_val - i_val
            rng = feature_ranges[feat]
            
            norm_diff = abs(diff) / rng
            penalty += w * min(1.0, norm_diff * 1.5)
            
            pct_diff = (diff / i_val * 100) if i_val else 0
            if abs(pct_diff) > 25:
                direction = "lower than ideal" if diff < 0 else "higher than ideal"
                gaps.append({
                    "feature": feat,
                    "user_value": u_val,
                    "ideal_value": i_val,
                    "direction": direction,
                    "message": f"{feat} is {abs(round(diff, 1))} units {direction} (Target: {i_val})"
                })
                
        compatibility_score = round(max(5.0, min(100.0, (1.0 - penalty) * 100)), 1)
        
        return {
            "crop": crop_id,
            "details": details,
            "ideal_profile": ideal,
            "agronomic": agro,
            "compatibility_score": compatibility_score,
            "gaps": gaps,
            "user_values": user_vals
        }

    def analyze_soil_health(self, n, p, k, ph):
        """Diagnose soil nutrient levels and pH status with actionable agronomic tips"""
        health = {}
        
        # Nitrogen (N)
        if n < 40:
            health["N"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Nitrogen limits vegetative tillering and leaf growth. Supplement with Urea or well-decomposed FYM compost."}
        elif n <= 90:
            health["N"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Nitrogen level is in a balanced, productive agronomic range."}
        else:
            health["N"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "Excess Nitrogen promotes overly lush vegetative growth and pest vulnerability. Reduce synthetic urea application."}
            
        # Phosphorus (P)
        if p < 35:
            health["P"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Phosphorus restricts root establishment and seedling vigor. Apply DAP or Single Superphosphate (SSP)."}
        elif p <= 75:
            health["P"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Phosphorus level is ideal for vigorous root nodulation and early floral development."}
        else:
            health["P"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "High soil Phosphorus. Skip heavy phosphate applications to prevent zinc and iron lockup."}

        # Potassium (K)
        if k < 30:
            health["K"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Potassium lowers drought resilience and disease defense. Incorporate Muriate of Potash (MOP)."}
        elif k <= 65:
            health["K"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Potassium level supports robust stem strength, osmotic regulation, and grain/fruit filling."}
        else:
            health["K"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "High Potassium reserves. Very favorable for high-potassium consumers like banana, sugarcane, and potato."}

        # pH Level
        if ph < 5.5:
            health["pH"] = {"status": "Strongly Acidic", "badge": "Acidic", "color": "#ef4444", "tip": "Strong acidity causes aluminum toxicity and locks Phosphorus. Apply agricultural lime (CaCO3) to neutralize."}
        elif ph < 6.5:
            health["pH"] = {"status": "Slightly Acidic", "badge": "Optimal", "color": "#10b981", "tip": "Slightly acidic soil; peak nutrient bioavailability for most cereals, pulses, and cash crops."}
        elif ph <= 7.5:
            health["pH"] = {"status": "Neutral / Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Neutral pH offers peak bioavailability for all primary and secondary plant nutrients."}
        elif ph <= 8.5:
            health["pH"] = {"status": "Slightly Alkaline", "badge": "Alkaline", "color": "#f59e0b", "tip": "Slightly alkaline. Apply agricultural gypsum (CaSO4) and organic farmyard manure to buffer pH."}
        else:
            health["pH"] = {"status": "Strongly Alkaline", "badge": "Alkaline", "color": "#ef4444", "tip": "High alkalinity locks micronutrients (Zinc, Iron). Apply Gypsum and green manuring (Dhaincha/Sesbania)."}

        return health

    def calculate_fertilizer_dosage(self, crop_name, n_soil, p_soil, k_soil, ph_soil, field_size_acres=1.0):
        """
        Calculates exact commercial fertilizer quantities (Urea, DAP, MOP, Lime/Gypsum)
        based on Recommended Dose of Fertilizer (RDF) adjusted for soil nutrient test ratings.
        """
        crop_id = crop_name.lower().strip()
        agro = AGRONOMIC_PROFILES.get(crop_id, AGRONOMIC_PROFILES["rice"])
        field_size = max(0.1, float(field_size_acres))
        
        # 1 Hectare = 2.471 Acres
        ACRES_PER_HA = 2.47105
        
        # Base RDF per acre (kg/acre)
        base_n_acre = agro["rdf_n"] / ACRES_PER_HA
        base_p_acre = agro["rdf_p"] / ACRES_PER_HA
        base_k_acre = agro["rdf_k"] / ACRES_PER_HA
        
        # Soil test rating adjustment factor:
        # Low soil test: +25% fertilizer; High soil test: -25% fertilizer
        adj_n = 1.25 if n_soil < 40 else (0.75 if n_soil > 90 else 1.0)
        adj_p = 1.25 if p_soil < 35 else (0.75 if p_soil > 75 else 1.0)
        adj_k = 1.25 if k_soil < 30 else (0.75 if k_soil > 65 else 1.0)
        
        target_n_acre = base_n_acre * adj_n
        target_p_acre = base_p_acre * adj_p
        target_k_acre = base_k_acre * adj_k
        
        # Total nutrient required for full field
        total_n_req = target_n_acre * field_size
        total_p_req = target_p_acre * field_size
        total_k_req = target_k_acre * field_size
        
        # Commercial Fertilizers formulation:
        # 1. DAP (18% N, 46% P2O5) supplies all P requirement
        dap_kg = total_p_req / 0.46
        dap_bags = math.ceil(dap_kg / 50.0) # 50 kg per bag
        n_from_dap = dap_kg * 0.18
        
        # 2. Urea (46% N) supplies remaining N requirement
        remaining_n = max(0.0, total_n_req - n_from_dap)
        urea_kg = remaining_n / 0.46
        urea_bags = math.ceil(urea_kg / 45.0) # 45 kg per standard bag
        
        # 3. MOP (60% K2O) supplies K requirement
        mop_kg = total_k_req / 0.60
        mop_bags = math.ceil(mop_kg / 50.0) # 50 kg per bag
        
        # 4. Soil pH Conditioner:
        # Lime if pH < 6.0; Gypsum if pH > 7.5
        conditioner_name = "None (Optimal pH)"
        conditioner_kg = 0.0
        conditioner_bags = 0
        conditioner_tip = "Soil pH is within ideal range; no chemical buffering needed."
        
        if ph_soil < 6.0:
            conditioner_name = "Agricultural Lime (CaCO3)"
            conditioner_kg = round((6.5 - ph_soil) * 350.0 * field_size, 1)
            conditioner_bags = math.ceil(conditioner_kg / 50.0)
            conditioner_tip = f"Soil is acidic ({ph_soil}). Apply agricultural lime to raise soil pH toward neutral and unlock Phosphorus."
        elif ph_soil > 7.5:
            conditioner_name = "Agricultural Gypsum (CaSO4)"
            conditioner_kg = round((ph_soil - 7.5) * 450.0 * field_size, 1)
            conditioner_bags = math.ceil(conditioner_kg / 50.0)
            conditioner_tip = f"Soil is alkaline ({ph_soil}). Apply gypsum to replace excess sodium ions and buffer pH down."
            
        # 5. Organic Manure (FYM)
        fym_tonnes = round(2.0 * field_size, 1) # 2 tonnes per acre
        
        # 6. Costs Estimation (Market Averages in INR, convert to USD @ 1 USD = 83 INR)
        INR_TO_USD = 1.0 / 83.0
        urea_price_bag = 266.0   # Govt subsidized 45kg bag
        dap_price_bag = 1350.0   # 50kg bag
        mop_price_bag = 1700.0   # 50kg bag
        cond_price_per_kg = 8.0  # Lime/Gypsum per kg
        
        cost_urea_inr = urea_bags * urea_price_bag
        cost_dap_inr = dap_bags * dap_price_bag
        cost_mop_inr = mop_bags * mop_price_bag
        cost_cond_inr = conditioner_kg * cond_price_per_kg
        total_fert_cost_inr = cost_urea_inr + cost_dap_inr + cost_mop_inr + cost_cond_inr
        
        # 7. Split Application Schedule
        schedule = [
            {
                "stage": "1. Basal Application (At Sowing / Transplanting)",
                "timing": "Day 0 - Incorporate into soil during final ploughing",
                "urea_pct": 25,
                "dap_pct": 100,
                "mop_pct": 50,
                "instructions": f"Apply {round(dap_kg, 1)} kg DAP (100%), {round(mop_kg * 0.5, 1)} kg MOP (50%), and {round(urea_kg * 0.25, 1)} kg Urea (25%) alongside {fym_tonnes} tonnes FYM."
            },
            {
                "stage": "2. Vegetative Phase (Tillering / Early Growth)",
                "timing": "20–30 days after sowing / transplanting",
                "urea_pct": 45,
                "dap_pct": 0,
                "mop_pct": 0,
                "instructions": f"Top dress {round(urea_kg * 0.45, 1)} kg Urea when soil has adequate moisture. Weeding should precede application."
            },
            {
                "stage": "3. Reproductive Phase (Panicle / Flowering Initiation)",
                "timing": "50–65 days after sowing / pre-flowering",
                "urea_pct": 30,
                "dap_pct": 0,
                "mop_pct": 50,
                "instructions": f"Top dress {round(urea_kg * 0.30, 1)} kg Urea and remaining {round(mop_kg * 0.5, 1)} kg MOP to boost seed setting and fruit bulking."
            }
        ]
        
        return {
            "crop": crop_id,
            "field_size_acres": field_size,
            "nutrient_requirements_kg": {
                "N": round(total_n_req, 1),
                "P": round(total_p_req, 1),
                "K": round(total_k_req, 1)
            },
            "commercial_fertilizers": {
                "urea": {"kg": round(urea_kg, 1), "bags": urea_bags, "bag_size": "45 kg", "cost_inr": cost_urea_inr},
                "dap": {"kg": round(dap_kg, 1), "bags": dap_bags, "bag_size": "50 kg", "cost_inr": cost_dap_inr},
                "mop": {"kg": round(mop_kg, 1), "bags": mop_bags, "bag_size": "50 kg", "cost_inr": cost_mop_inr},
                "organic_manure": {"tonnes": fym_tonnes, "desc": "Well-cured Farmyard Manure (FYM)"},
                "soil_conditioner": {
                    "name": conditioner_name,
                    "kg": conditioner_kg,
                    "bags": conditioner_bags,
                    "cost_inr": cost_cond_inr,
                    "tip": conditioner_tip
                }
            },
            "schedule": schedule,
            "costs": {
                "total_inr": round(total_fert_cost_inr, 2),
                "total_usd": round(total_fert_cost_inr * INR_TO_USD, 2),
                "per_acre_inr": round(total_fert_cost_inr / field_size, 2),
                "per_acre_usd": round((total_fert_cost_inr / field_size) * INR_TO_USD, 2)
            }
        }

    def calculate_crop_economics(self, crop_name, field_size_acres=1.0, fertilizer_cost_inr=0.0):
        """Calculates projected yield, gross revenue, cultivation costs, net profit and ROI"""
        crop_id = crop_name.lower().strip()
        agro = AGRONOMIC_PROFILES.get(crop_id, AGRONOMIC_PROFILES["rice"])
        field_size = max(0.1, float(field_size_acres))
        
        INR_TO_USD = 1.0 / 83.0
        
        is_coconut = (crop_id == "coconut")
        yield_per_acre = agro["yield_qtl_per_acre"]
        total_yield = round(yield_per_acre * field_size, 1)
        
        market_price = agro["market_price_inr"]
        gross_revenue_inr = round(total_yield * market_price, 2)
        
        cultivation_cost_acre = agro["cultivation_cost_inr"]
        base_operational_cost_inr = round(cultivation_cost_acre * field_size, 2)
        total_cost_inr = round(base_operational_cost_inr + fertilizer_cost_inr, 2)
        
        net_profit_inr = round(gross_revenue_inr - total_cost_inr, 2)
        roi_pct = round((net_profit_inr / total_cost_inr * 100), 1) if total_cost_inr > 0 else 0.0
        
        return {
            "crop": crop_id,
            "field_size_acres": field_size,
            "duration_days": agro["duration_days"],
            "risk_level": agro["risk_level"],
            "water_demand_mm": agro["water_demand_mm"],
            "yield": {
                "total": total_yield,
                "per_acre": yield_per_acre,
                "unit": "Nuts" if is_coconut else "Quintals (100 kg)",
                "metric_tonnes": round(total_yield * 0.1, 2) if not is_coconut else None
            },
            "market_price": {
                "inr": market_price,
                "usd": round(market_price * INR_TO_USD, 2),
                "unit": "per nut" if is_coconut else "per quintal"
            },
            "gross_revenue": {
                "inr": gross_revenue_inr,
                "usd": round(gross_revenue_inr * INR_TO_USD, 2)
            },
            "total_costs": {
                "inr": total_cost_inr,
                "usd": round(total_cost_inr * INR_TO_USD, 2),
                "operational_inr": base_operational_cost_inr,
                "fertilizer_inr": fertilizer_cost_inr
            },
            "net_profit": {
                "inr": net_profit_inr,
                "usd": round(net_profit_inr * INR_TO_USD, 2)
            },
            "roi_percent": roi_pct
        }

    def compare_crops(self, crop1_name, crop2_name, n, p, k, temp, hum, ph, rain, field_size_acres=1.0):
        """Generates a detailed side-by-side comparison between two crops for decision support"""
        c1_id = crop1_name.lower().strip()
        c2_id = crop2_name.lower().strip()
        
        fit1 = self.analyze_crop_compatibility(c1_id, n, p, k, temp, hum, ph, rain)
        fit2 = self.analyze_crop_compatibility(c2_id, n, p, k, temp, hum, ph, rain)
        
        if not fit1 or not fit2:
            return None
            
        fert1 = self.calculate_fertilizer_dosage(c1_id, n, p, k, ph, field_size_acres)
        fert2 = self.calculate_fertilizer_dosage(c2_id, n, p, k, ph, field_size_acres)
        
        econ1 = self.calculate_crop_economics(c1_id, field_size_acres, fert1["costs"]["total_inr"])
        econ2 = self.calculate_crop_economics(c2_id, field_size_acres, fert2["costs"]["total_inr"])
        
        # Winner recommendations:
        # Agronomic Fit Winner
        agro_winner = c1_id if fit1["compatibility_score"] >= fit2["compatibility_score"] else c2_id
        # Profit Winner
        profit_winner = c1_id if econ1["net_profit"]["inr"] >= econ2["net_profit"]["inr"] else c2_id
        
        return {
            "crop1": {
                "id": c1_id,
                "details": fit1["details"],
                "fit_score": fit1["compatibility_score"],
                "gaps": fit1["gaps"],
                "fertilizer": fert1,
                "economics": econ1
            },
            "crop2": {
                "id": c2_id,
                "details": fit2["details"],
                "fit_score": fit2["compatibility_score"],
                "gaps": fit2["gaps"],
                "fertilizer": fert2,
                "economics": econ2
            },
            "summary": {
                "best_agronomic_fit": agro_winner,
                "highest_profit_potential": profit_winner,
                "profit_difference_inr": abs(round(econ1["net_profit"]["inr"] - econ2["net_profit"]["inr"], 2)),
                "profit_difference_usd": abs(round(econ1["net_profit"]["usd"] - econ2["net_profit"]["usd"], 2))
            }
        }

    def predict(self, n, p, k, temperature, humidity, ph, rainfall, field_size_acres=1.0):
        """Run ML prediction and generate top recommendations with probabilities, fertilizer, and economics"""
        x = [float(n), float(p), float(k), float(temperature), float(humidity), float(ph), float(rainfall)]
        
        params = self.meta["model_parameters"]
        classes = params["classes"]
        priors = params["class_priors"]
        stats = params["stats"]
        
        # Compute Gaussian log-likelihood
        log_probs = {}
        for c in classes:
            lp = math.log(priors.get(c, 1.0 / len(classes)))
            c_stats = stats[c]
            for f_idx in range(len(x)):
                val = x[f_idx]
                mean, var = c_stats[f_idx]
                lp += -0.5 * math.log(2 * math.pi * var) - ((val - mean)**2) / (2 * var)
            log_probs[c] = lp
            
        # Softmax for normalized probability
        max_lp = max(log_probs.values())
        exps = {c: math.exp(lp - max_lp) for c, lp in log_probs.items()}
        total_exp = sum(exps.values())
        probs = {c: exps[c] / total_exp for c in classes}
        
        # Sort top 3
        sorted_crops = sorted(probs.items(), key=lambda t: t[1], reverse=True)[:3]
        top_recommendations = []
        
        for crop_name, conf in sorted_crops:
            crop_info = CROP_DETAILS.get(crop_name.lower(), {
                "title": crop_name.title(),
                "category": "Agricultural Crop",
                "icon": "🌱",
                "water_req": "Standard",
                "soil_type": "Loamy soil",
                "fertilizer_tip": "Follow recommended NPK dosage",
                "growing_season": "Standard",
                "description": "Suitable for given parameters."
            })
            
            agro = AGRONOMIC_PROFILES.get(crop_name.lower(), {})
            
            top_recommendations.append({
                "crop": crop_name,
                "confidence": round(conf * 100, 1),
                "details": crop_info,
                "duration_days": agro.get("duration_days", 120),
                "yield_per_acre": agro.get("yield_qtl_per_acre", 15.0),
                "risk_level": agro.get("risk_level", "Moderate")
            })
            
        primary = top_recommendations[0]
        soil_health = self.analyze_soil_health(n, p, k, ph)
        
        # Calculate Fertilizer Prescription & Economics for primary crop
        fertilizer_plan = self.calculate_fertilizer_dosage(primary["crop"], n, p, k, ph, field_size_acres)
        economic_projection = self.calculate_crop_economics(primary["crop"], field_size_acres, fertilizer_plan["costs"]["total_inr"])
        
        return {
            "top_recommendations": top_recommendations,
            "primary_crop": primary["crop"],
            "primary_details": primary["details"],
            "primary_confidence": primary["confidence"],
            "soil_health": soil_health,
            "fertilizer_plan": fertilizer_plan,
            "economic_projection": economic_projection,
            "inputs": {
                "N": n, "P": p, "K": k,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall,
                "field_size_acres": field_size_acres
            }
        }
