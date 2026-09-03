from typing import Dict, Any, Tuple

class RiskCalculator:
    """
    Deterministic Evidence Aggregator & Risk Engine.
    Combines physical environmental metrics into a normalized 0-100 hazard index.
    The LLM interprets this quantitative evidence rather than hallucinating raw numbers.
    """

    @staticmethod
    def calculate_risk(
        weather_obs: Dict[str, Any],
        terrain_obs: Dict[str, Any],
        satellite_obs: Dict[str, Any] = None,
        exposure_obs: Dict[str, Any] = None,
        memory_obs: Dict[str, Any] = None
    ) -> Tuple[float, str, Dict[str, float]]:
        
        # 1. Rainfall Component (Weight: 35%)
        # Based on Nepal DHM monsoon trigger curves (>140mm in 24h is severe)
        r24 = weather_obs.get("rainfall_24h_mm", 0.0) if weather_obs else 0.0
        if r24 >= 160.0:
            rain_comp = 35.0
        elif r24 >= 120.0:
            rain_comp = 28.0 + (r24 - 120.0) / 40.0 * 7.0
        elif r24 >= 80.0:
            rain_comp = 18.0 + (r24 - 80.0) / 40.0 * 10.0
        elif r24 >= 40.0:
            rain_comp = 8.0 + (r24 - 40.0) / 40.0 * 10.0
        else:
            rain_comp = (r24 / 40.0) * 8.0

        # 2. Terrain / Slope Component (Weight: 25%)
        # In Himalayan geology, slope > 35 degrees has critical shear stress failure potential
        slope = terrain_obs.get("slope_deg", 25.0) if terrain_obs else 25.0
        if slope >= 40.0:
            terrain_comp = 25.0
        elif slope >= 32.0:
            terrain_comp = 18.0 + (slope - 32.0) / 8.0 * 7.0
        elif slope >= 22.0:
            terrain_comp = 10.0 + (slope - 22.0) / 10.0 * 8.0
        else:
            terrain_comp = max(2.0, (slope / 22.0) * 10.0)

        # 3. Satellite Spectral Change Component (Weight: 15%)
        if satellite_obs and "change_score" in satellite_obs:
            c_score = satellite_obs.get("change_score", 0.0)
            # If clouds block visibility, satellite cannot contribute full weight
            if satellite_obs.get("cloud_cover_pct", 0) > 75.0:
                sat_comp = 5.0 # default baseline for unverified
            else:
                sat_comp = min(15.0, c_score * 15.0)
        else:
            # Missing satellite: fallback assigns conservative baseline (5.0)
            sat_comp = 5.0

        # 4. Road & Population Exposure Component (Weight: 15%)
        if exposure_obs:
            exp_raw = exposure_obs.get("exposure_score", 50.0)
            exp_comp = (exp_raw / 100.0) * 15.0
        else:
            exp_comp = 7.5

        # 5. Historical Memory Component (Weight: 10%)
        if memory_obs:
            multiplier = memory_obs.get("history_multiplier", 1.0)
            has_unresolved = memory_obs.get("has_unresolved_incidents", False)
            events = memory_obs.get("total_historical_events", 0)
            
            base_hist = 5.0
            if has_unresolved:
                base_hist = 10.0
            elif events >= 2:
                base_hist = 8.0
            elif events >= 1:
                base_hist = 6.0
            hist_comp = min(10.0, base_hist * multiplier)
        else:
            hist_comp = 5.0

        # Total Aggregated Raw Score (0 to 100)
        total_score = rain_comp + terrain_comp + sat_comp + exp_comp + hist_comp
        total_score = max(0.0, min(100.0, round(total_score, 1)))

        # Standard Classification
        if total_score >= 80.0:
            level = "CRITICAL"
        elif total_score >= 60.0:
            level = "HIGH"
        elif total_score >= 30.0:
            level = "MODERATE"
        else:
            level = "LOW"

        breakdown = {
            "rainfall_component": round(rain_comp, 1),
            "terrain_component": round(terrain_comp, 1),
            "satellite_component": round(sat_comp, 1),
            "exposure_component": round(exp_comp, 1),
            "history_component": round(hist_comp, 1),
            "total_score": total_score
        }

        return total_score, level, breakdown
