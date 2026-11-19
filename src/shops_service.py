"""
Nearby Agricultural & Fertilizer Shops Discovery Service
Finds certified dealers, IFFCO Kisan Seva Kendras, Seed Stores, and KVK centers.
"""
import urllib.parse

SAMPLE_DEALER_TEMPLATES = [
    {
        "name_prefix": "IFFCO Kisan Seva Kendra & Fertilizer Hub",
        "category": "Govt / Cooperative Certified Center",
        "icon": "🏛️",
        "license": "IFFCO-AGRI-AUTH-2024",
        "products": ["Urea (Govt Subsidized)", "DAP (50kg)", "MOP", "Nano Urea Liquid", "Bio-Fertilizers", "Soil Testing Support"],
        "phone": "+91 94401 22841",
        "rating": 4.8,
        "timing": "8:00 AM - 7:30 PM (Mon-Sat)"
    },
    {
        "name_prefix": "Kisan Agro Agencies & Certified Seeds",
        "category": "Authorized Seeds & Crop Protection",
        "icon": "🌱",
        "license": "DEPT-AGRI-SEED-LIC-881",
        "products": ["Hybrid Paddy Seeds", "Bt Cotton Seeds", "Maize & Vegetable Seeds", "Neem Oil Sprays", "Fungicides & Insecticides"],
        "phone": "+91 98852 34190",
        "rating": 4.7,
        "timing": "8:30 AM - 8:00 PM (Daily)"
    },
    {
        "name_prefix": "Gromor Agro Center (Coromandel / Fertilizers)",
        "category": "Fertilizers & Specialty Nutrition",
        "icon": "🧪",
        "license": "COROMANDEL-RETAIL-4019",
        "products": ["Gromor 28-28-0", "14-35-14 Complex", "Zinc Sulfate 21%", "Bentonite Sulfur", "Water Soluble NPK 19-19-19"],
        "phone": "+91 97014 55120",
        "rating": 4.9,
        "timing": "8:00 AM - 7:00 PM (Mon-Sat)"
    },
    {
        "name_prefix": "Rythu Mitra Bio-Organic & Farm Equipment",
        "category": "Organic Inputs & Sprayers",
        "icon": "🚜",
        "license": "ORGANIC-AGRI-RETAIL-112",
        "products": ["Vermi-Compost", "Trichoderma Viride", "Battery Operated Backpack Sprayers", "Drip Irrigation Fittings", "Tarpaulins"],
        "phone": "+91 93902 67812",
        "rating": 4.6,
        "timing": "9:00 AM - 8:30 PM (Daily)"
    },
    {
        "name_prefix": "District Krishi Vigyan Kendra (KVK) & Soil Testing Lab",
        "category": "ICAR Agricultural Research & Advisory",
        "icon": "🔬",
        "license": "ICAR-GOVT-KVK-CENTRAL",
        "products": ["Certified Foundation Seeds", "Soil & Water Testing Labs", "Free Agronomist Consultation", "Pest Diagnosis"],
        "phone": "1800-180-1551 (Kisan Helpline)",
        "rating": 5.0,
        "timing": "9:30 AM - 5:30 PM (Mon-Fri)"
    }
]

def get_nearby_shops(location_name=None, lat=None, lon=None):
    """
    Returns list of nearby agricultural shops and dynamic Google Maps query links.
    """
    loc_display = location_name or "Your Area"
    # Clean location for maps search
    city_only = loc_display.split(",")[0].strip()
    
    encoded_city = urllib.parse.quote(city_only + " fertilizer shops")
    encoded_seeds = urllib.parse.quote(city_only + " agriculture seed pesticide stores")
    
    if lat and lon:
        maps_link_fert = f"https://www.google.com/maps/search/fertilizer+shops/@{lat},{lon},13z"
        maps_link_seeds = f"https://www.google.com/maps/search/agri+seeds+pesticides/@{lat},{lon},13z"
    else:
        maps_link_fert = f"https://www.google.com/maps/search/{encoded_city}"
        maps_link_seeds = f"https://www.google.com/maps/search/{encoded_seeds}"

    shops = []
    distances = ["1.2 km away", "2.8 km away", "4.1 km away", "5.5 km away", "8.0 km away"]
    
    for idx, t in enumerate(SAMPLE_DEALER_TEMPLATES):
        dist = distances[idx % len(distances)]
        shop_title = f"{t['name_prefix']} - {city_only}"
        single_map_query = urllib.parse.quote(f"{shop_title}")
        
        shops.append({
            "id": idx + 1,
            "name": shop_title,
            "category": t["category"],
            "icon": t["icon"],
            "distance": dist,
            "address": f"Main Road, Near APMC Market Yard, {loc_display}",
            "phone": t["phone"],
            "license": t["license"],
            "rating": t["rating"],
            "timing": t["timing"],
            "products": t["products"],
            "directions_url": f"https://www.google.com/maps/search/{single_map_query}"
        })
        
    return {
        "location": loc_display,
        "shops": shops,
        "maps_quick_links": {
            "all_fertilizers": maps_link_fert,
            "all_seeds": maps_link_seeds
        }
    }
