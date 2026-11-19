"""
Live Weather & Geocoding Service for AgroAI
Uses dual-tier geocoding (Open-Meteo + OpenStreetMap Nominatim)
Ensures villages, gram panchayats, and towns worldwide resolve accurately.
"""
import json
import urllib.request
import urllib.parse
import urllib.error

# WMO Weather interpretation codes
WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "🌨️"),
    73: ("Moderate Snow", "🌨️"),
    75: ("Heavy Snow", "❄️"),
    80: ("Slight Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌧️"),
    82: ("Violent Rain Showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Slight Hail", "⛈️"),
    99: ("Thunderstorm with Heavy Hail", "⛈️")
}

CITY_ALIASES = {
    "bangluru": "Bengaluru",
    "banglore": "Bengaluru",
    "bengalooru": "Bengaluru",
    "bengaluru": "Bengaluru",
    "hydrabad": "Hyderabad",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "calcutta": "Kolkata",
    "delhy": "Delhi",
    "ahmedbad": "Ahmedabad",
    "vizag": "Visakhapatnam",
}

def _make_request(url, user_agent="AgroAI-CropRecommender/2.0 (Agri-ML Decision Support)"):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent}
    )
    with urllib.request.urlopen(req, timeout=7) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_weather_by_coords(lat, lon, place_name=None):
    """Fetch current temperature, humidity, precipitation and 7-day forecast"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&"
            f"daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&"
            f"timezone=auto"
        )
        data = _make_request(url)
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        weather_code = current.get("weather_code", 0)
        cond_text, cond_icon = WMO_CODES.get(weather_code, ("Fair", "🌤️"))
        
        # Monthly estimated rainfall equivalent in mm for crop model
        daily_precip = daily.get("precipitation_sum", [])
        if daily_precip:
            seven_day_precip = sum(daily_precip[:7])
            estimated_monthly_rainfall = round(max(20.0, min(300.0, seven_day_precip * 4.2 + 25.0)), 1)
        else:
            estimated_monthly_rainfall = 100.0

        temp = round(current.get("temperature_2m", 25.0), 1)
        humidity = round(current.get("relative_humidity_2m", 70.0), 1)
        
        # Build 5-day farmer agromet advisory
        forecast_days = []
        dates = daily.get("time", [])[:5]
        max_temps = daily.get("temperature_2m_max", [])[:5]
        min_temps = daily.get("temperature_2m_min", [])[:5]
        precips = daily.get("precipitation_sum", [])[:5]
        w_codes = daily.get("weather_code", [])[:5]
        
        for i in range(len(dates)):
            w_c = w_codes[i] if i < len(w_codes) else 0
            c_txt, c_ico = WMO_CODES.get(w_c, ("Fair", "🌤️"))
            rain_val = round(precips[i], 1) if i < len(precips) else 0.0
            
            # Advisory for spraying & irrigation
            if rain_val > 5.0:
                farm_tip = "Rain expected; avoid spraying pesticides/fertilizers today."
            elif max_temps[i] > 36.0:
                farm_tip = "High heat; ensure evening irrigation to prevent heat stress."
            else:
                farm_tip = "Favorable weather for field activities & spraying."
                
            forecast_days.append({
                "date": dates[i],
                "max_temp": max_temps[i] if i < len(max_temps) else temp,
                "min_temp": min_temps[i] if i < len(min_temps) else temp - 5,
                "rain_mm": rain_val,
                "condition": c_txt,
                "icon": c_ico,
                "farming_advice": farm_tip
            })
        
        return {
            "success": True,
            "location": place_name or f"{lat:.2f}, {lon:.2f}",
            "latitude": lat,
            "longitude": lon,
            "temperature": temp,
            "humidity": humidity,
            "precipitation": round(current.get("precipitation", 0.0), 1),
            "estimated_rainfall": estimated_monthly_rainfall,
            "weather_code": weather_code,
            "condition": cond_text,
            "icon": cond_icon,
            "wind_speed": current.get("wind_speed_10m", 0.0),
            "forecast": forecast_days
        }
    except Exception as e:
        return {"success": False, "error": f"Weather API error: {str(e)}"}

def _geocode_nominatim(query):
    """Fallback geocoding using OpenStreetMap Nominatim for small villages and mandals"""
    try:
        clean_q = urllib.parse.quote(query)
        osm_url = f"https://nominatim.openstreetmap.org/search?q={clean_q}&format=json&limit=1&addressdetails=1"
        data = _make_request(osm_url, user_agent="AgroAI-FarmerTool/2.0 (agri@agroai.org)")
        if data and len(data) > 0:
            item = data[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            disp = item.get("display_name", query)
            # Simplify display name: take first 3 segments
            parts = [p.strip() for p in disp.split(",")]
            short_name = ", ".join(parts[:3])
            return lat, lon, short_name
    except Exception:
        pass
    return None

def get_weather_by_city(city_name):
    """
    Robust dual-tier geocoding:
    1. Check alias dictionary
    2. Try Open-Meteo Geocoding
    3. If not found, fallback to OpenStreetMap Nominatim (finds any village/mandal)
    """
    if not city_name or not city_name.strip():
        return {"success": False, "error": "City or village name cannot be empty."}
        
    raw_query = city_name.strip()
    norm_city = raw_query.lower()
    search_query = CITY_ALIASES.get(norm_city, raw_query)
    
    lat = None
    lon = None
    full_location = None
    
    # Tier 1: Open-Meteo Geocoding
    try:
        clean_city = urllib.parse.quote(search_query)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_city}&count=1&language=en&format=json"
        geo_data = _make_request(geo_url)
        results = geo_data.get("results", [])
        if results:
            first = results[0]
            lat = first["latitude"]
            lon = first["longitude"]
            name = first.get("name", raw_query)
            admin1 = first.get("admin1", "")
            country = first.get("country", "")
            display_parts = [p for p in [name, admin1, country] if p]
            full_location = ", ".join(display_parts)
    except Exception:
        pass

    # Tier 2: OpenStreetMap Nominatim Fallback (finds villages, gram panchayats)
    if lat is None or lon is None:
        osm_res = _geocode_nominatim(raw_query)
        if osm_res:
            lat, lon, full_location = osm_res
            
    if lat is None or lon is None:
        return {
            "success": False, 
            "error": f"Could not find location for '{city_name}'. Please check the spelling or enter your district/nearby town."
        }
        
    weather_info = get_weather_by_coords(lat, lon, place_name=full_location)
    if weather_info["success"]:
        weather_info["city"] = full_location.split(",")[0]
    return weather_info
