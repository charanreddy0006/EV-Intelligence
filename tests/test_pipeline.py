import tempfile
from pathlib import Path
import pandas as pd
import pytest
from src.evintel.pipeline import validate, transform, load

def tiny_data():
    return {
        "sessions": pd.DataFrame([{
            "session_id":"S1","station_id":"ST1","vehicle_id":"EV1",
            "started_at":"2025-01-01T08:00:00+00:00","duration_minutes":60,
            "energy_kwh":10.0,"amount_inr":150.0,"session_status":"completed",
            "payment_method":"UPI"}]),
        "stations": pd.DataFrame([{
            "station_id":"ST1","station_name":"Test Station","city":"Hyderabad",
            "operator":"VoltWay","connector_type":"CCS2","charger_power_kw":50,
            "latitude":17.4,"longitude":78.4,"commissioned_date":"2023-01-01"}]),
        "vehicles": pd.DataFrame([{
            "vehicle_id":"EV1","vehicle_model":"Test EV",
            "battery_capacity_kwh":40,"vehicle_segment":"Mid-range"}])
    }

def test_validate_accepts_valid_data():
    validate(tiny_data())

def test_validate_rejects_negative_energy():
    data = tiny_data()
    data["sessions"].loc[0, "energy_kwh"] = -1
    with pytest.raises(ValueError):
        validate(data)

def test_transform_adds_calendar_fields():
    result = transform(tiny_data())
    assert result["sessions"].loc[0, "session_date"] == "2025-01-01"
    assert result["sessions"].loc[0, "start_hour"] == 8

def test_load_creates_star_schema():
    data = transform(tiny_data())
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        load(data, db)
        import sqlite3
        with sqlite3.connect(db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM fact_charging_sessions").fetchone()[0]
        assert count == 1
