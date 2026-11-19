"""
Live Weather & Geocoding Service for AgroAI
Uses Open-Meteo free public API (No API key required)
"""
import json
import urllib.request
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

def _make_request(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AgroAI-CropRecommender/1.0 (Educational Agri-ML App)"}
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_weather_by_coords(lat, lon, place_name=None):
    """Fetch current temperature, humidity, precipitation and forecast for given lat/lon"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&"
            f"daily=precipitation_sum,temperature_2m_max,temperature_2m_min&"
            f"timezone=auto"
        )
        data = _make_request(url)
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        weather_code = current.get("weather_code", 0)
        cond_text, cond_icon = WMO_CODES.get(weather_code, ("Fair", "🌤️"))
        
        # Estimate rainfall for agronomic recommendation:
        # Sum 7-day predicted precipitation or scale current daily precipitation
        daily_precip = daily.get("precipitation_sum", [])
        if daily_precip:
            seven_day_precip = sum(daily_precip[:7])
            # Monthly estimated rainfall equivalent in mm (typical metric for crop growth model)
            estimated_monthly_rainfall = round(max(20.0, min(300.0, seven_day_precip * 4.2 + 25.0)), 1)
        else:
            estimated_monthly_rainfall = 100.0

        temp = round(current.get("temperature_2m", 25.0), 1)
        humidity = round(current.get("relative_humidity_2m", 70.0), 1)
        
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
            "wind_speed": current.get("wind_speed_10m", 0.0)
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch weather: {str(e)}"}

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

def get_weather_by_city(city_name):
    """Geocode city name and fetch current weather"""
    if not city_name or not city_name.strip():
        return {"success": False, "error": "City name cannot be empty."}
        
    try:
        norm_city = city_name.strip().lower()
        search_query = CITY_ALIASES.get(norm_city, city_name.strip())
        
        clean_city = urllib.parse.quote(search_query)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_city}&count=1&language=en&format=json"
        geo_data = _make_request(geo_url)
        
        results = geo_data.get("results", [])
        if not results:
            return {"success": False, "error": f"Could not find location for '{city_name}'."}
            
        first = results[0]
        lat = first["latitude"]
        lon = first["longitude"]
        name = first.get("name", city_name)
        admin1 = first.get("admin1", "")
        country = first.get("country", "")
        
        display_parts = [p for p in [name, admin1, country] if p]
        full_location = ", ".join(display_parts)
        
        weather_info = get_weather_by_coords(lat, lon, place_name=full_location)
        if weather_info["success"]:
            weather_info["city"] = name
            weather_info["country"] = country
        return weather_info
    except Exception as e:
        return {"success": False, "error": f"Geocoding or weather lookup failed: {str(e)}"}
