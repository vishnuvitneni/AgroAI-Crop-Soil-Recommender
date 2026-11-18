# 🌾 AgroAI - Smart Crop Recommendation & Soil Health Analyzer
### *With Real-Time Location, Live Weather & Agricultural Advisory Reports*

An end-to-end Machine Learning and Full-Stack web application that predicts the most suitable crops for cultivation based on soil chemical parameters, real-time live weather, and climate indicators, complete with an agronomic soil health diagnostic engine and field care advice.

---

## 🌟 Key Features

- **High-Accuracy ML Model**: Benchmarked across multiple algorithms; the **Gaussian Naive Bayes** model achieves **99.32% test accuracy** on 22 distinct crop categories.
- **22 Supported Crops**: Rice, Maize, Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, and Coffee.
- **🌍 Real-Time Location & Live Weather Integration**:
  - Type in any city in the world (e.g. *Hyderabad, Mumbai, Nairobi, London, Fresno, Delhi, Bengaluru*) or click **"📍 GPS"** to auto-detect your location.
  - Automatically fetches live Temperature, Relative Humidity, Weather condition (Clear, Cloudy, Rainy, Thunderstorm), and estimated monthly precipitation.
  - One-click **"⚡ Auto-Fill Weather"** applies real-time climate data directly to the ML model!
- **Top-3 Probability Rankings**: Generates softmax confidence percentages for the primary crop and top compatible alternatives.
- **Soil Health Diagnostics**: Color-coded diagnosis for Nitrogen, Phosphorus, Potassium (N-P-K), and Soil pH (Acidic, Neutral, Alkaline) with actionable fertilizer and soil conditioning advice.
- **📜 SQLite History & Official Reports**:
  - Automatically logs every field test to an SQLite database (`data/agroai_history.db`).
  - View previous tests in the history table and click **"View / Print Official Report"** to print or save a PDF diagnosis!
- **Field Presets**: Instant 1-click presets for common farming environments (Monsoon Wetlands, High-altitude Orchards, Semi-Arid Cotton Belts, Winter Pulses).
- **RESTful API**: Clean `/api/predict`, `/api/weather/city`, `/api/weather/coords`, and `/api/history` endpoints.

---

## 🏗️ Project Architecture

```
ML project/
│
├── data/
│   ├── Crop_recommendation.csv      # Standard benchmark dataset (2,200 rows)
│   └── agroai_history.db            # SQLite database storing user tests and predictions
│
├── models/
│   └── trained_model.json           # Serialized model parameters, weights & metadata
│
├── src/
│   ├── train.py                     # ML pipeline: data loading, splitting, training, benchmarking
│   ├── recommend.py                 # Prediction, probability distribution & soil health engine
│   ├── weather_service.py           # Real-time weather & geocoding via Open-Meteo
│   └── database.py                  # SQLite database persistence layer
│
├── templates/
│   ├── index.html                   # Interactive full-stack web UI with weather, sliders & history
│   └── report.html                  # Official printable farmer diagnostic report
│
├── app.py                           # Flask backend and REST API server
└── README.md                        # Documentation
```

---

## 🔬 Model Performance & Benchmarks

The models were evaluated using an 80/20 stratified train/test split on 2,200 samples:

| Algorithm | Test Accuracy | Status |
| :--- | :---: | :---: |
| **Gaussian Naive Bayes** | **99.32%** | 🏆 **Champion Model** |
| **K-Nearest Neighbors (k=5)** | **97.95%** | Benchmark |
| **K-Nearest Neighbors (k=3)** | **97.50%** | Benchmark |

---

## 🚀 How to Run the Web Application

To launch the full-stack interactive dashboard, open your terminal in this directory and run:

```powershell
python app.py
```

Then open your browser at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📡 REST API Usage

### 1. Fetch Live Weather by City:
**Endpoint:** `GET /api/weather/city?q=Hyderabad`

### 2. Predict Suitable Crop & Save History:
**Endpoint:** `POST /api/predict`
```json
{
  "n": 85,
  "p": 45,
  "k": 40,
  "temperature": 28.5,
  "humidity": 60.0,
  "ph": 6.5,
  "rainfall": 150.0,
  "location": "Hyderabad, Telangana, India"
}
```

### 3. Retrieve Test History:
**Endpoint:** `GET /api/history`
