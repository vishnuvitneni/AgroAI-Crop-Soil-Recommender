"""
Crop Recommendation and Soil Health Advisory Engine
"""
import os
import json
import math

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
        "category": "Horticultural Fruit",
        "icon": "🍎",
        "water_req": "Moderate (Drip irrigation recommended)",
        "soil_type": "Well-drained deep loamy or alluvial soil",
        "fertilizer_tip": "High Potassium (MOP or SOP) during fruit development for vibrant rind color and sweetness.",
        "growing_season": "Perennial (Hasta / Ambe / Mrig Bahar seasons)",
        "description": "Lucrative fruit crop that thrives in semi-arid conditions with low relative humidity."
    },
    "banana": {
        "title": "Banana (Musa acuminata)",
        "category": "Tropical Fruit",
        "icon": "🍌",
        "water_req": "Very High (Requires continuous soil moisture)",
        "soil_type": "Deep, fertile rich alluvial or loamy soil rich in organic matter",
        "fertilizer_tip": "Heavy feeder of Potassium and Nitrogen. Apply N and K2O in frequent small fertigation doses.",
        "growing_season": "Perennial (Planted year-round in tropical belts)",
        "description": "Fast-growing high-yield tropical crop demanding high nutrition and abundant water."
    },
    "mango": {
        "title": "Mango (Mangifera indica)",
        "category": "Fruit Orchard",
        "icon": "🥭",
        "water_req": "Moderate (Needs dry spell before flowering)",
        "soil_type": "Deep alluvial, well-drained loamy soil",
        "fertilizer_tip": "Farmyard manure (FYM) + N-P-K applied post-monsoon. Micronutrient spray (Boron & Zinc) prevents fruit drop.",
        "growing_season": "Summer fruit (Perennial tree)",
        "description": "King of fruits; requires distinct dry period to induce abundant flowering."
    },
    "grapes": {
        "title": "Grapes (Vitis vinifera)",
        "category": "Vineyard Fruit",
        "icon": "🍇",
        "water_req": "Moderate (Controlled drip irrigation)",
        "soil_type": "Well-drained sandy loam or gravelly soil",
        "fertilizer_tip": "Potassium-dominant nutrition during berry enlargement and veraison for high brix (sugar).",
        "growing_season": "Perennial (Pruned twice yearly)",
        "description": "Requires sunny, warm dry climate; excessive rain during ripening causes berry cracking."
    },
    "watermelon": {
        "title": "Watermelon (Citrullus lanatus)",
        "category": "Cucurbit / Fruit",
        "icon": "🍉",
        "water_req": "Moderate (Frequent shallow irrigation until ripening)",
        "soil_type": "Sandy or sandy loam soils near riverbeds",
        "fertilizer_tip": "High Potassium and Calcium prevents blossom end rot and improves rind firmness.",
        "growing_season": "Zaid (Spring / Summer)",
        "description": "Heat-loving crop requiring warm days and cool nights for maximum sugar content."
    },
    "muskmelon": {
        "title": "Muskmelon / Cantaloupe (Cucumis melo)",
        "category": "Cucurbit / Fruit",
        "icon": "🍈",
        "water_req": "Moderate (Cut irrigation 7-10 days before harvest for sweetness)",
        "soil_type": "Sandy loam soil with excellent drainage",
        "fertilizer_tip": "Balanced NPK + Foliar micronutrients (Boron & Magnesium).",
        "growing_season": "Summer (Zaid)",
        "description": "Thrives under long sunny warm days with low atmospheric humidity."
    },
    "apple": {
        "title": "Apple (Malus domestica)",
        "category": "Temperate Fruit",
        "icon": "🍏",
        "water_req": "Moderate to High (1000-1200 mm rainfall or snowmelt)",
        "soil_type": "Well-drained deep loamy soil rich in humus",
        "fertilizer_tip": "Apply Nitrogen in early spring; Calcium sprays during fruit development prevent bitter pit.",
        "growing_season": "Temperate / High Altitude (requires 800-1000 chilling hours below 7°C)",
        "description": "Premier temperate orchard crop requiring cold winters and mild summers."
    },
    "orange": {
        "title": "Orange / Citrus (Citrus sinensis)",
        "category": "Citrus Fruit",
        "icon": "🍊",
        "water_req": "Moderate (Regular basin or drip irrigation)",
        "soil_type": "Deep well-drained sandy loam to clay loam, free from hardpan",
        "fertilizer_tip": "Zinc, Iron, and Manganese foliar sprays prevent citrus chlorosis. Balanced NPK with Organic manure.",
        "growing_season": "Sub-tropical / Perennial",
        "description": "Requires well-drained soil with good aeration to avoid root rot."
    },
    "papaya": {
        "title": "Papaya (Carica papaya)",
        "category": "Tropical Fruit",
        "icon": "🍈",
        "water_req": "Moderate (Extremely sensitive to waterlogging)",
        "soil_type": "Well-drained rich alluvial or sandy loam soil",
        "fertilizer_tip": "Apply 200g N, 200g P, 250g K per plant divided into 6 applications per year.",
        "growing_season": "Tropical (10-12 months seed-to-fruit)",
        "description": "Rapidly growing herbaceous plant that yields within one year of transplanting."
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

class CropAdvisoryEngine:
    def __init__(self, model_file="models/trained_model.json"):
        self.model_file = model_file
        self.meta = None
        self.load()
        
    def load(self):
        if not os.path.exists(self.model_file):
            raise FileNotFoundError(f"Model file {self.model_file} not found. Run train.py first.")
        with open(self.model_file, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
            
    def get_crop_catalog(self):
        """Return list of all supported crops with metadata for search"""
        profiles = self.meta.get("crop_profiles", {})
        catalog = []
        for crop_id, details in CROP_DETAILS.items():
            ideal = profiles.get(crop_id, {})
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
                "ideal_profile": ideal
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
        
        # Calculate feature deviations & suitability score
        # Using normalized squared differences
        user_vals = {
            "N": n, "P": p, "K": k,
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall
        }
        
        # Weights for agricultural importance
        weights = {
            "rainfall": 0.22,
            "humidity": 0.18,
            "temperature": 0.18,
            "ph": 0.14,
            "N": 0.10,
            "P": 0.09,
            "K": 0.09
        }
        
        # Max standard ranges for normalization
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
            
            # Record significant differences
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
            "compatibility_score": compatibility_score,
            "gaps": gaps,
            "user_values": user_vals
        }

    def analyze_soil_health(self, n, p, k, ph):
        """Diagnose soil nutrient levels and pH status"""
        health = {}
        
        # Nitrogen (N)
        if n < 40:
            health["N"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Nitrogen limits vegetative growth. Add Urea or composted manure."}
        elif n <= 90:
            health["N"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Nitrogen level is in a balanced, productive range."}
        else:
            health["N"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "High Nitrogen can cause excess foliage and delayed maturity. Reduce synthetic nitrogen."}
            
        # Phosphorus (P)
        if p < 35:
            health["P"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Phosphorus restricts root establishment. Incorporate DAP or Single Superphosphate (SSP)."}
        elif p <= 75:
            health["P"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Phosphorus level is ideal for vigorous root and flower formation."}
        else:
            health["P"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "High soil Phosphorus. Avoid adding excess phosphate fertilizers."}

        # Potassium (K)
        if k < 30:
            health["K"] = {"status": "Low / Deficient", "badge": "Deficient", "color": "#ef4444", "tip": "Low Potassium lowers disease resistance. Add Muriate of Potash (MOP)."}
        elif k <= 65:
            health["K"] = {"status": "Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Potassium level supports high stress tolerance and fruit filling."}
        else:
            health["K"] = {"status": "High / Rich", "badge": "High", "color": "#f59e0b", "tip": "High Potassium level. Excellent for fruit crops and root vegetables."}

        # pH Level
        if ph < 5.5:
            health["pH"] = {"status": "Strongly Acidic", "badge": "Acidic", "color": "#ef4444", "tip": "Acidic soil fixes nutrients. Apply agricultural lime (calcium carbonate) to raise pH."}
        elif ph < 6.5:
            health["pH"] = {"status": "Slightly Acidic", "badge": "Optimal", "color": "#10b981", "tip": "Slightly acidic soil; very favorable for most cereal, pulse, and cash crops."}
        elif ph <= 7.5:
            health["pH"] = {"status": "Neutral / Optimal", "badge": "Optimal", "color": "#10b981", "tip": "Neutral pH offers peak nutrient bioavailability for standard agriculture."}
        elif ph <= 8.5:
            health["pH"] = {"status": "Slightly Alkaline", "badge": "Alkaline", "color": "#f59e0b", "tip": "Slightly alkaline. Add gypsum or organic compost to buffer pH."}
        else:
            health["pH"] = {"status": "Strongly Alkaline", "badge": "Alkaline", "color": "#ef4444", "tip": "Alkaline soil causes micronutrient lockup. Treat with elemental sulfur or gypsum."}

        return health

    def predict(self, n, p, k, temperature, humidity, ph, rainfall):
        """Run ML prediction and generate top recommendations with probabilities"""
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
            
            top_recommendations.append({
                "crop": crop_name,
                "confidence": round(conf * 100, 1),
                "details": crop_info
            })
            
        primary = top_recommendations[0]
        soil_health = self.analyze_soil_health(n, p, k, ph)
        
        return {
            "top_recommendations": top_recommendations,
            "primary_crop": primary["crop"],
            "primary_details": primary["details"],
            "primary_confidence": primary["confidence"],
            "soil_health": soil_health,
            "inputs": {
                "N": n, "P": p, "K": k,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            }
        }
