"""
Live Weather & Geocoding Service for AgroAI
Uses Open-Meteo free public API (No API key required)
Enhanced with 7-Day Agricultural Forecast & Smart Field Advisory Engine
"""
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

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
        headers={"User-Agent": "AgroAI-CropRecommender/2.0 (Agricultural Decision Support)"}
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))

def generate_agricultural_advisories(current, daily):
    """Generate actionable agronomic rules based on live weather and 7-day outlook"""
    advisories = []
    
    # 1. 3-Day Cumulative Precipitation
    daily_precip = daily.get("precipitation_sum", [])
    daily_probs = daily.get("precipitation_probability_max", [])
    daily_winds = daily.get("wind_speed_10m_max", [])
    daily_max_temps = daily.get("temperature_2m_max", [])
    daily_min_temps = daily.get("temperature_2m_min", [])
    
    three_day_rain = sum(daily_precip[:3]) if len(daily_precip) >= 3 else (sum(daily_precip) if daily_precip else 0.0)
    tomorrow_rain_prob = daily_probs[1] if len(daily_probs) > 1 else (daily_probs[0] if daily_probs else 0)
    current_wind = current.get("wind_speed_10m", 0.0)
    tomorrow_wind = daily_winds[1] if len(daily_winds) > 1 else current_wind
    
    # --- Irrigation Advisory ---
    if three_day_rain >= 25.0:
        advisories.append({
            "type": "irrigation",
            "title": "Hold Irrigation (High Rainfall Ahead)",
            "status": "Suspend Irrigation",
            "level": "warning",
            "icon": "🌧️",
            "badge_color": "#0284c7", # Sky blue
            "message": f"Forecast predicts ~{round(three_day_rain, 1)} mm rain in next 72 hours. Suspend field irrigation to avoid soil waterlogging and fertilizer leaching."
        })
    elif three_day_rain < 4.0 and any(t >= 32.0 for t in daily_max_temps[:3]):
        advisories.append({
            "type": "irrigation",
            "title": "Dry & Warm Spell (Irrigation Advised)",
            "status": "Irrigation Recommended",
            "level": "info",
            "icon": "💧",
            "badge_color": "#f59e0b", # Amber
            "message": "Warm temperatures with minimal rainfall expected. Maintain root-zone moisture, especially for crops in tillering or pod/fruit filling stages."
        })
    else:
        advisories.append({
            "type": "irrigation",
            "title": "Normal Soil Moisture Conditions",
            "status": "Standard Schedule",
            "level": "success",
            "icon": "🌱",
            "badge_color": "#10b981", # Green
            "message": "Moderate weather outlook. Maintain standard seasonal irrigation intervals according to crop growth phase."
        })

    # --- Spray Window Advisory ---
    if tomorrow_wind >= 20.0:
        advisories.append({
            "type": "spray",
            "title": "Unfavorable Spray Conditions (High Wind)",
            "status": "Avoid Spraying",
            "level": "warning",
            "icon": "💨",
            "badge_color": "#f97316", # Orange
            "message": f"Winds up to {round(tomorrow_wind, 1)} km/h will cause severe chemical drift. Postpone pesticide, herbicide, or foliar nutrient spraying."
        })
    elif tomorrow_rain_prob >= 40:
        advisories.append({
            "type": "spray",
            "title": "High Rain Risk for Foliar Sprays",
            "status": "Delay Spraying",
            "level": "warning",
            "icon": "🌧️",
            "badge_color": "#ef4444", # Red
            "message": f"{tomorrow_rain_prob}% chance of rain within 24-48 hours. Rain will wash away foliar applications. Wait for a dry 24-hour window."
        })
    else:
        advisories.append({
            "type": "spray",
            "title": "Favorable Spray Window",
            "status": "Ideal Spray Conditions",
            "level": "success",
            "icon": "🎯",
            "badge_color": "#10b981", # Green
            "message": f"Gentle wind ({round(tomorrow_wind, 1)} km/h) and low rain risk ({tomorrow_rain_prob}%). Suitable morning window for bio-fertilizers and protective sprays."
        })

    # --- Thermal & Weather Hazard Advisory ---
    max_forecast_temp = max(daily_max_temps) if daily_max_temps else current.get("temperature_2m", 25.0)
    min_forecast_temp = min(daily_min_temps) if daily_min_temps else current.get("temperature_2m", 25.0)
    
    if max_forecast_temp >= 38.0:
        advisories.append({
            "type": "thermal",
            "title": "Heat Stress Warning",
            "status": "Heatwave Alert",
            "level": "danger",
            "icon": "🔥",
            "badge_color": "#dc2626", # Crimson
            "message": f"Peak daytime temperatures reaching {max_forecast_temp}°C. Protect young seedlings with light evening irrigation or mulch."
        })
    elif min_forecast_temp <= 8.0:
        advisories.append({
            "type": "thermal",
            "title": "Chilling / Frost Risk",
            "status": "Cold Alert",
            "level": "warning",
            "icon": "❄️",
            "badge_color": "#3b82f6", # Blue
            "message": f"Night temperatures dropping to {min_forecast_temp}°C. Protect sensitive tropical crops (banana, papaya) against cold shock."
        })
        
    return advisories

def get_weather_by_coords(lat, lon, place_name=None):
    """Fetch current temperature, humidity, precipitation, 7-day forecast and agronomic advisories"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&"
            f"daily=precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,weather_code&"
            f"timezone=auto"
        )
        data = _make_request(url)
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        weather_code = current.get("weather_code", 0)
        cond_text, cond_icon = WMO_CODES.get(weather_code, ("Fair", "🌤️"))
        
        # Estimate monthly rainfall equivalent for agronomic recommendation model
        daily_precip = daily.get("precipitation_sum", [])
        if daily_precip:
            seven_day_precip = sum(daily_precip[:7])
            estimated_monthly_rainfall = round(max(20.0, min(300.0, seven_day_precip * 4.2 + 25.0)), 1)
        else:
            estimated_monthly_rainfall = 100.0

        temp = round(current.get("temperature_2m", 25.0), 1)
        humidity = round(current.get("relative_humidity_2m", 70.0), 1)
        
        # Build 7-Day Forecast Array
        forecast_days = []
        times = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precips = daily.get("precipitation_sum", [])
        probs = daily.get("precipitation_probability_max", [])
        winds = daily.get("wind_speed_10m_max", [])
        wcodes = daily.get("weather_code", [])
        
        for i in range(len(times)):
            dt_str = times[i]
            try:
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d")
                day_name = dt_obj.strftime("%a")
                fmt_date = dt_obj.strftime("%b %d")
            except Exception:
                day_name = f"Day {i+1}"
                fmt_date = dt_str
                
            code = wcodes[i] if i < len(wcodes) else 0
            w_text, w_icon = WMO_CODES.get(code, ("Fair", "🌤️"))
            
            forecast_days.append({
                "date": fmt_date,
                "day": day_name,
                "max_temp": round(max_temps[i], 1) if i < len(max_temps) else temp,
                "min_temp": round(min_temps[i], 1) if i < len(min_temps) else temp,
                "rain_mm": round(precips[i], 1) if i < len(precips) else 0.0,
                "rain_prob": int(probs[i]) if i < len(probs) and probs[i] is not None else 0,
                "wind_speed": round(winds[i], 1) if i < len(winds) else 0.0,
                "condition": w_text,
                "icon": w_icon
            })
            
        # Generate Smart Advisories
        advisories = generate_agricultural_advisories(current, daily)
        
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
            "forecast_7d": forecast_days,
            "advisories": advisories
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch weather: {str(e)}"}

def get_weather_by_city(city_name):
    """Geocode city name and fetch current weather with 7-day outlook"""
    if not city_name or not city_name.strip():
        return {"success": False, "error": "City name cannot be empty."}
        
    try:
        clean_city = urllib.parse.quote(city_name.strip())
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
        if weather_info.get("success"):
            weather_info["city"] = name
            weather_info["country"] = country
        return weather_info
    except Exception as e:
        return {"success": False, "error": f"Geocoding or weather lookup failed: {str(e)}"}
