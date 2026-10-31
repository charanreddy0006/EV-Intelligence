"""Extract, validate, transform and load EV charging data into SQLite."""
from __future__ import annotations
import logging
import sqlite3
from pathlib import Path
import pandas as pd
from .config import RAW_DIR, DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("evintel")

REQUIRED = {
    "sessions": {"session_id", "station_id", "vehicle_id", "started_at", "duration_minutes",
                 "energy_kwh", "amount_inr", "session_status", "payment_method"},
    "stations": {"station_id", "station_name", "city", "operator", "connector_type",
                 "charger_power_kw", "latitude", "longitude", "commissioned_date"},
    "vehicles": {"vehicle_id", "vehicle_model", "battery_capacity_kwh", "vehicle_segment"},
}

def extract(raw_dir: Path = RAW_DIR):
    """Read source CSV files."""
    log.info("Extracting raw CSV files")
    data = {
        "sessions": pd.read_csv(raw_dir / "charging_sessions.csv"),
        "stations": pd.read_csv(raw_dir / "stations.csv"),
        "vehicles": pd.read_csv(raw_dir / "vehicles.csv"),
    }
    return data

def validate(data: dict) -> None:
    """Fail fast when required columns, keys or numeric values are invalid."""
    for name, required in REQUIRED.items():
        missing = required - set(data[name].columns)
        if missing:
            raise ValueError(f"{name}: missing required columns: {sorted(missing)}")
    for name, key in [("sessions", "session_id"), ("stations", "station_id"), ("vehicles", "vehicle_id")]:
        if data[name][key].isna().any() or data[name][key].duplicated().any():
            raise ValueError(f"{name}: {key} must be non-null and unique")
    s = data["sessions"]
    if (s["energy_kwh"] < 0).any() or (s["duration_minutes"] <= 0).any() or (s["amount_inr"] < 0).any():
        raise ValueError("Sessions contain invalid negative/zero measures")
    if not set(s["session_status"]).issubset({"completed", "failed", "interrupted"}):
        raise ValueError("Unexpected session_status value")
    if not set(s["station_id"]).issubset(set(data["stations"]["station_id"])):
        raise ValueError("Charging session references an unknown station")
    if not set(s["vehicle_id"]).issubset(set(data["vehicles"]["vehicle_id"])):
        raise ValueError("Charging session references an unknown vehicle")

def transform(data: dict) -> dict:
    """Normalize timestamps, derive calendar fields and retain auditable records."""
    sessions = data["sessions"].copy()
    sessions["started_at"] = pd.to_datetime(sessions["started_at"], utc=True, errors="coerce")
    if sessions["started_at"].isna().any():
        raise ValueError("Invalid started_at timestamp")
    sessions["session_date"] = sessions["started_at"].dt.date.astype(str)
    sessions["start_hour"] = sessions["started_at"].dt.hour
    sessions["month"] = sessions["started_at"].dt.to_period("M").astype(str)
    sessions["energy_kwh"] = sessions["energy_kwh"].round(3)
    sessions["amount_inr"] = sessions["amount_inr"].round(2)
    sessions["duration_minutes"] = sessions["duration_minutes"].round(1)
    return {"sessions": sessions, "stations": data["stations"], "vehicles": data["vehicles"]}

def load(data: dict, db_path: Path = DB_PATH) -> None:
    """Load dimensions and fact table into a local SQLite analytics database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript("""
        DROP TABLE IF EXISTS fact_charging_sessions;
        DROP TABLE IF EXISTS dim_stations;
        DROP TABLE IF EXISTS dim_vehicles;
        CREATE TABLE dim_stations (
            station_id TEXT PRIMARY KEY, station_name TEXT NOT NULL, city TEXT NOT NULL,
            operator TEXT NOT NULL, connector_type TEXT NOT NULL, charger_power_kw REAL NOT NULL,
            latitude REAL, longitude REAL, commissioned_date TEXT
        );
        CREATE TABLE dim_vehicles (
            vehicle_id TEXT PRIMARY KEY, vehicle_model TEXT NOT NULL,
            battery_capacity_kwh REAL NOT NULL, vehicle_segment TEXT NOT NULL
        );
        CREATE TABLE fact_charging_sessions (
            session_id TEXT PRIMARY KEY,
            station_id TEXT NOT NULL REFERENCES dim_stations(station_id),
            vehicle_id TEXT NOT NULL REFERENCES dim_vehicles(vehicle_id),
            started_at TEXT NOT NULL, session_date TEXT NOT NULL, start_hour INTEGER NOT NULL,
            month TEXT NOT NULL, duration_minutes REAL NOT NULL, energy_kwh REAL NOT NULL,
            amount_inr REAL NOT NULL, session_status TEXT NOT NULL, payment_method TEXT NOT NULL
        );
        CREATE INDEX idx_fact_date ON fact_charging_sessions(session_date);
        CREATE INDEX idx_fact_station ON fact_charging_sessions(station_id);
        CREATE INDEX idx_fact_status ON fact_charging_sessions(session_status);
        """)
        data["stations"].to_sql("dim_stations", conn, if_exists="append", index=False)
        data["vehicles"].to_sql("dim_vehicles", conn, if_exists="append", index=False)
        data["sessions"].to_sql("fact_charging_sessions", conn, if_exists="append", index=False)
    log.info("Loaded %s sessions into %s", len(data["sessions"]), db_path)

def run_pipeline(raw_dir: Path = RAW_DIR, db_path: Path = DB_PATH) -> dict:
    data = extract(raw_dir)
    validate(data)
    clean = transform(data)
    load(clean, db_path)
    return {"sessions_loaded": len(clean["sessions"]), "stations_loaded": len(clean["stations"]),
            "vehicles_loaded": len(clean["vehicles"]), "database": str(db_path)}

if __name__ == "__main__":
    print(run_pipeline())
