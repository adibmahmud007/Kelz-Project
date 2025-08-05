from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import tempfile, os
from app.services.deviation.investigation.investigation import InvestigationService

router = APIRouter()

# New input schema for combined investigation
class InvestigationInput(BaseModel):
    incident_response: Dict[str, Any] = Field(..., description="Response from incident endpoint")
    file_extract_response: Dict[str, Any] = Field(..., description="Response from file_extract endpoint")

def ensure_string(val):
    if isinstance(val, list):
        return "; ".join(str(v) for v in val)
    return str(val) if val is not None else "Not found in document"

@router.post("/investigation-ai/", tags=["deviation"])
async def investigation_ai(input_data: InvestigationInput = Body(...)):
    """
    Accepts the response from incident and file_extract, combines them, and generates a full investigation using AI.
    """
    # Combine context from both sources
    incident = input_data.incident_response
    file_extract = input_data.file_extract_response

    # Build a combined context string for the AI
    context_parts = []
    if incident:
        context_parts.append("INCIDENT RESPONSE:\n" + str(incident))
    if file_extract:
        context_parts.append("FILE EXTRACT RESPONSE:\n" + str(file_extract))
    combined_context = "\n\n".join(context_parts)

    # AI analysis using InvestigationService
    ai_result = InvestigationService.analyze_transcript(combined_context)

    # Build the response, ensuring all fields are strings
    response = {
        "Background": ensure_string(ai_result.get("Background", "Not found in document")),
        "Deviation_Triage": ensure_string(ai_result.get("Deviation Triage", "Not found in document")),
        "Discussion": {
            "process": ensure_string(ai_result.get("Discussion", {}).get("process", "Not found in document")) if isinstance(ai_result.get("Discussion"), dict) else "Not found in document",
            "equipment": ensure_string(ai_result.get("Discussion", {}).get("equipment", "Not found in document")) if isinstance(ai_result.get("Discussion"), dict) else "Not found in document",
            "environment_people": ensure_string(ai_result.get("Discussion", {}).get("environment_people", "Not found in document")) if isinstance(ai_result.get("Discussion"), dict) else "Not found in document",
            "documentation": ensure_string(ai_result.get("Discussion", {}).get("documentation", "Not found in document")) if isinstance(ai_result.get("Discussion"), dict) else "Not found in document",
        },
        "Root_Cause_Analysis": {
            "5_why": ensure_string(ai_result.get("Root Cause Analysis", {}).get("5_why", "Not found in document")) if isinstance(ai_result.get("Root Cause Analysis"), dict) else "Not found in document",
            "Fishbone": ensure_string(ai_result.get("Root Cause Analysis", {}).get("Fishbone", "Not found in document")) if isinstance(ai_result.get("Root Cause Analysis"), dict) else "Not found in document",
            "5Ms": ensure_string(ai_result.get("Root Cause Analysis", {}).get("5Ms", "Not found in document")) if isinstance(ai_result.get("Root Cause Analysis"), dict) else "Not found in document",
            "FMEA": ensure_string(ai_result.get("Root Cause Analysis", {}).get("FMEA", "Not found in document")) if isinstance(ai_result.get("Root Cause Analysis"), dict) else "Not found in document",
        },
        "Final_Assessment": {
            "Patient_Safety": ensure_string(ai_result.get("Final Assessment", {}).get("Patient_Safety", "Not found in document")) if isinstance(ai_result.get("Final Assessment"), dict) else "Not found in document",
            "Product_Quality": ensure_string(ai_result.get("Final Assessment", {}).get("Product_Quality", "Not found in document")) if isinstance(ai_result.get("Final Assessment"), dict) else "Not found in document",
            "Compliance_Impact": ensure_string(ai_result.get("Final Assessment", {}).get("Compliance_Impact", "Not found in document")) if isinstance(ai_result.get("Final Assessment"), dict) else "Not found in document",
            "Validation_Impact": ensure_string(ai_result.get("Final Assessment", {}).get("Validation_Impact", "Not found in document")) if isinstance(ai_result.get("Final Assessment"), dict) else "Not found in document",
            "Regulatory_Impact": ensure_string(ai_result.get("Final Assessment", {}).get("Regulatory_Impact", "Not found in document")) if isinstance(ai_result.get("Final Assessment"), dict) else "Not found in document",
        },
        "Historic_Review": {
            "previous_occurrence": ensure_string(ai_result.get("Historic Review", {}).get("previous_occurrence", "Not found in document")) if isinstance(ai_result.get("Historic Review"), dict) else "Not found in document",
            "impact_to_adequacy_of_RCA_and_CAPA": ensure_string(ai_result.get("Historic Review", {}).get("impact_to_adequacy_of_RCA_and_CAPA", "Not found in document")) if isinstance(ai_result.get("Historic Review"), dict) else "Not found in document",
        },
        "CAPA": {
            "Correction": ensure_string(ai_result.get("CAPA", {}).get("Correction", "Not found in document")) if isinstance(ai_result.get("CAPA"), dict) else "Not found in document",
            "Interim_Action": ensure_string(ai_result.get("CAPA", {}).get("Interim_Action", "Not found in document")) if isinstance(ai_result.get("CAPA"), dict) else "Not found in document",
            "Corrective_Action": ensure_string(ai_result.get("CAPA", {}).get("Corrective_Action", "Not found in document")) if isinstance(ai_result.get("CAPA"), dict) else "Not found in document",
            "Preventive_Action": ensure_string(ai_result.get("CAPA", {}).get("Preventive_Action", "Not found in document")) if isinstance(ai_result.get("CAPA"), dict) else "Not found in document",
        },
        "Investigation_Summary": ensure_string(ai_result.get("Investigation Summary", "Not found in document")),
    }
    return JSONResponse(status_code=200, content=response)
