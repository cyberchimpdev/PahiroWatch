from typing import Dict, Any, List, Tuple

class ConfidenceEngine:
    """
    Honest Confidence Assessment Engine.
    Penalizes missing data, stale telemetry, sensor timeouts, and contradictory evidence.
    Ensures the system never reports unwarranted high confidence during bad days or sparse coverage.
    """

    @staticmethod
    def assess_confidence(
        weather_obs: Dict[str, Any],
        terrain_obs: Dict[str, Any],
        satellite_obs: Dict[str, Any] = None,
        exposure_obs: Dict[str, Any] = None,
        memory_obs: Dict[str, Any] = None,
        is_satellite_missing: bool = False,
        is_weather_stale: bool = False
    ) -> Tuple[float, str, List[str], str]:
        
        base_confidence = 0.90
        missing_data = []
        reasons = []
        contradictory = None

        # 1. Weather Data Check
        if not weather_obs or weather_obs.get("is_stale", False) or is_weather_stale:
            base_confidence -= 0.18
            missing_data.append("WEATHER_REALTIME")
            freshness = weather_obs.get("freshness_minutes", 0) // 60 if weather_obs else "Unknown"
            reasons.append(f"Rainfall data is stale ({freshness}h old) — precipitation trend unverified.")
        else:
            reasons.append("Rainfall telemetry is recent and verified.")

        # 2. Terrain Data Check
        if not terrain_obs:
            base_confidence -= 0.15
            missing_data.append("TERRAIN_DEM")
            reasons.append("DEM slope elevation unavailable.")
        else:
            reasons.append("High-resolution DEM slope verified.")

        # 3. Satellite Data Check
        if is_satellite_missing or not satellite_obs or "surface_change_indicator" not in satellite_obs:
            base_confidence -= 0.22
            missing_data.append("SATELLITE_OPTICAL")
            reasons.append("Satellite optical confirmation is unavailable due to provider timeout or blackout.")
        elif satellite_obs.get("cloud_cover_pct", 0) > 70.0:
            base_confidence -= 0.15
            missing_data.append("SATELLITE_CLOUD_CONTAMINATED")
            reasons.append(f"Satellite imagery degraded by monsoon cloud cover ({satellite_obs.get('cloud_cover_pct')}%) — partial occlusion.")
        else:
            reasons.append("Satellite multispectral difference verified.")

        # 4. Exposure Data Check
        if not exposure_obs:
            base_confidence -= 0.08
            missing_data.append("ROAD_EXPOSURE")
        
        # 5. Check Contradictory Evidence (e.g., Extreme Rain + Flat Slope, or Extreme Rain + Zero Satellite Change with clear sky)
        r24 = weather_obs.get("rainfall_24h_mm", 0.0) if weather_obs else 0.0
        slope = terrain_obs.get("slope_deg", 0.0) if terrain_obs else 0.0
        sat_change = satellite_obs.get("change_score", 0.0) if satellite_obs else None
        sat_clouds = satellite_obs.get("cloud_cover_pct", 100.0) if satellite_obs else 100.0

        contradictory_notes = []
        if r24 > 140.0 and slope < 15.0:
            base_confidence -= 0.12
            contradictory_notes.append("Severe rainfall recorded, but slope angle is gentle (<15°). Landslide mass failure unlikely despite water saturation; possible localized flooding rather than slope shear.")
            reasons.append("Contradiction: high rainfall on low slope gradient.")

        if r24 > 140.0 and sat_change is not None and sat_change < 0.10 and sat_clouds < 25.0:
            base_confidence -= 0.10
            contradictory_notes.append("Cloud-free satellite imagery reveals negligible canopy disturbance (<0.10) despite reported cloudburst. Ground movement may be subterranean or delayed.")
            reasons.append("Contradiction: high rainfall without visible optical surface change.")

        contradictory = " | ".join(contradictory_notes) if contradictory_notes else None
        final_confidence = round(max(0.20, min(0.95, base_confidence)), 2)
        confidence_reason = " ".join(reasons)

        return final_confidence, confidence_reason, missing_data, contradictory
