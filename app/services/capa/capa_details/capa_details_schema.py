from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CAPADetailsRequest(BaseModel):
    """Request model for CAPA details processing"""
    audio_file_path: Optional[str] = None
    text_content: Optional[str] = None
    
class CAPADetailsResponse(BaseModel):
    """Response model for CAPA details"""
    transcription: Optional[str] = None
    capa_title: str
    capa_description: str
    detailed_actions: List[str]
    document_references: List[str]
    document_sections_to_amend: List[str]
    document_type: str
    created_at: datetime = datetime.now()
    
class CAPAAnalysisInput(BaseModel):
    """Input model for AI analysis"""
    transcript_text: str