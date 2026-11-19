"""
Comprehensive Test Suite for AgroAI Crop Recommender & Soil Health Analyzer
Verifies ML pipeline, database persistence, weather service, and Flask REST endpoints.
"""
import os
import json
import pytest
from app import app
from src.recommend import CropAdvisoryEngine, CROP_DETAILS
from src.database import init_db, save_prediction, get_history, get_prediction_by_id, clear_history
from src.weather_service import get_weather_by_city, get_weather_by_coords

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_crop_catalog_completeness():
    """Ensure all 22 crop categories are present in knowledge base"""
    assert len(CROP_DETAILS) == 22
    for crop_id, info in CROP_DETAILS.items():
        assert "title" in info
        assert "category" in info
        assert "water_req" in info
        assert "fertilizer_tip" in info
        assert "growing_season" in info

def test_engine_prediction():
    """Verify Gaussian Naive Bayes probability calculation and top-3 sorting"""
    engine = CropAdvisoryEngine()
    result = engine.predict(
        n=85, p=45, k=40,
        temperature=24.5, humidity=82.0,
        ph=6.5, rainfall=230.0
    )
    assert "top_recommendations" in result
    assert len(result["top_recommendations"]) == 3
    assert result["primary_crop"] in ["rice", "jute"]
    assert result["primary_confidence"] > 50.0
    assert "soil_health" in result
    assert "N" in result["soil_health"]
    assert "P" in result["soil_health"]
    assert "K" in result["soil_health"]
    assert "pH" in result["soil_health"]

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

def test_crop_compatibility_analysis():
    """Test feature gap computation for specific crops"""
    engine = CropAdvisoryEngine()
    compat = engine.analyze_crop_compatibility("rice", 85, 45, 40, 24.5, 82.0, 6.5, 230.0)
    assert compat is not None
    assert compat["compatibility_score"] >= 80.0
    assert "gaps" in compat

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
        "location": "Monsoon Delta"
    }
    res_pred = client.post("/api/predict", json=pred_data)
    assert res_pred.status_code == 200
    pred_json = res_pred.get_json()
    assert pred_json["status"] == "success"
    rec_id = pred_json["result"]["record_id"]

    # 5. Report View
    res_rep = client.get(f"/report/{rec_id}")
    assert res_rep.status_code == 200

    # 6. Presets
    res_presets = client.get("/api/presets")
    assert res_presets.status_code == 200
    assert "monsoon_rice" in res_presets.get_json()["presets"]

    # 7. Model Info
    res_info = client.get("/api/model-info")
    assert res_info.status_code == 200
    assert "metadata" in res_info.get_json()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
