import streamlit as st
import pandas as pd
from src.evintel.config import DB_PATH
from src.evintel.pipeline import run_pipeline
from src.evintel.analytics import overview, city_performance, monthly_trend, station_leaderboard, hourly_demand, reliability

st.set_page_config(page_title="EV Intelligence", page_icon="⚡", layout="wide")
st.title("⚡ EV Intelligence")
st.caption("Electric vehicle charging network — operational analytics platform")

if not DB_PATH.exists():
    st.warning("Analytics database not found. Run the ETL pipeline first.")
    if st.button("Run ETL pipeline"):
        with st.spinner("Loading and validating source data..."):
            result = run_pipeline()
        st.success(f"Loaded {result['sessions_loaded']:,} charging sessions.")
        st.rerun()
    st.stop()

with st.sidebar:
    st.header("Controls")
    if st.button("Refresh data pipeline", use_container_width=True):
        with st.spinner("Running ETL..."):
            result = run_pipeline()
        st.success(f"Loaded {result['sessions_loaded']:,} sessions.")
        st.rerun()
    st.markdown("---")
    st.caption("Data: bundled sample dataset")
    st.caption("Storage: SQLite star schema")

m = overview()
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Charging sessions", f"{m['total_sessions']:,}")
c2.metric("Completed", f"{m['completed_sessions']:,}")
c3.metric("Energy delivered", f"{m['total_energy_kwh']:,.0f} kWh")
c4.metric("Revenue", f"₹{m['total_revenue_inr']:,.0f}")
c5.metric("Completion rate", f"{m['completion_rate_pct']}%")

st.divider()
left,right = st.columns(2)
with left:
    st.subheader("Monthly charging demand")
    trend = monthly_trend()
    if not trend.empty:
        st.line_chart(trend.set_index("month")[["sessions"]])
with right:
    st.subheader("Energy delivered by city")
    cities = city_performance()
    if not cities.empty:
        st.bar_chart(cities.set_index("city")[["energy_kwh"]])

st.divider()
left,right = st.columns(2)
with left:
    st.subheader("Charging demand by hour (UTC)")
    hourly = hourly_demand()
    st.area_chart(hourly.set_index("start_hour")[["sessions"]])
with right:
    st.subheader("Operator reliability")
    rel = reliability()
    st.dataframe(rel, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Top charging stations")
stations = station_leaderboard()
st.dataframe(stations, use_container_width=True, hide_index=True)

st.subheader("City performance detail")
st.dataframe(cities, use_container_width=True, hide_index=True)

st.caption("Portfolio demo • Synthetic sample records • INR • Calendar timestamps stored in UTC")
