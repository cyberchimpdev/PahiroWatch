from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseWeatherProvider(ABC):
    @abstractmethod
    def get_weather_rainfall(self, latitude: float, longitude: float, time_window_hours: int = 24) -> Dict[str, Any]:
        """Fetch precipitation telemetry for coordinates."""
        pass

class BaseTerrainProvider(ABC):
    @abstractmethod
    def get_terrain_risk(self, latitude: float, longitude: float, baseline_slope: float = 35.0, elevation: float = 300.0) -> Dict[str, Any]:
        """Fetch topographic DEM profile, slope gradient, and terrain hazard index."""
        pass

class BaseSatelliteProvider(ABC):
    @abstractmethod
    def get_satellite_change(self, latitude: float, longitude: float, simulate_failure: bool = False) -> Dict[str, Any]:
        """Fetch optical/multispectral difference indicator with cloud quality metrics."""
        pass

class BaseExposureProvider(ABC):
    @abstractmethod
    def get_road_exposure(self, latitude: float, longitude: float, location_name: str) -> Dict[str, Any]:
        """Fetch proximity to critical highway corridor, settlements, and civil assets."""
        pass

class BaseMemoryProvider(ABC):
    @abstractmethod
    def get_incident_memory(self, location_id: str) -> Dict[str, Any]:
        """Fetch persistent incident memory and cross-run historical context."""
        pass
