-- Create view: active_floats_summary
-- Aggregates temperature and salinity by basin for recently active profiles.

CREATE OR REPLACE VIEW active_floats_summary AS
SELECT
  CASE
    WHEN p.lat IS NULL OR p.lon IS NULL THEN 'unknown'
    WHEN p.lat >= 60 THEN 'arctic'
    WHEN p.lat <= -50 THEN 'southern_ocean'
    WHEN p.lon BETWEEN -70 AND 20 AND p.lat >= 0 THEN 'north_atlantic'
    WHEN p.lon BETWEEN -70 AND 20 AND p.lat < 0 THEN 'south_atlantic'
    WHEN p.lon BETWEEN 20 AND 150 THEN 'indian'
    WHEN p.lon >= 150 OR p.lon <= -70 THEN
      CASE WHEN p.lat >= 0 THEN 'north_pacific' ELSE 'south_pacific' END
    ELSE 'other'
  END AS basin,
  COUNT(DISTINCT p.float_id) AS active_float_count,
  COUNT(m.id) AS measurement_count,
  AVG(m.temperature) AS avg_temperature,
  AVG(m.salinity) AS avg_salinity,
  MAX(p.profile_date) AS last_profile_date
FROM profiles p
JOIN measurements m ON m.profile_id = p.profile_id
WHERE p.profile_date >= (CURRENT_DATE - INTERVAL '7 days')
GROUP BY basin;
