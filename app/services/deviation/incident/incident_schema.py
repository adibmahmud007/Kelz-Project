#!/usr/bin/env python3
"""
Incident Schema Module
Consolidated Pydantic model for incident-related API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class IncidentSchema(BaseModel):
    """Unified schema for all incident-related operations"""
    
    # Common fields
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status or error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")
    
    # Request fields
    transcribed_text: Optional[str] = Field(None, description="Transcribed text to analyze")
    
    # Response fields
    transcription: Optional[str] = Field(None, description="Original transcribed text")
    incident_description: Optional[str] = Field(None, description="AI-generated incident description")
    headline: Optional[str] = Field(None, description="Succinct headline of incident")
    summary: Optional[str] = Field(None, description="Brief incident summary")
    
    # Analysis fields
    title: Optional[str] = Field(None, description="AI-generated incident title")
    who: Optional[str] = Field(None, description="People involved in the incident")
    what: Optional[str] = Field(None, description="Description of what happened")
    where: Optional[str] = Field(None, description="Location where incident occurred")
    immediate_action: Optional[str] = Field(None, description="Actions taken immediately")
    quality_concerns: Optional[str] = Field(None, description="Quality-related concerns")
    quality_controls: Optional[str] = Field(None, description="Quality control measures")
    rca_tool: Optional[str] = Field(None, description="Recommended root cause analysis tool")
    expected_interim_action: Optional[str] = Field(None, description="Expected interim actions")
    capa: Optional[str] = Field(None, description="Corrective and Preventive Actions")
    
    # File upload fields
    filename: Optional[str] = Field(None, description="Name of uploaded file")
    file_size: Optional[int] = Field(None, description="Size of uploaded file in bytes")
    
    # Error fields
    error_type: Optional[str] = Field(None, description="Type of error")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "success": True,
                "message": "Incident processed successfully",
                "headline": "Equipment failure in production line",
                "summary": "Brief description of the incident",
                "timestamp": "2024-01-15T10:30:00"
            }
        }