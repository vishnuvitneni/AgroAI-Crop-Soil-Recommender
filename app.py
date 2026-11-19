"""
AgroAI - Crop Recommendation & Soil Health Diagnosis Full-Stack Web Application
Flask backend serving REST API, live Weather integration, SQLite history, and Crop Explorer.
"""
import os
import sys
import io
import csv
import json
from flask import Flask, render_template, request, jsonify
from src.recommend import CropAdvisoryEngine, CROP_DETAILS
from src.weather_service import get_weather_by_city, get_weather_by_coords
from src.database import save_prediction, get_history, get_prediction_by_id, clear_history
from src.market_rates import get_all_market_rates, get_commodity_by_id
from src.shops_service import get_nearby_shops
from src.farmer_tools import calculate_fertilizer_bags, get_pest_and_disease_guide, get_helplines, CROP_FERT_GUIDELINES
from src.ai_chatbot import generate_ai_response
from src.season_and_profit import estimate_farm_budget, get_seasonal_crops_data, CROP_BUDGET_BENCHMARKS

app = Flask(__name__)
engine = CropAdvisoryEngine()

PRESETS = {
    "monsoon_rice": {
        "title": "🌾 Monsoon Wetland (Paddy/Jute)",
        "desc": "Heavy rainfall, high humidity, warm tropical climate with moderate NPK",
        "values": {"n": 85, "p": 45, "k": 40, "temperature": 24.5, "humidity": 82.0, "ph": 6.5, "rainfall": 230.0, "acres": 2.5}
    },
    "temperate_orchard": {
        "title": "🍏 High Altitude Orchard (Apple)",
        "desc": "Cool temperatures, high potassium soil, moderate rainfall",
        "values": {"n": 25, "p": 130, "k": 195, "temperature": 21.0, "humidity": 92.0, "ph": 6.0, "rainfall": 110.0, "acres": 3.0}
    },
    "tropical_banana": {
        "title": "🍌 Tropical Humid (Banana/Papaya)",
        "desc": "Warm, sunny, rich potassium and nitrogen nutrition with steady rainfall",
        "values": {"n": 105, "p": 75, "k": 52, "temperature": 27.5, "humidity": 80.0, "ph": 6.2, "rainfall": 105.0, "acres": 2.0}
    },
    "semiarid_cotton": {
        "title": "☁️ Black Cotton Belt (Cotton/Maize)",
        "desc": "Warm semi-arid climate, deep black soil, moderate rainfall",
        "values": {"n": 118, "p": 48, "k": 22, "temperature": 24.0, "humidity": 65.0, "ph": 6.8, "rainfall": 75.0, "acres": 5.0}
    },
    "winter_pulses": {
        "title": "🌱 Cool Winter Pulses (Chickpea/Lentil)",
        "desc": "Low nitrogen (leguminous fixation), high phosphorus, low rainfall",
        "values": {"n": 38, "p": 68, "k": 80, "temperature": 18.5, "humidity": 17.0, "ph": 7.2, "rainfall": 78.0, "acres": 4.0}
    }
}

@app.route("/")
def index():
    meta = engine.meta or {}
    benchmarks = meta.get("model_benchmarks", {})
    crop_catalog = engine.get_crop_catalog()
    market_rates = get_all_market_rates()
    diseases = get_pest_and_disease_guide()
    helplines = get_helplines()
    seasons = get_seasonal_crops_data()
    return render_template("index.html", 
                           presets=PRESETS, 
                           benchmarks=benchmarks, 
                           crop_catalog=crop_catalog,
                           market_rates=market_rates,
                           fert_crops=CROP_FERT_GUIDELINES,
                           diseases=diseases,
                           helplines=helplines,
                           seasons=seasons,
                           budget_crops=CROP_BUDGET_BENCHMARKS,
                           crop_count=len(CROP_DETAILS))

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        reply = generate_ai_response(user_msg)
        return jsonify({"status": "success", "reply": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/seasons", methods=["GET"])
def api_seasons():
    return jsonify({"status": "success", "seasons": get_seasonal_crops_data()})

@app.route("/api/profit-estimator", methods=["POST"])
def api_profit_estimator():
    try:
        data = request.get_json(force=True)
        crop = data.get("crop", "rice")
        land_size = float(data.get("land_size", 1.0))
        unit = data.get("unit", "acre")
        budget = estimate_farm_budget(crop, land_size, unit)
        return jsonify({"status": "success", "budget": budget})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/market-rates", methods=["GET"])
def api_market_rates():
    cat = request.args.get("category", "")
    q = request.args.get("q", "")
    rates = get_all_market_rates(category=cat, query=q)
    return jsonify({"status": "success", "rates": rates})

@app.route("/api/shops", methods=["GET"])
def api_shops():
    loc = request.args.get("location", "Hyderabad, Telangana")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    lat_val = float(lat) if lat and lat != "undefined" else None
    lon_val = float(lon) if lon and lon != "undefined" else None
    shops_data = get_nearby_shops(location_name=loc, lat=lat_val, lon=lon_val)
    return jsonify({"status": "success", "data": shops_data})

@app.route("/api/fertilizer-calc", methods=["POST"])
def api_fertilizer_calc():
    try:
        data = request.get_json(force=True)
        crop = data.get("crop", "rice")
        land_size = float(data.get("land_size", 1.0))
        unit = data.get("unit", "acre")
        calc = calculate_fertilizer_bags(crop, land_size, unit)
        return jsonify({"status": "success", "calc": calc})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/disease-guide", methods=["GET"])
def api_disease_guide():
    q = request.args.get("q", "")
    guide = get_pest_and_disease_guide(q)
    return jsonify({"status": "success", "diseases": guide})

@app.route("/api/helplines", methods=["GET"])
def api_helplines():
    return jsonify({"status": "success", "helplines": get_helplines()})

@app.route("/api/crops", methods=["GET"])
def api_crops():
    catalog = engine.get_crop_catalog()
    return jsonify({"status": "success", "crops": catalog})

@app.route("/api/crops/<crop_name>/compatibility", methods=["POST"])
def api_crop_compatibility(crop_name):
    try:
        data = request.get_json(force=True) or {}
        n = float(data.get("n", 50))
        p = float(data.get("p", 50))
        k = float(data.get("k", 50))
        temp = float(data.get("temperature", 25.0))
        hum = float(data.get("humidity", 70.0))
        ph = float(data.get("ph", 6.5))
        rain = float(data.get("rainfall", 100.0))
        
        analysis = engine.analyze_crop_compatibility(crop_name, n, p, k, temp, hum, ph, rain)
        if not analysis:
            return jsonify({"status": "error", "message": f"Crop '{crop_name}' not found."}), 404
        return jsonify({"status": "success", "analysis": analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/fertilizer", methods=["POST"])
def api_fertilizer():
    try:
        data = request.get_json(force=True) or {}
        crop = data.get("crop", "rice")
        n = float(data.get("n", 50))
        p = float(data.get("p", 50))
        k = float(data.get("k", 50))
        ph = float(data.get("ph", 6.5))
        acres = float(data.get("acres", 1.0))
        
        plan = engine.calculate_fertilizer_dosage(crop, n, p, k, ph, acres)
        return jsonify({"status": "success", "plan": plan})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/economics", methods=["POST"])
def api_economics():
    try:
        data = request.get_json(force=True) or {}
        crop = data.get("crop", "rice")
        acres = float(data.get("acres", 1.0))
        fert_cost = float(data.get("fertilizer_cost", 0.0))
        
        econ = engine.calculate_crop_economics(crop, acres, fert_cost)
        return jsonify({"status": "success", "economics": econ})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/crops/compare", methods=["POST"])
def api_compare_crops():
    try:
        data = request.get_json(force=True) or {}
        crop1 = data.get("crop1", "rice")
        crop2 = data.get("crop2", "maize")
        n = float(data.get("n", 50))
        p = float(data.get("p", 50))
        k = float(data.get("k", 50))
        temp = float(data.get("temperature", 25.0))
        hum = float(data.get("humidity", 70.0))
        ph = float(data.get("ph", 6.5))
        rain = float(data.get("rainfall", 100.0))
        acres = float(data.get("acres", 1.0))
        
        comparison = engine.compare_crops(crop1, crop2, n, p, k, temp, hum, ph, rain, acres)
        if not comparison:
            return jsonify({"status": "error", "message": "One or both selected crops could not be found."}), 404
        return jsonify({"status": "success", "comparison": comparison})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/weather/city", methods=["GET"])
def api_weather_city():
    city = request.args.get("q", "").strip()
    if not city:
        return jsonify({"success": False, "error": "City name parameter 'q' is required"}), 400
    res = get_weather_by_city(city)
    return jsonify(res), (200 if res.get("success") else 404)

@app.route("/api/weather/coords", methods=["GET"])
def api_weather_coords():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        place = request.args.get("place", "")
        res = get_weather_by_coords(lat, lon, place_name=place)
        return jsonify(res), (200 if res.get("success") else 500)
    except Exception as e:
        return jsonify({"success": False, "error": f"Invalid coordinates: {str(e)}"}), 400

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(force=True) or {}
        n = float(data.get("n", 50))
        p = float(data.get("p", 50))
        k = float(data.get("k", 50))
        temp = float(data.get("temperature", 25.0))
        hum = float(data.get("humidity", 70.0))
        ph = float(data.get("ph", 6.5))
        rain = float(data.get("rainfall", 100.0))
        acres = float(data.get("acres", 1.0))
        location = data.get("location", "Custom Field")
        
        result = engine.predict(n, p, k, temp, hum, ph, rain, field_size_acres=acres)
        
        # Determine overall soil summary
        n_stat = result["soil_health"]["N"]["status"]
        ph_stat = result["soil_health"]["pH"]["status"]
        summary = f"{n_stat} Nitrogen, {ph_stat}"
        
        # Save to SQLite history
        rec_id = save_prediction(
            location=location,
            n=n, p=p, k=k,
            temperature=temp,
            humidity=hum,
            ph=ph,
            rainfall=rain,
            predicted_crop=result["primary_crop"],
            confidence=result["primary_confidence"],
            soil_status=summary
        )
        result["record_id"] = rec_id
        
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/history", methods=["GET"])
def api_get_history():
    history = get_history(limit=50)
    return jsonify({"status": "success", "history": history})

@app.route("/api/history", methods=["DELETE"])
def api_clear_history():
    clear_history()
    return jsonify({"status": "success", "message": "History cleared successfully"})

@app.route("/api/history/export", methods=["GET"])
def api_export_history():
    history = get_history(limit=500)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Record ID", "Timestamp", "Location", 
        "Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "pH Level",
        "Temperature (C)", "Humidity (%)", "Rainfall (mm)",
        "Recommended Crop", "Confidence (%)", "Soil Summary"
    ])
    for h in history:
        writer.writerow([
            h.get("id"), h.get("timestamp"), h.get("location"),
            h.get("n"), h.get("p"), h.get("k"), h.get("ph"),
            h.get("temperature"), h.get("humidity"), h.get("rainfall"),
            h.get("predicted_crop"), h.get("confidence"), h.get("soil_status")
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=agroai_soil_test_history.csv"}
    )

@app.route("/api/shops", methods=["GET"])
def api_nearby_shops():
    location = request.args.get("location", "Hyderabad, Telangana, India").strip()
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    res = get_nearby_shops(location_name=location, lat=lat, lon=lon)
    return jsonify({"status": "success", "data": res})

@app.route("/api/prices", methods=["GET"])
def api_prices():
    category = request.args.get("category", "all")
    items = get_price_drop_sheet(category)
    return jsonify({"status": "success", "total": len(items), "items": items})

@app.route("/api/prices/export", methods=["GET"])
def api_export_prices():
    items = get_price_drop_sheet()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Item ID", "Commodity Name", "Category", "Brand / Manufacturer",
        "MRP (INR)", "Current Price (INR)", "Price Drop (%)", "Discount Amount (INR)",
        "Subsidy Tag", "Stock Status", "Availability Notes"
    ])
    for item in items:
        writer.writerow([
            item.get("id"), item.get("name"), item.get("category"), item.get("brand"),
            item.get("mrp_inr"), item.get("current_price_inr"), item.get("price_drop_pct"),
            item.get("drop_amount_inr"), item.get("subsidy_tag"), item.get("stock_status"),
            item.get("notes")
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=agroai_price_drop_sheet.csv"}
    )

@app.route("/report/<int:prediction_id>")
def view_report(prediction_id):
    rec = get_prediction_by_id(prediction_id)
    if not rec:
        return "Advisory report not found", 404
        
    crop_name = rec["predicted_crop"].lower()
    details = CROP_DETAILS.get(crop_name, {
        "title": crop_name.title(),
        "category": "Agricultural Crop",
        "icon": "🌱",
        "water_req": "Standard",
        "soil_type": "Loam",
        "fertilizer_tip": "Balanced NPK",
        "growing_season": "Standard",
        "description": "Suitable for given soil and climate."
    })
    
    # Calculate fertilizer prescription & economics for report
    fert = engine.calculate_fertilizer_dosage(
        crop_name=crop_name,
        n_soil=rec["n"],
        p_soil=rec["p"],
        k_soil=rec["k"],
        ph_soil=rec["ph"],
        field_size_acres=1.0 # Standard 1-acre benchmark
    )
    econ = engine.calculate_crop_economics(
        crop_name=crop_name,
        field_size_acres=1.0,
        fertilizer_cost_inr=fert["costs"]["total_inr"]
    )
    
    return render_template("report.html", rec=rec, details=details, fert=fert, econ=econ)

@app.route("/api/presets", methods=["GET"])
def api_presets():
    return jsonify({"status": "success", "presets": PRESETS})

@app.route("/api/model-info", methods=["GET"])
def api_model_info():
    return jsonify({"status": "success", "metadata": engine.meta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
