# 🌾 AgroAI - Farmer Decision Support & Smart Agriculture Platform

An end-to-end Machine Learning and Full-Stack web application designed to solve real-world farmer challenges: precision crop recommendation, reliable village-level weather forecasts, live Mandi commodity prices, nearby fertilizer shop discovery, and interactive agronomic calculators.

---

## 🌟 Key Subsystems & Features

### 1. 🌦️ Village-Level Live Weather & 5-Day Agricultural Forecast
- **Dual-Tier Geocoding**: Combines Open-Meteo with OpenStreetMap Nominatim so **any small village, gram panchayat, mandal, or town** (e.g. *Mudivedu, Madanapalle, Chittoor, Guntur, Khanna*) resolves seamlessly.
- **5-Day Agricultural Weather Outlook**: Day-by-day temperatures, rainfall precipitation (mm), and actionable farming advice (e.g. *"Rain expected; avoid spraying pesticides today"*).
- **Auto-Fill Weather**: One-click transfer of real-time temperature, humidity, and rainfall into the ML model.

### 2. 📈 Live Mandi & Vegetable Market Rates
- **Daily APMC Market Rates**: Covers 20+ major commodities across Vegetables (*Tomato, Onion, Potato, Chilli, Ginger, Garlic, Cabbage*), Cereals (*Paddy, Wheat, Maize, Bajra*), Pulses (*Chana, Tur/Arhar, Urad, Moong*), and Cash Crops (*Cotton, Soybean, Mustard, Groundnut*).
- **Price Analytics**: Modal price (₹/Quintal and ₹/kg), daily Min-Max range, price trends (📈 Rising, 📉 Falling, ⚖️ Stable), MSP indicators, and primary trading mandis.

### 3. 🏪 Nearby Fertilizer & Agri-Input Shops Discovery
- **Certified Dealer Directory**: Locates nearby IFFCO Kisan Seva Kendras, Coromandel Gromor Centers, seed stores, and Krishi Vigyan Kendras (KVK).
- **Direct Google Maps Navigation**: One-click **"📍 Open All Fertilizer Shops in Google Maps"** directly directs farmers to input dealers in their area.
- **Inventory & Contact Details**: Verified mobile numbers, store operating hours, and stocked products (Urea, DAP, MOP, Bio-fertilizers, Hybrid Seeds).

### 4. 🧮 Fertilizer Dosage Calculator & Plant Doctor
- **Commercial Fertilizer Bag Calculator**: Select crop (Rice, Wheat, Maize, Cotton, Tomato, etc.) and land size (Acres or Hectares) to calculate the exact number of **Urea (45kg bags)**, **DAP (50kg bags)**, and **MOP (50kg bags)** needed, with basal and top-dressing split schedules.
- **Crop Pest & Disease Doctor**: Instant visual symptom diagnostic engine (e.g. Leaf Blast, Stem Borer, Leaf Curl, Powdery Mildew, Root Rot) with both organic and chemical control remedies.
- **Direct Kisan Helplines**: One-touch access to Kisan Call Centre (Toll-Free `1800-180-1551`), PM-Kisan DBT support, and Crop Insurance assistance.

---

## 🚀 How to Run Locally

```powershell
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 📡 Live Cloud Deployment (Render.com)

Push the latest commits to GitHub:
```powershell
git push origin main
```
Render automatically triggers continuous deployment and hosts the application with public SSL.
