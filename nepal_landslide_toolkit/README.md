# Nepal Landslide Risk Agent Toolkit

An open-source, lightweight Python specification and toolkit for developing autonomous geospatial hazard response agents in Nepal.

## Purpose
Provides standardized Pydantic schemas, provider interfaces, and baseline physical aggregation formulas so municipal disaster management departments, universities, and open-source hackathon contributors can build interoperable, transparent early-warning tools without vendor lock-in.

## Key Components
- **`schemas.py`**: Standardized schemas for rainfall observations, DEM slope profiles, Sentinel-2 spectral difference, road exposure, and immutable agent trace logs.
- **`interfaces.py`**: Abstract interfaces (`BaseWeatherProvider`, `BaseTerrainProvider`, `BaseSatelliteProvider`, `BaseExposureProvider`) facilitating plug-and-play integration with DHM, NASA, Copernicus, or OSM.
- **`simple_risk.py`**: Minimal transparent physical aggregation baseline for 0–100 hazard scoring.

## License
MIT License. Free for municipal and research applications across Nepal.
