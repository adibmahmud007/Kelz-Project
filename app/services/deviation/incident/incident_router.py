#!/usr/bin/env python3
"""
Simplified Incident Router Module
Single endpoint for incident analysis with clean JSON response
"""

from fastapi import File, UploadFile, HTTPException, Depends
from typing import Optional
import tempfile
import os

from app.services.deviation.incident.incident import IncidentManager



def register_incident_routes(router):
    incident_manager = IncidentManager()

    @router.post("/incident/analyze/audio", tags=["deviation"])
    async def analyze_incident(
        file: UploadFile = File(...),
        manager: IncidentManager = Depends(lambda: incident_manager)
    ):
        """
        Analyze incident from audio file and return structured JSON response

        Args:
            file: Audio file upload
            manager: Incident manager instance

        Returns:
            dict: Clean JSON response with incident analysis
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
            file_extension = os.path.splitext(file.filename)[1].lower()

            if file_extension not in valid_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}"
                )

            # Check file size (25MB limit)
            file_content = await file.read()
            if len(file_content) > 25 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum size is 25MB."
                )

            # Process the file
            result = manager.process_uploaded_file(file_content, file.filename)

            # Return your desired JSON structure
            return {
                "status": "success" if result.success else "error",
                "filename": file.filename,
                "incident_description": result.incident_description or "",
                "headline": result.headline or "",
                "incident_data": {
                    "title": result.analysis.title if result.analysis else "",
                    "who": result.analysis.who if result.analysis else "",
                    "what": result.analysis.what if result.analysis else "",
                    "where": result.analysis.where if result.analysis else "",
                    "immediate_action": result.analysis.immediate_action if result.analysis else "",
                    "quality_concerns": result.analysis.quality_concerns if result.analysis else "",
                    "quality_controls": result.analysis.quality_controls if result.analysis else "",
                    "rca_tool": result.analysis.rca_tool if result.analysis else "",
                    "expected_interim_action": result.analysis.expected_interim_action if result.analysis else "",
                    "capa": result.analysis.capa if result.analysis else ""
                },
                "message": "Deviation incident analysis completed" if result.success else result.message
            }

        except HTTPException:
            raise
        except Exception as e:
            return {
                "status": "error",
                "filename": file.filename if file.filename else "unknown",
                "incident_description": "",
                "headline": "",
                "incident_data": {
                    "title": "",
                    "who": "",
                    "what": "",
                    "where": "",
                    "immediate_action": "",
                    "quality_concerns": "",
                    "quality_controls": "",
                    "rca_tool": "",
                    "expected_interim_action": "",
                    "capa": ""
                },
                "message": f"Error processing file: {str(e)}"
            }
