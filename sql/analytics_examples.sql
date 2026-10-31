-- EV Intelligence: standalone SQL practice queries (SQLite syntax)

-- 1. Energy and revenue by city
SELECT s.city, ROUND(SUM(f.energy_kwh), 2) AS energy_kwh,
       ROUND(SUM(f.amount_inr), 2) AS revenue_inr
FROM fact_charging_sessions f
JOIN dim_stations s USING (station_id)
GROUP BY s.city
ORDER BY energy_kwh DESC;

-- 2. Rank stations by delivered energy
SELECT station_name, city, energy_kwh,
       DENSE_RANK() OVER (ORDER BY energy_kwh DESC) AS energy_rank
FROM (
    SELECT s.station_name, s.city, SUM(f.energy_kwh) AS energy_kwh
    FROM fact_charging_sessions f
    JOIN dim_stations s USING (station_id)
    GROUP BY s.station_id
);

-- 3. Session success rate by operator
SELECT s.operator, COUNT(*) AS total_sessions,
       SUM(CASE WHEN f.session_status='completed' THEN 1 ELSE 0 END) AS completed,
       ROUND(100.0 * SUM(CASE WHEN f.session_status='completed' THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS success_rate_pct
FROM fact_charging_sessions f
JOIN dim_stations s USING (station_id)
GROUP BY s.operator;

-- 4. Peak charging hour
SELECT start_hour, COUNT(*) AS session_count
FROM fact_charging_sessions
GROUP BY start_hour
ORDER BY session_count DESC
LIMIT 5;
