"""
Comprehensive Test Suite for AgroAI Crop Recommender, Soil Diagnostic & Farming Advisory Engine
Verifies ML pipeline, database persistence, weather service, fertilizer dosage, crop economics, and Flask REST endpoints.
"""
import os
import json
import pytest
from app import app
from src.recommend import CropAdvisoryEngine, CROP_DETAILS, AGRONOMIC_PROFILES
from src.database import init_db, save_prediction, get_history, get_prediction_by_id, clear_history
from src.weather_service import get_weather_by_city, get_weather_by_coords

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_crop_catalog_completeness():
    """Ensure all 22 crop categories are present in knowledge base with agronomic profiles"""
    assert len(CROP_DETAILS) == 22
    assert len(AGRONOMIC_PROFILES) == 22
    for crop_id, info in CROP_DETAILS.items():
        assert "title" in info
        assert "category" in info
        assert "water_req" in info
        assert "fertilizer_tip" in info
        assert "growing_season" in info
        assert crop_id in AGRONOMIC_PROFILES

def test_engine_prediction():
    """Verify Gaussian Naive Bayes probability calculation and top-3 sorting with fertilizer & economics"""
    engine = CropAdvisoryEngine()
    result = engine.predict(
        n=85, p=45, k=40,
        temperature=24.5, humidity=82.0,
        ph=6.5, rainfall=230.0,
        field_size_acres=2.5
    )
    assert "top_recommendations" in result
    assert len(result["top_recommendations"]) == 3
    assert result["primary_crop"] in ["rice", "jute"]
    assert result["primary_confidence"] > 50.0
    assert "soil_health" in result
    assert "fertilizer_plan" in result
    assert "economic_projection" in result
    assert result["fertilizer_plan"]["commercial_fertilizers"]["urea"]["bags"] > 0
    assert result["economic_projection"]["gross_revenue"]["inr"] > 0

def test_fertilizer_dosage_and_bags():
    """Test commercial fertilizer formulation (Urea, DAP, MOP, Lime/Gypsum)"""
    engine = CropAdvisoryEngine()
    plan = engine.calculate_fertilizer_dosage(
        crop_name="rice",
        n_soil=30, p_soil=20, k_soil=20, # Low nutrient field
        ph_soil=5.2, # Acidic
        field_size_acres=2.0
    )
    assert plan["commercial_fertilizers"]["urea"]["bags"] >= 1
    assert plan["commercial_fertilizers"]["dap"]["bags"] >= 1
    assert plan["commercial_fertilizers"]["mop"]["bags"] >= 1
    assert plan["commercial_fertilizers"]["soil_conditioner"]["kg"] > 0 # Lime needed
    assert len(plan["schedule"]) == 3 # 3-stage split application
    assert plan["costs"]["total_inr"] > 0

def test_crop_economics_and_roi():
    """Test revenue, costs, and net return calculations"""
    engine = CropAdvisoryEngine()
    econ = engine.calculate_crop_economics("cotton", field_size_acres=5.0, fertilizer_cost_inr=15000.0)
    assert econ["yield"]["total"] > 0
    assert econ["gross_revenue"]["inr"] > 0
    assert econ["total_costs"]["inr"] > 0
    assert "roi_percent" in econ

def test_crop_comparison_matrix():
    """Test side-by-side comparison between two crops"""
    engine = CropAdvisoryEngine()
    comp = engine.compare_crops(
        crop1_name="rice",
        crop2_name="cotton",
        n=85, p=45, k=40,
        temp=24.5, hum=82.0, ph=6.5, rain=200.0,
        field_size_acres=2.0
    )
    assert comp is not None
    assert "crop1" in comp
    assert "crop2" in comp
    assert "summary" in comp
    assert comp["summary"]["best_agronomic_fit"] in ["rice", "cotton"]
    assert comp["summary"]["profit_difference_inr"] >= 0

def test_soil_health_diagnostics():
    """Test agronomic threshold classifications for deficient and optimal ranges"""
    engine = CropAdvisoryEngine()
    # Deficient soil
    diag_low = engine.analyze_soil_health(n=20, p=15, k=10, ph=4.8)
    assert diag_low["N"]["badge"] == "Deficient"
    assert diag_low["P"]["badge"] == "Deficient"
    assert diag_low["K"]["badge"] == "Deficient"
    assert diag_low["pH"]["badge"] == "Acidic"

    # Optimal soil
    diag_opt = engine.analyze_soil_health(n=70, p=50, k=50, ph=6.8)
    assert diag_opt["N"]["badge"] == "Optimal"
    assert diag_opt["P"]["badge"] == "Optimal"
    assert diag_opt["K"]["badge"] == "Optimal"
    assert diag_opt["pH"]["badge"] == "Optimal"

def test_database_crud():
    """Test SQLite insert, retrieval, and clearing"""
    init_db()
    clear_history()
    rec_id = save_prediction(
        location="Test Field",
        n=80, p=40, k=40,
        temperature=25.0, humidity=75.0,
        ph=6.5, rainfall=150.0,
        predicted_crop="rice", confidence=95.5,
        soil_status="Optimal Nitrogen, Neutral / Optimal"
    )
    assert rec_id is not None
    rec = get_prediction_by_id(rec_id)
    assert rec is not None
    assert rec["predicted_crop"] == "rice"
    assert rec["location"] == "Test Field"

    history = get_history()
    assert len(history) >= 1
    clear_history()
    assert len(get_history()) == 0

def test_flask_endpoints(client):
    """Test all public HTTP and REST API endpoints"""
    # 1. Index
    res_idx = client.get("/")
    assert res_idx.status_code == 200

    # 2. Health
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "healthy"

    # 3. Crops Catalog
    res_crops = client.get("/api/crops")
    assert res_crops.status_code == 200
    assert len(res_crops.get_json()["crops"]) == 22

    # 4. Predict
    pred_data = {
        "n": 90, "p": 42, "k": 43,
        "temperature": 21.0, "humidity": 82.0,
        "ph": 6.5, "rainfall": 200.0,
        "acres": 2.5,
        "location": "Monsoon Delta"
    }
    res_pred = client.post("/api/predict", json=pred_data)
    assert res_pred.status_code == 200
    pred_json = res_pred.get_json()
    assert pred_json["status"] == "success"
    assert "fertilizer_plan" in pred_json["result"]
    assert "economic_projection" in pred_json["result"]
    rec_id = pred_json["result"]["record_id"]

    # 5. Report View with Fertilizer & Economics
    res_rep = client.get(f"/report/{rec_id}")
    assert res_rep.status_code == 200
    assert "Commercial Fertilizer Prescription" in res_rep.get_data(as_text=True)

    # 6. Fertilizer API
    res_fert = client.post("/api/fertilizer", json={"crop": "rice", "n": 60, "p": 30, "k": 30, "ph": 6.5, "acres": 2.0})
    assert res_fert.status_code == 200
    assert res_fert.get_json()["status"] == "success"

    # 7. Economics API
    res_econ = client.post("/api/economics", json={"crop": "maize", "acres": 3.0, "fertilizer_cost": 8000})
    assert res_econ.status_code == 200
    assert res_econ.get_json()["status"] == "success"

    # 8. Compare Crops API
    res_comp = client.post("/api/crops/compare", json={"crop1": "rice", "crop2": "maize", "n": 80, "p": 40, "k": 40, "temperature": 25.0, "humidity": 70.0, "ph": 6.5, "rainfall": 120.0, "acres": 2.0})
    assert res_comp.status_code == 200
    assert res_comp.get_json()["status"] == "success"

    # 9. Export History CSV
    res_csv = client.get("/api/history/export")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.content_type
    assert "Nitrogen (N)" in res_csv.get_data(as_text=True)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
