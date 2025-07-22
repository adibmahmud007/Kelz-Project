from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.utils.ai_analysis import AIAnalyzer
from app.services.utils.transcription import VoiceTranscriber
import os

from app.services.deviation.quality_review.quality_review_router import router as quality_review_router
from app.services.deviation.file_extract.file_extract_router import router as file_extract_router

app = FastAPI(title="Document Analysis and Transcription API")


@app.post("/incident/audio/")
def process_incident_from_audio(audio: UploadFile = File(...)):
    """
    Process an incident report from an uploaded audio file.
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{audio.filename}"
        with open(temp_path, "wb") as f:
            f.write(audio.file.read())

        # Transcribe audio
        transcriber = VoiceTranscriber()
        transcribed_text = transcriber.transcribe_audio(temp_path)
        os.remove(temp_path)

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio.")

        # Analyze the incident
        analyzer = AIAnalyzer()
        incident_data = analyzer.analyze_incident(transcribed_text)
        return {"transcription": transcribed_text, "incident_analysis": incident_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/text/")
def extract_and_analyze_text(file: UploadFile = File(...)):
    """
    Extract and analyze text from an uploaded file.
    """
    try:
        text_content = file.file.read().decode("utf-8", errors="ignore")
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in file.")
        analyzer = AIAnalyzer()
        document_data = analyzer.analyze_document_for_extraction(text_content)
        return {"content_preview": text_content[:200], "document_analysis": document_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quality/audio/")
def perform_quality_review_from_audio(audio: UploadFile = File(...)):
    """
    Perform quality review from an uploaded audio file.
    """
    try:
        temp_path = f"temp_{audio.filename}"
        with open(temp_path, "wb") as f:
            f.write(audio.file.read())
        transcriber = VoiceTranscriber()
        transcribed_text = transcriber.transcribe_audio(temp_path)
        os.remove(temp_path)
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio.")
        analyzer = AIAnalyzer()
        summary = analyzer.get_summary_analysis(transcribed_text)
        return {"transcription": transcribed_text, "quality_review_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/capa/details/audio/")
def process_capa_from_audio(audio: UploadFile = File(...)):
    """
    Process CAPA from audio file
    """
    try:
        # Save and transcribe audio
        temp_path = f"temp_{audio.filename}"
        with open(temp_path, "wb") as f:
            f.write(audio.file.read())
        
        transcriber = VoiceTranscriber()
        transcript = transcriber.transcribe_audio(temp_path)
        os.remove(temp_path)
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio.")
        
        # Analyze for CAPA
        analyzer = AIAnalyzer()
        capa_data = analyzer.analyze_capa(transcript)
        
        return {
            "voice_recording": audio.filename,
            "auto_transcription": transcript,
            "capa_title": capa_data.get("title", ""),
            "capa_description": capa_data.get("description", ""),
            "corrective_actions": capa_data.get("actions", []),
            "document_references": capa_data.get("document_refs", []),
            "document_sections": capa_data.get("sections", []),
            "document_type": capa_data.get("doc_type", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Welcome to the Document Analysis and Transcription API!"}