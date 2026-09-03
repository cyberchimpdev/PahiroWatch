from typing import Dict, Any

class AlertGenerator:
    """
    Alert Synthesis Engine for PahiroWatch.
    Produces high-impact, actionable notifications formatted in both English and official Nepali (नेपाली),
    along with ultra-compact low-bandwidth SMS payloads for rural VHF/SMS dispatch.
    """

    @staticmethod
    def generate_alerts(
        location_name: str,
        corridor_code: str,
        risk_level: str,
        risk_score: float,
        confidence_score: float,
        rainfall_24h: float,
        slope_deg: float,
        recommended_action: str,
        road_distance_m: float
    ) -> Dict[str, str]:
        
        # Nepali Risk Level Mapping
        ne_risk_map = {
            "CRITICAL": "अति उच्च जोखिम (CRITICAL)",
            "HIGH": "उच्च जोखिम (HIGH)",
            "MODERATE": "मध्यम जोखिम (MODERATE)",
            "LOW": "न्यून जोखिम (LOW)"
        }
        ne_risk = ne_risk_map.get(risk_level, "जोखिम")

        # English Operational Report
        report_en = (
            f"PAHIROWATCH EARLY-WARNING ADVISORY\n"
            f"Status: {risk_level} RISK (Score: {risk_score}/100, Confidence: {int(confidence_score*100)}%)\n"
            f"Location: {location_name} [{corridor_code}]\n"
            f"Key Drivers:\n"
            f"• 24h Precipitation: {rainfall_24h} mm (Critical Monsoon Saturated)\n"
            f"• Topographic Slope: {slope_deg}°\n"
            f"• Infrastructure Proximity: {road_distance_m}m to Primary Highway Lifeline\n"
            f"Recommended Operational Action: {recommended_action}\n"
            f"Disclaimer: Decision-support prototype. Requires human ground verification."
        )

        # Nepali Municipal Emergency Alert
        report_ne = (
            f"पहिरोवाच (PahiroWatch) पूर्वसूचना तथा सचेतना सूचना\n\n"
            f"स्थिति: सम्भावित पहिरो {ne_risk} छ (जोखिम अंक: {risk_score}/100, विश्वसनीयता: {int(confidence_score*100)}%)\n"
            f"स्थान: {location_name} (करिडोर: {corridor_code})\n\n"
            f"प्रमुख प्राविधिक कारण:\n"
            f"• पछिल्लो २४ घण्टामा अति भारी वर्षा: {rainfall_24h} मि.मि.\n"
            f"• भिरालो कमजोर भूभाग: {slope_deg} डिग्री\n"
            f"• मुख्य राजमार्गबाट दूरी: {road_distance_m} मिटर नजिक\n\n"
            f"सिफारिस कार्य:\n"
            f"{recommended_action}\n"
            f"(स्थल निरीक्षण टोली तुरुन्त परिचालन गर्नुहोस् र आवश्यकता अनुसार सवारी आवागमन नियन्त्रण गर्नुहोस्।)\n\n"
            f"नोट: यो पूर्वसूचना मानवीय निर्णय सहयोग प्रणाली (Decision Support Prototype) बाट स्वचालित तयार पारिएको हो।"
        )

        # Ultra-Compact Low-Bandwidth SMS / Radio Dispatch format (<160 chars)
        sms_compact = (
            f"PAHIROWATCH ALERT\n"
            f"{risk_level} RISK ({risk_score})\n"
            f"Loc: {location_name[:18]}\n"
            f"Rain24h: {rainfall_24h}mm | Slope: {slope_deg}deg\n"
            f"Conf: {int(confidence_score*100)}%\n"
            f"Action: {recommended_action[:30]}"
        )

        return {
            "payload_en": report_en,
            "payload_ne": report_ne,
            "payload_sms_compact": sms_compact
        }
