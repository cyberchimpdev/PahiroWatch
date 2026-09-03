"""
Nepal Landslide Risk Agent Toolkit — Minimal Reference Risk Aggregator
"""

from typing import Dict, Any, Tuple

def calculate_simple_risk(
    rainfall_24h_mm: float,
    slope_deg: float,
    satellite_change: float = 0.0,
    road_distance_m: float = 100.0,
    cloud_cover_pct: float = 20.0
) -> Tuple[float, str]:
    """
    Computes baseline 0-100 landslide hazard index for Himalayan mountain slopes.
    """
    # 1. Rain Component (35 max)
    rain_c = min(35.0, (rainfall_24h_mm / 160.0) * 35.0)
    
    # 2. Slope Component (30 max)
    slope_c = min(30.0, (slope_deg / 45.0) * 30.0)
    
    # 3. Satellite Change Component (15 max)
    if cloud_cover_pct > 70.0:
        sat_c = 5.0
    else:
        sat_c = min(15.0, satellite_change * 15.0)
        
    # 4. Road Proximity Component (20 max)
    if road_distance_m < 50.0:
        exp_c = 20.0
    elif road_distance_m < 200.0:
        exp_c = 14.0
    else:
        exp_c = 6.0

    total = round(rain_c + slope_c + sat_c + exp_c, 1)
    
    if total >= 80.0:
        level = "CRITICAL"
    elif total >= 60.0:
        level = "HIGH"
    elif total >= 30.0:
        level = "MODERATE"
    else:
        level = "LOW"
        
    return total, level
