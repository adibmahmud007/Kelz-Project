from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from app.services.utils.ai_analysis import AIAnalyzer
from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.document_ocr import DocumentOCR
import os
import tempfile
import shutil
from typing import Dict, Any

router = APIRouter()

# Initialize services
ai_analyzer = AIAnalyzer()
voice_transcriber = VoiceTranscriber()
document_ocr = DocumentOCR()

# --- DEFAULT TAG ---
@router.post("/ai-analysis/", tags=["default"])
async def ai_analysis(file: UploadFile = File(...)):
    """AI analysis of uploaded text file."""
    try:
        # Validate file type
        if not file.content_type.startswith('text/'):
            raise HTTPException(status_code=400, detail="Only text files are supported")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Perform AI analysis
        result = ai_analyzer.analyze_incident(text_content)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": file.filename,
                    "analysis": result,
                    "message": "AI analysis completed successfully"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="AI analysis failed")
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please upload a UTF-8 text file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/extract-text/", tags=["default"])
async def text_extraction(file: UploadFile = File(...)):
    """Extract text from uploaded file using OCR."""
    temp_file_path = None
    try:
        # Validate file type
        supported_types = [
            'application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 
            'image/gif', 'image/webp', 'image/bmp', 'image/tiff'
        ]
        
        if file.content_type not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Supported types: {', '.join(supported_types)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Extract text using OCR only
        extracted_text = document_ocr.extract_text(temp_file_path)
        
        if extracted_text:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": file.filename,
                    "extracted_text": extracted_text,
                    "text_length": len(extracted_text),
                    "message": "Text extraction completed successfully"
                }
            )
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "warning",
                    "filename": file.filename,
                    "extracted_text": "",
                    "message": "No text could be extracted from the document"
                }
            )
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Temporary file not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.post("/transcription/audio/", tags=["default"])
async def transcription_audio(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file."""
    temp_file_path = None
    try:
        # Validate file type
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
        
        # Transcribe audio
        original_transcription, polished_transcription = voice_transcriber.process_file_with_results(temp_file_path)
        
        if original_transcription:
            # Also perform AI analysis on the transcription
            incident_analysis = ai_analyzer.analyze_incident(original_transcription)
            summary_analysis = ai_analyzer.get_summary_analysis(original_transcription)
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": audio.filename,
                    "original_transcription": original_transcription,
                    "polished_transcription": polished_transcription,
                    "incident_analysis": incident_analysis,
                    "summary": summary_analysis,
                    "transcription_length": len(original_transcription),
                    "message": "Audio transcription completed successfully"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Audio transcription failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

# --- DEVIATION TAG ---
@router.post("/file-analysis/", tags=["deviation"])
async def file_analysis(file: UploadFile = File(...)):
    """Analyze uploaded file for deviation incidents."""
    temp_file_path = None
    try:
        # Handle different file types
        if file.content_type.startswith('text/'):
            # Text file
            content = await file.read()
            text_content = content.decode('utf-8')
            
        elif file.content_type.startswith('audio/'):
            # Audio file - transcribe first
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
            
            text_content = voice_transcriber.transcribe_audio(temp_file_path)
            if not text_content:
                raise HTTPException(status_code=500, detail="Failed to transcribe audio file")
                
        elif file.content_type in ['application/pdf'] or file.content_type.startswith('image/'):
            # Document/Image file - extract text first
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
            
            text_content = document_ocr.extract_text(temp_file_path)
            if not text_content:
                raise HTTPException(status_code=500, detail="Failed to extract text from document")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for deviation analysis")
        
        # Perform comprehensive analysis
        incident_analysis = ai_analyzer.analyze_incident(text_content)
        document_analysis = ai_analyzer.analyze_document_for_extraction(text_content)
        summary = ai_analyzer.get_summary_analysis(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "file_type": file.content_type,
                "extracted_content": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                "incident_analysis": incident_analysis,
                "document_analysis": document_analysis,
                "summary": summary,
                "message": "File analysis for deviation completed successfully"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis error: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.post("/incident/", tags=["deviation"])
async def deviation_incident(file: UploadFile = File(...)):
    """Process deviation incident from uploaded file."""
    try:
        # Read and process file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Analyze incident
        incident_analysis = ai_analyzer.analyze_incident(text_content)
        
        if incident_analysis:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": file.filename,
                    "incident_data": incident_analysis,
                    "message": "Deviation incident analysis completed"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Incident analysis failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incident processing error: {str(e)}")

@router.post("/investigation/", tags=["deviation"])
async def investigation(file: UploadFile = File(...)):
    """Process deviation investigation from uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Perform investigation analysis
        investigation_analysis = ai_analyzer.analyze_investigation_context(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "investigation_data": investigation_analysis,
                "message": "Deviation investigation analysis completed"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation analysis error: {str(e)}")

@router.post("/quality-review/", tags=["deviation"])
async def quality_review(file: UploadFile = File(...)):
    """Perform quality review on uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Perform quality-focused analysis
        incident_analysis = ai_analyzer.analyze_incident(text_content)
        document_analysis = ai_analyzer.analyze_document_for_extraction(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "quality_analysis": {
                    "incident_details": incident_analysis,
                    "document_references": document_analysis,
                    "quality_concerns": incident_analysis.get('quality_concerns') if incident_analysis else None,
                    "quality_controls": incident_analysis.get('quality_controls') if incident_analysis else None
                },
                "message": "Quality review completed"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality review error: {str(e)}")

# --- CAPA TAG ---
@router.post("/capa/details/", tags=["capa"])
async def capa_details(file: UploadFile = File(...)):
    """Extract CAPA details from uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Analyze for CAPA information
        capa_analysis = ai_analyzer.analyze_capa(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "capa_details": capa_analysis,
                "message": "CAPA details extraction completed"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAPA details error: {str(e)}")

@router.post("/capa/review/", tags=["capa"])
async def capa_review(file: UploadFile = File(...)):
    """Review CAPA from uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Perform CAPA analysis and review
        capa_analysis = ai_analyzer.analyze_capa(text_content)
        incident_analysis = ai_analyzer.analyze_incident(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "capa_review": {
                    "capa_details": capa_analysis,
                    "related_incident": incident_analysis,
                    "effectiveness_assessment": "Review required for implementation effectiveness"
                },
                "message": "CAPA review completed"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAPA review error: {str(e)}")

@router.post("/capa/documents/", tags=["capa"])
async def capa_documents(file: UploadFile = File(...)):
    """Process CAPA documents from uploaded file."""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Analyze documents for CAPA
        document_analysis = ai_analyzer.analyze_document_for_extraction(text_content)
        capa_analysis = ai_analyzer.analyze_capa(text_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "filename": file.filename,
                "document_analysis": document_analysis,
                "capa_information": capa_analysis,
                "message": "CAPA documents processing completed"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAPA documents error: {str(e)}")

# Initialize FastAPI app
app = FastAPI(
    title="AI Analysis API",
    description="API for AI-powered analysis of documents, audio, and text files",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "ai_analysis": "/ai-analysis/",
            "text_extraction": "/extract-text/",
            "transcription": "/transcription/audio/",
            "deviation_analysis": "/file-analysis/",
            "capa_processing": "/capa/details/"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running normally"}