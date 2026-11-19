import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from app import app

def test_app():
    client = app.test_client()

    print("1. Testing GET / ...")
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Kisan AI Copilot" in html, "Chatbot missing in HTML"
    assert "tab-seasons" in html, "Seasonal tab missing in HTML"
    assert "Land Area, Yield & Net Farm Profit Estimator" in html, "Profit estimator missing in HTML"
    assert "Error of place" in html, "Error of place modal missing in HTML"
    print("✓ GET / is 200 OK and all UI elements are rendered")

    print("\n2. Testing POST /api/chat ...")
    resp = client.post(
        "/api/chat",
        data=json.dumps({"message": "What is the best crop for kharif season with black soil?"}),
        content_type="application/json"
    )
    assert resp.status_code == 200
    res = json.loads(resp.data.decode("utf-8"))
    assert res["status"] == "success"
    print("✓ Chat API replied successfully:")
    print(" ", res["reply"][:150].replace("\n", " "), "...")

    print("\n3. Testing POST /api/profit-estimator ...")
    resp = client.post(
        "/api/profit-estimator",
        data=json.dumps({"crop": "cotton", "land_size": 2.5, "unit": "acre"}),
        content_type="application/json"
    )
    assert resp.status_code == 200
    res = json.loads(resp.data.decode("utf-8"))
    assert res["status"] == "success"
    b = res["budget"]
    print("✓ Profit Estimator replied successfully:")
    print(f"  Crop: {b['crop_name']} | Land: 2.5 Acres")
    print(f"  Expected Yield: {b['expected_yield_quintals']} Qtl | Cultivation Cost: Rs. {b['cultivation_cost_inr']}")
    print(f"  Gross Revenue: Rs. {b['gross_revenue_inr']} | Net Profit: Rs. {b['estimated_net_profit_inr']} ({b['roi_percentage']}% ROI)")

    print("\n4. Testing GET /api/seasons ...")
    resp = client.get("/api/seasons")
    assert resp.status_code == 200
    res = json.loads(resp.data.decode("utf-8"))
    assert res["status"] == "success"
    print(f"✓ Seasons API returned {len(res['seasons'])} cropping seasons: {list(res['seasons'].keys())}")

    print("\n5. Testing GET /api/market-rates ...")
    resp = client.get("/api/market-rates")
    assert resp.status_code == 200
    res = json.loads(resp.data.decode("utf-8"))
    assert res["status"] == "success"
    print(f"✓ Market rates returned {len(res['rates'])} commodities with live prices")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")

if __name__ == "__main__":
    test_app()
