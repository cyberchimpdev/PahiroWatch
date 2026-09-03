import json
from .ml_detector import evaluate_landslide_risk

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_run_landslide_susceptibility_model",
            "description": "Calculates statistical slope failure probability and extracts primary topographic and hydrological risk contributors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slope": {"type": "number"},
                    "rain_72h": {"type": "number"},
                    "moisture": {"type": "number"},
                    "ndvi": {"type": "number"},
                    "vib": {"type": "number"}
                },
                "required": ["slope", "rain_72h", "moisture", "ndvi", "vib"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_check_highway_traffic",
            "description": "Fetches current count of vehicles, freight trucks, and passenger buses in transit along the corridor sector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "corridor_sector": {"type": "string"}
                },
                "required": ["corridor_sector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_stage_emergency_dispatch",
            "description": "Stages life-safety actions: outbound SMS broadcasts to residents and closure of traffic police barriers. BLOCKS FOR HUMAN APPROVAL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_ward": {"type": "string"},
                    "sms_payload_nepali": {"type": "string"},
                    "divert_checkpoints": {"type": "boolean"},
                    "recommended_detour": {"type": "string"},
                    "confidence_score": {"type": "number"}
                },
                "required": ["target_ward", "sms_payload_nepali", "divert_checkpoints", "recommended_detour", "confidence_score"]
            }
        }
    }
]


def execute_tool(name, args_json):
    args = json.loads(args_json)
    if name == "tool_run_landslide_susceptibility_model":
        result = evaluate_landslide_risk(
            slope=float(args["slope"]),
            rain_72h=float(args["rain_72h"]),
            moisture=float(args["moisture"]),
            ndvi=float(args["ndvi"]),
            vib=float(args["vib"])
        )
        return json.dumps(result)
    elif name == "tool_check_highway_traffic":
        sector = args.get("corridor_sector", "Char Kilo")
        traffic_data = {
            "Char Kilo": {"buses": 14, "trucks": 28, "people": 520, "bay": "Jalbire Truck Staging Area (4km South)"},
            "Jalbire": {"buses": 8, "trucks": 15, "people": 310, "bay": "Jalbire Relief Camp (1km North)"},
            "Mugling": {"buses": 18, "trucks": 35, "people": 680, "bay": "Mugling Community Shelter (500m East)"},
        }
        data = traffic_data.get(sector, traffic_data["Char Kilo"])
        return json.dumps({
            "corridor": sector,
            "passenger_buses": data["buses"],
            "freight_trucks": data["trucks"],
            "estimated_people_at_risk": data["people"],
            "nearest_safe_bay": data["bay"]
        })
    elif name == "tool_stage_emergency_dispatch":
        return json.dumps({
            "status": "STAGED",
            "target_ward": args.get("target_ward", ""),
            "sms_payload_nepali": args.get("sms_payload_nepali", ""),
            "divert_checkpoints": args.get("divert_checkpoints", False),
            "recommended_detour": args.get("recommended_detour", ""),
            "confidence_score": args.get("confidence_score", 0.0)
        })
    return json.dumps({"error": "Tool '" + name + "' not recognized"})