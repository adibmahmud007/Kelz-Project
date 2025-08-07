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
        audio: Optional[UploadFile] = File(None),
        file: Optional[UploadFile] = File(None),
        manager: IncidentManager = Depends(lambda: incident_manager)
    ):
        """
        Analyze incident from audio and/or document file and return structured JSON response

        Args:
            audio: Audio file upload (optional)
            file: Document file upload (optional)
            manager: Incident manager instance

        Returns:
            dict: Clean JSON response with incident analysis
        """
        try:
            valid_audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
            valid_doc_extensions = ['.pdf', '.docx', '.txt']
            valid_extensions = valid_audio_extensions + valid_doc_extensions

            audio_text = None
            file_text = None
            filenames = []

            # Process audio if provided and not empty
            print("DEBUG: audio=", audio)
            print("DEBUG: file=", file)
            if audio and hasattr(audio, 'filename') and audio.filename:
                audio_content = await audio.read()
                print("DEBUG: audio.filename=", audio.filename)
                print("DEBUG: len(audio_content)=", len(audio_content))
                if not audio.filename.strip() or not audio_content:
                    audio = None  # Treat as not provided
                else:
                    audio_ext = os.path.splitext(audio.filename)[1].lower()
                    print("DEBUG: audio_ext=", audio_ext)
                    if audio_ext not in valid_audio_extensions:
                        raise HTTPException(status_code=400, detail=f"Unsupported audio file format: {audio_ext}")
                    if len(audio_content) > 25 * 1024 * 1024:
                        raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 25MB.")
                    result_audio = manager.process_uploaded_file(audio_content, audio.filename)
                    if result_audio.success and result_audio.transcription:
                        audio_text = result_audio.transcription
                    filenames.append(audio.filename)


            # Process document if provided and not empty
            if file and hasattr(file, 'filename') and file.filename:
                file_content = await file.read()
                print("DEBUG: file.filename=", file.filename)
                print("DEBUG: len(file_content)=", len(file_content))
                if not file.filename.strip() or not file_content:
                    file = None  # Treat as not provided
                else:
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    print("DEBUG: file_ext=", file_ext)
                    if file_ext not in valid_doc_extensions:
                        raise HTTPException(status_code=400, detail=f"Unsupported document file format: {file_ext}")
                    if len(file_content) > 25 * 1024 * 1024:
                        raise HTTPException(status_code=400, detail="Document file too large. Maximum size is 25MB.")
                    result_doc = manager.process_uploaded_document(file_content, file.filename)
                    if result_doc.success and result_doc.transcription:
                        file_text = result_doc.transcription
                    filenames.append(file.filename)

            if not audio_text and not file_text:
                raise HTTPException(status_code=400, detail="No valid audio or document file provided.")

            # If both audio and file are present, combine their texts and analyze as one
            if audio_text and file_text:
                combined_text = audio_text.strip() + "\n\n" + file_text.strip()
                combined_result = manager.process_incident_from_text(combined_text)
                return {
                    "status": "success" if combined_result.success else "error",
                    "filename": f"{audio.filename}, {file.filename}",
                    "incident_description": combined_result.incident_description or "",
                    "headline": combined_result.headline or "",
                    "incident_data": {
                        "title": combined_result.analysis.title if combined_result.analysis else "",
                        "who": combined_result.analysis.who if combined_result.analysis else "",
                        "what": combined_result.analysis.what if combined_result.analysis else "",
                        "where": combined_result.analysis.where if combined_result.analysis else "",
                        "immediate_action": combined_result.analysis.immediate_action if combined_result.analysis else "",
                        "quality_concerns": combined_result.analysis.quality_concerns if combined_result.analysis else "",
                        "quality_controls": combined_result.analysis.quality_controls if combined_result.analysis else "",
                        "rca_tool": combined_result.analysis.rca_tool if combined_result.analysis else "",
                        "expected_interim_action": combined_result.analysis.expected_interim_action if combined_result.analysis else "",
                        "capa": combined_result.analysis.capa if combined_result.analysis else ""
                    },
                    "deviation_triage": getattr(combined_result, "deviation_triage", None),
                    "product_quality": getattr(combined_result, "product_quality", None),
                    "patient_safety": getattr(combined_result, "patient_safety", None),
                    "regulatory_impact": getattr(combined_result, "regulatory_impact", None),
                    "validation_impact": getattr(combined_result, "validation_impact", None),
                    "customer_notification": getattr(combined_result, "customer_notification", None),
                    "review_qta": getattr(combined_result, "review_qta", None),
                    "criticality": getattr(combined_result, "criticality", None),
                    "message": "Deviation incident analysis completed" if combined_result.success else combined_result.message
                }
            # If only one file is present, analyze as before
            elif audio_text:
                audio_result = manager.process_incident_from_text(audio_text.strip())
                return {
                    "status": "success" if audio_result.success else "error",
                    "filename": audio.filename,
                    "incident_description": audio_result.incident_description or "",
                    "headline": audio_result.headline or "",
                    "incident_data": {
                        "title": audio_result.analysis.title if audio_result.analysis else "",
                        "who": audio_result.analysis.who if audio_result.analysis else "",
                        "what": audio_result.analysis.what if audio_result.analysis else "",
                        "where": audio_result.analysis.where if audio_result.analysis else "",
                        "immediate_action": audio_result.analysis.immediate_action if audio_result.analysis else "",
                        "quality_concerns": audio_result.analysis.quality_concerns if audio_result.analysis else "",
                        "quality_controls": audio_result.analysis.quality_controls if audio_result.analysis else "",
                        "rca_tool": audio_result.analysis.rca_tool if audio_result.analysis else "",
                        "expected_interim_action": audio_result.analysis.expected_interim_action if audio_result.analysis else "",
                        "capa": audio_result.analysis.capa if audio_result.analysis else ""
                    },
                    "deviation_triage": getattr(audio_result, "deviation_triage", None),
                    "product_quality": getattr(audio_result, "product_quality", None),
                    "patient_safety": getattr(audio_result, "patient_safety", None),
                    "regulatory_impact": getattr(audio_result, "regulatory_impact", None),
                    "validation_impact": getattr(audio_result, "validation_impact", None),
                    "customer_notification": getattr(audio_result, "customer_notification", None),
                    "review_qta": getattr(audio_result, "review_qta", None),
                    "criticality": getattr(audio_result, "criticality", None),
                    "message": "Deviation incident analysis completed" if audio_result.success else audio_result.message
                }
            elif file_text:
                file_result = manager.process_incident_from_text(file_text.strip())
                return {
                    "status": "success" if file_result.success else "error",
                    "filename": file.filename,
                    "incident_description": file_result.incident_description or "",
                    "headline": file_result.headline or "",
                    "incident_data": {
                        "title": file_result.analysis.title if file_result.analysis else "",
                        "who": file_result.analysis.who if file_result.analysis else "",
                        "what": file_result.analysis.what if file_result.analysis else "",
                        "where": file_result.analysis.where if file_result.analysis else "",
                        "immediate_action": file_result.analysis.immediate_action if file_result.analysis else "",
                        "quality_concerns": file_result.analysis.quality_concerns if file_result.analysis else "",
                        "quality_controls": file_result.analysis.quality_controls if file_result.analysis else "",
                        "rca_tool": file_result.analysis.rca_tool if file_result.analysis else "",
                        "expected_interim_action": file_result.analysis.expected_interim_action if file_result.analysis else "",
                        "capa": file_result.analysis.capa if file_result.analysis else ""
                    },
                    "deviation_triage": getattr(file_result, "deviation_triage", None),
                    "product_quality": getattr(file_result, "product_quality", None),
                    "patient_safety": getattr(file_result, "patient_safety", None),
                    "regulatory_impact": getattr(file_result, "regulatory_impact", None),
                    "validation_impact": getattr(file_result, "validation_impact", None),
                    "customer_notification": getattr(file_result, "customer_notification", None),
                    "review_qta": getattr(file_result, "review_qta", None),
                    "criticality": getattr(file_result, "criticality", None),
                    "message": "Deviation incident analysis completed" if file_result.success else file_result.message
                }
            else:
                return {
                    "status": "error",
                    "message": "No valid analysis results."
                }

        except HTTPException:
            raise
        except Exception as e:
            return {
                "status": "error",
                "filename": ", ".join(filenames) if filenames else "unknown",
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
                "message": f"Error processing file(s): {str(e)}"
            }
