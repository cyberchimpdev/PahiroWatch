from typing import Dict, Any, List
from app.providers.base import BaseExposureProvider

class ExposureProvider(BaseExposureProvider):
    """
    Infrastructure and Population Exposure Provider.
    Calculates vulnerability based on OpenStreetMap highway geometry, bridge proximity, settlements, and facilities.
    """
    def __init__(self, mode: str = "DEMO"):
        self.mode = mode

    def get_road_exposure(
        self, 
        latitude: float, 
        longitude: float, 
        location_name: str = "Jalbire Sector"
    ) -> Dict[str, Any]:
        
        if "Kurintar" in location_name or "Mugling" in location_name:
            nearest_road = "Prithvi / Narayanghat Highway Junction (NH04 / NH05)"
            road_class = "Trunk / Primary National Lifeline Highway"
            distance_to_road_m = 45.0
            settlements_nearby = ["Kurintar Ward 4", "Mugling Bazaar (approx. 4,200 residents)"]
            schools_nearby = ["Ichhyakamana Secondary School (350m)", "Kurintar Basic School (520m)"]
            critical_infra = ["Manakamana Cable Car Base Station", "Armed Police Disaster Training Center", "High-Voltage Power Line"]
            exposure_score = 88.0
            exposure_level = "CRITICAL"
        elif "Charkilo" in location_name or "Jalbire" in location_name:
            nearest_road = "Narayanghat-Mugling Highway (NH05, KM 28-32)"
            road_class = "Primary Lifeline Freight & Passenger Corridor"
            distance_to_road_m = 115.0
            settlements_nearby = ["Jalbire Settlement (approx. 180 residents)", "Highway Rest & Roadside Shops"]
            schools_nearby = ["Charkilo Primary School (920m)"]
            critical_infra = ["Jalbire Concrete Motor Bridge", "River Gabion Retaining Structure", "National Fiber Optic Duct"]
            exposure_score = 82.0
            exposure_level = "HIGH"
        else:
            nearest_road = "Kalikhola Rural Feeder Track"
            road_class = "Secondary / Rural Access Road"
            distance_to_road_m = 420.0
            settlements_nearby = ["Kalikhola Lower Village (approx. 90 residents)"]
            schools_nearby = []
            critical_infra = ["Local Culvert Drainage"]
            exposure_score = 38.0
            exposure_level = "MODERATE"

        return {
            "nearest_road": nearest_road,
            "road_class": road_class,
            "distance_to_road_m": distance_to_road_m,
            "settlements_nearby": settlements_nearby,
            "schools_nearby": schools_nearby,
            "critical_infrastructure": critical_infra,
            "exposure_score": exposure_score,
            "exposure_level": exposure_level,
            "source": "OpenStreetMap Nepal (OSM) / Department of Roads Highway Cadastre [DEMO PROVIDER]",
            "is_synthetic": True,
            "disclaimer": "OSM highway vector buffer simulated for Ichhyakamana Rural Municipality road corridor"
        }
