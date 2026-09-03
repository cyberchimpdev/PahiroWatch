import json
from app.db.database import get_db_connection, init_db

PILOT_LOCATIONS = [
    {
        "id": "LOC-JALBIRE-KM28",
        "name": "Jalbire Waterfall Sector (KM 28)",
        "corridor_code": "NH05-MUG",
        "district": "Chitwan",
        "municipality": "Ichhyakamana Rural Municipality",
        "ward": 5,
        "latitude": 27.8182,
        "longitude": 84.5381,
        "elevation_m": 340.0,
        "baseline_slope_deg": 38.5,
        "road_name": "Narayanghat-Mugling Highway (NH05)",
        "critical_infrastructure": json.dumps(["Jalbire Motor Bridge", "Trishuli River Retaining Wall", "Fiber Optic Lifeline Cable"])
    },
    {
        "id": "LOC-CHARKILO-KM32",
        "name": "Charkilo Fragile Bluff (KM 32)",
        "corridor_code": "NH05-MUG",
        "district": "Chitwan",
        "municipality": "Ichhyakamana Rural Municipality",
        "ward": 5,
        "latitude": 27.8340,
        "longitude": 84.5492,
        "elevation_m": 410.0,
        "baseline_slope_deg": 42.0,
        "road_name": "Narayanghat-Mugling Highway (NH05)",
        "critical_infrastructure": json.dumps(["Engineered Anchored Rocknet", "High-Voltage Transmission Tower"])
    },
    {
        "id": "LOC-KALIKHOLA-KM25",
        "name": "Kalikhola Gorge Section (KM 25)",
        "corridor_code": "NH05-MUG",
        "district": "Chitwan",
        "municipality": "Ichhyakamana Rural Municipality",
        "ward": 6,
        "latitude": 27.7925,
        "longitude": 84.5120,
        "elevation_m": 290.0,
        "baseline_slope_deg": 36.0,
        "road_name": "Narayanghat-Mugling Highway (NH05)",
        "critical_infrastructure": json.dumps(["Culvert Drainage Basin", "Dahakhani Highway Checkpoint"])
    },
    {
        "id": "LOC-KURINTAR-KM36",
        "name": "Kurintar Town Sector (KM 36)",
        "corridor_code": "NH05-MUG",
        "district": "Chitwan",
        "municipality": "Ichhyakamana Rural Municipality",
        "ward": 4,
        "latitude": 27.8650,
        "longitude": 84.5800,
        "elevation_m": 260.0,
        "baseline_slope_deg": 22.0,
        "road_name": "Prithvi / Mugling Feeder Road",
        "critical_infrastructure": json.dumps(["Manakamana Cable Car Base Station", "Armed Police Disaster Management Training Base", "Kurintar Health Post"])
    },
    {
        "id": "LOC-MUGLING-KM38",
        "name": "Mugling Bridge & Bazaar Hub (KM 38)",
        "corridor_code": "NH05-MUG",
        "district": "Chitwan",
        "municipality": "Ichhyakamana Rural Municipality",
        "ward": 5,
        "latitude": 27.8590,
        "longitude": 84.5550,
        "elevation_m": 250.0,
        "baseline_slope_deg": 18.0,
        "road_name": "Mugling Highway Junction (NH04 / NH05)",
        "critical_infrastructure": json.dumps(["Trishuli Arc Suspension Bridge", "Mugling Transport Terminal", "Emergency Ward Depot"])
    }
]

# Initial Seed Memory for cross-run historical recall
HISTORICAL_MEMORY_SEED = [
    {
        "id": "MEM-JALBIRE-2024-01",
        "location_id": "LOC-JALBIRE-KM28",
        "memory_key": "HISTORICAL_INCIDENTS",
        "memory_value": json.dumps({
            "incident_count_past_24m": 3,
            "last_major_slide": "2024-07-12 (Monsoon cloudburst, 36h road blockage)",
            "debris_volume_m3": 4500,
            "geological_vulnerability": "Weathered phyllite bedrock with colluvial overburden"
        }),
        "importance_weight": 1.5
    },
    {
        "id": "MEM-CHARKILO-2024-01",
        "location_id": "LOC-CHARKILO-KM32",
        "memory_key": "HISTORICAL_INCIDENTS",
        "memory_value": json.dumps({
            "incident_count_past_24m": 2,
            "last_major_slide": "2024-08-03 (Rockfall breaching barrier)",
            "debris_volume_m3": 1200,
            "geological_vulnerability": "Fractured limestone joint plane dipping toward highway"
        }),
        "importance_weight": 1.4
    }
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    for loc in PILOT_LOCATIONS:
        cursor.execute("""
        INSERT OR REPLACE INTO locations 
        (id, name, corridor_code, district, municipality, ward, latitude, longitude, elevation_m, baseline_slope_deg, road_name, critical_infrastructure)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            loc["id"], loc["name"], loc["corridor_code"], loc["district"], loc["municipality"],
            loc["ward"], loc["latitude"], loc["longitude"], loc["elevation_m"],
            loc["baseline_slope_deg"], loc["road_name"], loc["critical_infrastructure"]
        ))

    for mem in HISTORICAL_MEMORY_SEED:
        cursor.execute("""
        INSERT OR REPLACE INTO agent_memory 
        (id, location_id, memory_key, memory_value, importance_weight)
        VALUES (?, ?, ?, ?, ?)
        """, (
            mem["id"], mem["location_id"], mem["memory_key"], mem["memory_value"], mem["importance_weight"]
        ))

    conn.commit()
    conn.close()
    print("Seeded 5 pilot corridor locations and historical memory successfully.")

if __name__ == "__main__":
    seed_database()
