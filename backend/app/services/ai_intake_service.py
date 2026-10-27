import json
import re
import uuid
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.schemas.schemas import ExtractedServiceInfo

SAFETY_CRITICAL_KEYWORDS = [
    "brake", "brakes", "spongy", "grinding", "pedal to floor", "stopping distance",
    "fluid leak", "smoke", "smoking", "fire", "fuel smell", "gas smell", "burning",
    "steering locked", "shudder at speed", "tire blown", "airbag", "stalling on highway",
    "overheating", "overheat", "steam"
]

SERVICE_CATALOG = {
    "brake_service": {
        "keywords": ["brake", "brakes", "pad", "rotor", "caliper", "squeal", "grind", "stopping"],
        "duration": 90,
        "recommended_parts": ["Premium Ceramic Brake Pads", "Front Brake Rotors", "DOT4 Brake Fluid"],
        "category": "brakes"
    },
    "oil_change": {
        "keywords": ["oil", "filter", "lube", "fluid change", "maintenance", "service a", "service b"],
        "duration": 45,
        "recommended_parts": ["Synthetic 5W-30 Engine Oil (5qt)", "High-Flow Oil Filter", "Crush Washer"],
        "category": "general_maintenance"
    },
    "engine_diagnostics": {
        "keywords": ["check engine", "cel", "misfire", "rough idle", "stutter", "hesitation", "scanner", "error code"],
        "duration": 60,
        "recommended_parts": ["OBD2 Diagnostic Scan", "Spark Plugs Set"],
        "category": "diagnostics"
    },
    "transmission_service": {
        "keywords": ["transmission", "gear", "slipping", "clutch", "shift", "automatic fluid"],
        "duration": 120,
        "recommended_parts": ["Transmission Fluid ATF", "Transmission Filter Kit"],
        "category": "transmission"
    },
    "detailing_and_wash": {
        "keywords": ["wash", "detail", "wax", "clean", "interior", "polish", "ceramic coat"],
        "duration": 90,
        "recommended_parts": ["Ceramic Protective Sealant", "Leather Conditioner"],
        "category": "detailing"
    },
    "suspension_and_tires": {
        "keywords": ["clunk", "bump", "strut", "shock", "tire", "alignment", "balance", "vibration"],
        "duration": 75,
        "recommended_parts": ["Front Strut Assembly", "Sway Bar Bushings"],
        "category": "suspension"
    }
}

async def call_gemini_api(prompt: str) -> Optional[str]:
    """Call Google Gemini API if GEMINI_API_KEY is available."""
    if not settings.GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
    except Exception as e:
        print(f"Gemini API request failed, falling back to deterministic parser: {e}")
        return None
    return None

def heuristic_extraction(
    message: str,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    vehicle_year: Optional[int] = None
) -> ExtractedServiceInfo:
    """Deterministic fallback and rule-based NLP extraction engine."""
    msg_lower = message.lower()
    
    # 1. Vehicle extraction if not already provided
    extracted_make = vehicle_make
    extracted_model = vehicle_model
    extracted_year = vehicle_year
    
    common_makes = ["toyota", "honda", "ford", "chevrolet", "bmw", "audi", "mercedes", "subaru", "nissan", "hyundai", "kia", "volkswagen", "mazda", "lexus", "tesla"]
    if not extracted_make:
        for make in common_makes:
            if re.search(r'\b' + make + r'\b', msg_lower):
                extracted_make = make.title()
                break
                
    if not extracted_year:
        year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', message)
        if year_match:
            extracted_year = int(year_match.group(1))

    # 2. Safety escalation detection
    is_safety_critical = any(kw in msg_lower for kw in SAFETY_CRITICAL_KEYWORDS)
    safety_advisory = None
    if is_safety_critical:
        safety_advisory = (
            "SAFETY ADVISORY: The reported symptoms involve safety-critical vehicle systems (brakes, steering, or thermal hazards). "
            "PitStop AI has escalated this intake for immediate certified mechanic inspection. "
            "Caution: Avoid driving at highway speeds or under heavy load until professionally verified."
        )

    # 3. Service matching
    detected_service = "general_inspection"
    service_duration = 60
    recommended_parts = []
    
    for s_key, s_data in SERVICE_CATALOG.items():
        if any(kw in msg_lower for kw in s_data["keywords"]):
            detected_service = s_key
            service_duration = s_data["duration"]
            recommended_parts = s_data["recommended_parts"]
            break

    # 4. Symptoms identification
    symptoms = []
    symptom_patterns = [
        (r'squeak\w*|grind\w*|squeal\w*', "Abnormal brake or mechanical grinding/squeaking noise"),
        (r'leak\w*|fluid\w*', "Fluid leak observed under vehicle or reservoir"),
        (r'shudder\w*|vibrat\w*', "Steering or pedal vibration/shudder"),
        (r'smell\w*|smoke\w*', "Unusual odor or smoke emitted"),
        (r'check engine|light on|cel', "Check Engine Light / warning indicator illuminated"),
        (r'soft pedal|pedal to the floor|spongy', "Spongy or low brake pedal travel"),
        (r'oil change|filter', "Routine maintenance / oil life expired")
    ]
    for pattern, desc in symptom_patterns:
        if re.search(pattern, msg_lower):
            symptoms.append(desc)
    if not symptoms:
        symptoms.append("Customer-reported mechanical concern requiring diagnostic review")

    # 5. Missing fields detection
    missing_fields = []
    clarification_questions = []
    
    if not extracted_year:
        missing_fields.append("vehicle_year")
        clarification_questions.append("Could you confirm the model year of your vehicle?")
    if not extracted_make or not extracted_model:
        missing_fields.append("vehicle_make_model")
        clarification_questions.append("What is the exact make and model of your vehicle?")
    if is_safety_critical and "brake" in msg_lower:
        clarification_questions.append("Does the brake pedal feel soft/spongy, or do you hear a high-pitched grinding sound when coming to a complete stop?")
    if not clarification_questions:
        clarification_questions.append("Do you have a preferred time window or specific day this week for drop-off?")

    urgency = "safety_critical" if is_safety_critical else ("high" if "urgent" in msg_lower or "asap" in msg_lower else "normal")
    
    summary = (
        f"Intake for {extracted_year or 'Unknown Year'} {extracted_make or 'Vehicle'} "
        f"indicating {detected_service.replace('_', ' ').title()}. "
        f"{'Safety escalation active.' if is_safety_critical else 'Standard priority triage.'}"
    )

    return ExtractedServiceInfo(
        vehicle_make=extracted_make,
        vehicle_model=extracted_model,
        vehicle_year=extracted_year,
        symptoms=symptoms,
        proposed_service_type=detected_service,
        estimated_duration_minutes=service_duration,
        urgency=urgency,
        safety_escalation=is_safety_critical,
        safety_advisory=safety_advisory,
        missing_fields=missing_fields,
        clarification_questions=clarification_questions,
        recommended_parts=recommended_parts,
        ai_confidence_score=0.92,
        ai_summary=summary
    )

async def extract_service_request_agent(
    message: str,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    vehicle_year: Optional[int] = None
) -> ExtractedServiceInfo:
    """Primary AI Agent entry point with Gemini LLM and deterministic fallback."""
    
    prompt = f"""
You are the PitStop AI Service Intake Agent for an automotive repair workshop.
Analyze the following customer message and context to extract structured service information according to workshop policies.

Customer message: "{message}"
Known Context:
- Make: {vehicle_make or "Unknown"}
- Model: {vehicle_model or "Unknown"}
- Year: {vehicle_year or "Unknown"}
- Customer Name: {customer_name or "Unknown"}

Strict Rules:
1. Identify vehicle year, make, and model if mentioned in the message.
2. Categorize service into one of: ["brake_service", "oil_change", "engine_diagnostics", "transmission_service", "detailing_and_wash", "suspension_and_tires", "general_inspection"].
3. Estimate reasonable duration in minutes (e.g. 45 for oil, 90 for brakes).
4. SAFETY GUARDRAIL: If the message mentions brake problems, smoke, fluid leaks, spongy pedals, or steering loss, set safety_escalation=true and urgency="safety_critical". Provide a cautious safety advisory reminding the customer that this is not a final mechanical diagnosis and to avoid hazardous driving.
5. Identify any missing information (e.g. year, trim, exact symptom) and form 1-2 polite, targeted clarification questions.
6. List likely recommended parts.

Respond strictly in valid JSON matching this structure:
{{
  "vehicle_make": string or null,
  "vehicle_model": string or null,
  "vehicle_year": integer or null,
  "symptoms": [string],
  "proposed_service_type": string,
  "estimated_duration_minutes": integer,
  "urgency": "low" | "normal" | "high" | "safety_critical",
  "safety_escalation": boolean,
  "safety_advisory": string or null,
  "missing_fields": [string],
  "clarification_questions": [string],
  "recommended_parts": [string],
  "ai_confidence_score": float,
  "ai_summary": string
}}
"""

    gemini_resp = await call_gemini_api(prompt)
    if gemini_resp:
        try:
            data = json.loads(gemini_resp)
            return ExtractedServiceInfo(**data)
        except Exception as e:
            print(f"Failed to parse Gemini response as JSON: {e}")
            
    # Fallback to high quality deterministic extraction
    return heuristic_extraction(
        message=message,
        customer_name=customer_name,
        customer_phone=customer_phone,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        vehicle_year=vehicle_year
    )
