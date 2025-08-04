#!/usr/bin/env python3
"""
Quality Review Router
FastAPI router for quality review endpoints
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path


from app.services.deviation.quality_review.quality_review import QualityReviewer
from app.services.deviation.quality_review.quality_review_schema import VoiceQualityReviewResponse

# Create router
router = APIRouter()


quality_reviewer = QualityReviewer()


@router.post(
    "/voice-quality-review/", 
    tags=["deviation"],
    response_model=VoiceQualityReviewResponse,
    summary="Voice Quality Review Analysis",
    description="Upload audio file for comprehensive quality and SME review analysis"
)
async def voice_quality_review(audio: UploadFile = File(...)):
    """
    Process audio file for quality review analysis.
    
    - **audio**: Audio file (mp3, wav, m4a, mp4, webm, ogg, flac)
    - Returns transcription with quality and SME review analysis
    """
    temp_file_path = None
    try:
        # Validate audio file type
        supported_audio_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
            'audio/mp4', 'audio/webm', 'audio/ogg', 'audio/flac'
        ]
        if audio.content_type not in supported_audio_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio type: {audio.content_type}. Supported types: {', '.join(supported_audio_types)}"
            )
        # Check file size (25MB limit for OpenAI Whisper)
        content = await audio.read()
        if len(content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(content)
        # Process voice for quality review
        result = quality_reviewer.process_voice_for_quality_review(temp_file_path)
        if result and result.get("status") == "success":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": audio.filename,
                    "transcription": result["transcription"],
                    "quality_review": result["quality_review"],
                    "sme_review": result["sme_review"],
                    "message": result["message"]
                }
            )
        elif result and result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Voice quality review failed"))
        else:
            raise HTTPException(status_code=500, detail="Voice quality review failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice quality review error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)



@router.post(
    "/quality-assessment/", 
    tags=["deviation"],
    summary="Quick Quality Assessment",
    description="Upload text file for quick quality assessment analysis"
)
async def quality_assessment(file: UploadFile = File(...)):
    """
    Perform quick quality assessment on uploaded text file.
    
    - **file**: Text file containing investigation or quality data
    - Returns quality assessment analysis
    """
    try:
        # Validate file type
        if not file.content_type.startswith('text/'):
            raise HTTPException(status_code=400, detail="Only text files are supported")
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        # Perform quality assessment using the quality review analysis
        quality_prompt = f"""
You are a Quality Assurance specialist. Perform a quick quality assessment of the following content:

CONTENT TO ASSESS:
"{text_content}"

Please provide a brief assessment covering:
1. Overall quality status
2. Key concerns identified
3. Immediate actions needed
4. Compliance implications

Keep the assessment concise but comprehensive.
"""
        from app.services.utils.ai_analysis import AIAnalyzer
        ai_analyzer = AIAnalyzer()
        assessment = ai_analyzer.analyze_with_prompt(quality_prompt)
        if assessment:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": file.filename,
                    "quality_assessment": assessment,
                    "text_length": len(text_content),
                    "message": "Quality assessment completed successfully"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Quality assessment failed")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please upload a UTF-8 text file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality assessment error: {str(e)}")
