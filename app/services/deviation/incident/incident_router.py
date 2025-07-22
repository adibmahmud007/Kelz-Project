#!/usr/bin/env python3
"""
Incident Router Module
FastAPI routes for incident-related endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os
import shutil

from incident import IncidentManager
from incident_schema import (
    IncidentResponse, 
    IncidentRequest, 
    IncidentSummaryResponse,
    FileUploadResponse,
    ErrorResponse
)

# Create router
router = APIRouter(
    prefix="/incident",
    tags=["incident"],
    responses={404: {"description": "Not found"}},
)

# Initialize incident manager
incident_manager = IncidentManager()

# Dependency to get incident manager
def get_incident_manager() -> IncidentManager:
    return incident_manager

@router.get("/", response_model=dict)
async def incident_root():
    """
    Root endpoint for incident module
    """
    return {
        "message": "Incident Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process-audio": "Process incident from audio file",
            "POST /process-text": "Process incident from text",
            "POST /summary": "Get incident summary",
            "GET /health": "Health check"
        }
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test if the incident manager is properly initialized
        if incident_manager.transcriber and incident_manager.analyzer:
            return {
                "status": "healthy",
                "message": "Incident service is operational",
                "transcriber": "ready",
                "analyzer": "ready"
            }
        else:
            return {
                "status": "degraded",
                "message": "Some components are not properly initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Service check failed: {str(e)}"
        }

@router.post("/process-audio", response_model=IncidentResponse)
async def process_incident_audio(
    file: UploadFile = File(...),
    manager: IncidentManager = Depends(get_incident_manager)
):
    """
    Process incident from uploaded audio file
    
    Args:
        file: Audio file upload
        manager: Incident manager instance
        
    Returns:
        IncidentResponse: Complete incident analysis
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}. "
                       f"Supported formats: {', '.join(valid_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size (25MB limit for Whisper)
        if len(file_content) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 25MB for audio processing."
            )
        
        # Process the file
        result = manager.process_uploaded_file(file_content, file.filename)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio file: {str(e)}"
        )

@router.post("/process-text", response_model=IncidentResponse)
async def process_incident_text(
    request: IncidentRequest,
    manager: IncidentManager = Depends(get_incident_manager)
):
    """
    Process incident from transcribed text
    
    Args:
        request: Incident request with transcribed text
        manager: Incident manager instance
        
    Returns:
        IncidentResponse: Complete incident analysis
    """
    try:
        if not request.transcribed_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcribed text cannot be empty"
            )
        
        result = manager.process_incident_from_text(request.transcribed_text)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing text: {str(e)}"
        )

@router.post("/summary", response_model=IncidentSummaryResponse)
async def get_incident_summary(
    request: IncidentRequest,
    manager: IncidentManager = Depends(get_incident_manager)
):
    """
    Get a quick summary of the incident
    
    Args:
        request: Incident request with transcribed text
        manager: Incident manager instance
        
    Returns:
        IncidentSummaryResponse: Brief incident summary
    """
    try:
        if not request.transcribed_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcribed text cannot be empty"
            )
        
        result = manager.get_incident_summary(request.transcribed_text)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/transcribe", response_model=dict)
async def transcribe_audio_only(
    file: UploadFile = File(...),
    manager: IncidentManager = Depends(get_incident_manager)
):
    """
    Transcribe audio file without analysis
    
    Args:
        file: Audio file upload
        manager: Incident manager instance
        
    Returns:
        dict: Transcription result
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            # Transcribe audio
            transcription = manager.transcriber.transcribe_audio(tmp_file_path)
            
            if transcription:
                return {
                    "success": True,
                    "message": "Transcription completed successfully",
                    "transcription": transcription,
                    "filename": file.filename,
                    "character_count": len(transcription)
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to transcribe audio",
                    "transcription": None,
                    "filename": file.filename,
                    "character_count": 0
                }
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing audio: {str(e)}"
        )

@router.post("/analyze-existing", response_model=IncidentResponse)
async def analyze_existing_transcription(
    audio_file: UploadFile = File(...),
    manager: IncidentManager = Depends(get_incident_manager)
):
    """
    Complete workflow: Upload audio -> Transcribe -> Analyze -> Return full results
    
    Args:
        audio_file: Audio file upload
        manager: Incident manager instance
        
    Returns:
        IncidentResponse: Complete incident analysis with all fields
    """
    try:
        # Validate file
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
        file_extension = os.path.splitext(audio_file.filename)[1].lower()
        
        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}"
            )
        
        # Read file content
        file_content = await audio_file.read()
        
        # Process the complete workflow
        result = manager.process_uploaded_file(file_content, audio_file.filename)
        
        # Display results in console (for debugging)
        manager.display_incident_results(result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in complete analysis workflow: {str(e)}"
        )

@router.get("/templates/fields")
async def get_incident_fields():
    """
    Get the structure of incident analysis fields
    
    Returns:
        dict: Field descriptions for the incident analysis
    """
    return {
        "incident_fields": {
            "title": "AI-generated incident title",
            "who": "People involved in the incident",
            "what": "Description of what happened",
            "where": "Location where incident occurred",
            "immediate_action": "Actions taken immediately",
            "quality_concerns": "Quality-related concerns",
            "quality_controls": "Quality control measures",
            "rca_tool": "Recommended root cause analysis tool",
            "expected_interim_action": "Expected interim actions",
            "capa": "Corrective and Preventive Actions"
        },
        "response_structure": {
            "success": "Boolean indicating processing success",
            "message": "Status message",
            "transcription": "Original transcribed text",
            "incident_description": "AI-generated incident description",
            "headline": "Succinct headline of incident",
            "analysis": "Detailed structured analysis",
            "timestamp": "Processing timestamp"
        }
    }

# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            error_type="HTTPException"
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message=f"Internal server error: {str(exc)}",
            error_type="InternalError"
        ).dict()
    )