"""
SQLite Database Layer for AgroAI
Stores past soil analysis queries, locations, weather, and recommendations.
"""
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("data", "agroai_history.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT,
            n REAL,
            p REAL,
            k REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT NOT NULL,
            confidence REAL NOT NULL,
            soil_status TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(location, n, p, k, temperature, humidity, ph, rainfall, predicted_crop, confidence, soil_status):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO predictions (timestamp, location, n, p, k, temperature, humidity, ph, rainfall, predicted_crop, confidence, soil_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ts, location or "Custom Field", n, p, k, temperature, humidity, ph, rainfall, predicted_crop, confidence, soil_status))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_history(limit=25):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM predictions ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_prediction_by_id(pred_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def clear_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
