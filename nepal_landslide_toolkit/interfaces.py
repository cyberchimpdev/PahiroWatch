"""
Nepal Landslide Risk Agent Toolkit — Abstract Provider Interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseWeatherProvider(ABC):
    @abstractmethod
    def get_weather_rainfall(self, latitude: float, longitude: float, time_window_hours: int = 24) -> Dict[str, Any]:
        """Fetch precipitation observations for geospatial coordinates."""
        pass

class BaseTerrainProvider(ABC):
    @abstractmethod
    def get_terrain_risk(self, latitude: float, longitude: float, baseline_slope: float, elevation: float) -> Dict[str, Any]:
        """Fetch DEM topographic profile and slope steepness."""
        pass

class BaseSatelliteProvider(ABC):
    @abstractmethod
    def get_satellite_change(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch optical/multispectral difference indicator with cloud quality metrics."""
        pass

class BaseExposureProvider(ABC):
    @abstractmethod
    def get_road_exposure(self, latitude: float, longitude: float, location_name: str) -> Dict[str, Any]:
        """Fetch proximity to critical highway corridor, settlements, and civil assets."""
        pass
