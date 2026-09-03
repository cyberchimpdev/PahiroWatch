from typing import Dict, Any
from backend.app.providers.base import BaseTerrainProvider

class TerrainProvider(BaseTerrainProvider):
    """
    Topographic & Digital Elevation Model (DEM) Provider.
    Inspired by terrain slope and curvature analysis from landslides_detection reference.
    """
    def __init__(self, mode: str = "DEMO"):
        self.mode = mode

    def get_terrain_risk(
        self, 
        latitude: float, 
        longitude: float, 
        baseline_slope: float = 38.5, 
        elevation: float = 340.0
    ) -> Dict[str, Any]:
        
        # Calculate physical terrain risk component based on slope angle
        if baseline_slope > 40.0:
            hazard_level = "CRITICAL"
            terrain_risk_score = 92.0
            lithology = "Steep fractured rockface with joint dipping toward highway"
        elif baseline_slope >= 30.0:
            hazard_level = "HIGH"
            terrain_risk_score = 78.0
            lithology = "Colluvial mantle on weathered phyllite slope"
        elif baseline_slope >= 20.0:
            hazard_level = "MODERATE"
            terrain_risk_score = 48.0
            lithology = "Semi-stabilized terrace deposits"
        else:
            hazard_level = "LOW"
            terrain_risk_score = 18.0
            lithology = "Alluvial valley floor"

        return {
            "elevation_m": elevation,
            "slope_deg": round(baseline_slope, 1),
            "aspect_cardinal": "South-West (SW)",
            "terrain_risk_score": terrain_risk_score,
            "hazard_level": hazard_level,
            "geological_context": lithology,
            "source": "SRTM 30m / ALOS Global Digital Surface Model [DEMO PROVIDER]",
            "resolution": "30-meter spatial grid",
            "is_synthetic": True,
            "disclaimer": "DEM values pre-calculated from SRTM v3 topographical profile for Narayanghat-Mugling sector"
        }
