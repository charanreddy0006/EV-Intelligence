"""Reusable SQL-backed metrics for the dashboard and CLI."""
import sqlite3
import pandas as pd
from .config import DB_PATH

def query(sql: str, db_path=DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn)

def overview(db_path=DB_PATH):
    return query("""
    SELECT COUNT(*) AS total_sessions,
           SUM(CASE WHEN session_status='completed' THEN 1 ELSE 0 END) AS completed_sessions,
           ROUND(SUM(energy_kwh),2) AS total_energy_kwh,
           ROUND(SUM(amount_inr),2) AS total_revenue_inr,
           ROUND(AVG(CASE WHEN session_status='completed' THEN duration_minutes END),1) AS avg_duration_min,
           ROUND(100.0 * SUM(CASE WHEN session_status='completed' THEN 1 ELSE 0 END)/COUNT(*),2) AS completion_rate_pct
    FROM fact_charging_sessions
    """, db_path).iloc[0].to_dict()

def city_performance(db_path=DB_PATH):
    return query("""
    SELECT st.city, COUNT(*) AS sessions,
           ROUND(SUM(fs.energy_kwh),1) AS energy_kwh,
           ROUND(SUM(fs.amount_inr),0) AS revenue_inr,
           ROUND(AVG(fs.energy_kwh),1) AS avg_energy_per_session
    FROM fact_charging_sessions fs JOIN dim_stations st USING(station_id)
    GROUP BY st.city ORDER BY energy_kwh DESC
    """, db_path)

def monthly_trend(db_path=DB_PATH):
    return query("""
    SELECT month, COUNT(*) AS sessions, ROUND(SUM(energy_kwh),1) AS energy_kwh,
           ROUND(SUM(amount_inr),0) AS revenue_inr
    FROM fact_charging_sessions
    GROUP BY month ORDER BY month
    """, db_path)

def station_leaderboard(db_path=DB_PATH):
    return query("""
    SELECT st.station_name, st.city, st.operator, st.charger_power_kw,
           COUNT(*) AS sessions, ROUND(SUM(fs.energy_kwh),1) AS energy_kwh,
           ROUND(SUM(fs.amount_inr),0) AS revenue_inr
    FROM fact_charging_sessions fs JOIN dim_stations st USING(station_id)
    GROUP BY st.station_id ORDER BY sessions DESC LIMIT 15
    """, db_path)

def hourly_demand(db_path=DB_PATH):
    return query("""
    SELECT start_hour, COUNT(*) AS sessions, ROUND(SUM(energy_kwh),1) AS energy_kwh
    FROM fact_charging_sessions GROUP BY start_hour ORDER BY start_hour
    """, db_path)

def reliability(db_path=DB_PATH):
    return query("""
    SELECT st.operator, COUNT(*) AS total_sessions,
           SUM(CASE WHEN fs.session_status='completed' THEN 1 ELSE 0 END) AS completed,
           ROUND(100.0*SUM(CASE WHEN fs.session_status='completed' THEN 1 ELSE 0 END)/COUNT(*),2) AS success_rate_pct
    FROM fact_charging_sessions fs JOIN dim_stations st USING(station_id)
    GROUP BY st.operator ORDER BY success_rate_pct DESC
    """, db_path)
