from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os
from app.services.deviation.file_extract.file_extract import FileExtractService
from app.services.deviation.file_extract.file_extract_schema import FileExtractResponse, DocumentAnalysis

router = APIRouter()

@router.post("/text/analyze/text", response_model=FileExtractResponse, tags=["deviation"])
async def analyze_file(file: UploadFile = File(...)):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        result = FileExtractService.extract_and_analyze(temp_file_path)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        doc_analysis = result["document_analysis"]
        response = {
            "status": "success",
            "filename": file.filename,
            "file_type": file.content_type,
            "extracted_content": result["extracted_text"],
            "document_analysis": {
                "AI_suggested_Title": doc_analysis.get("AI suggested Title"),
                "Batch_records": doc_analysis.get("Batch records"),
                "SOP_s": doc_analysis.get("SOP's"),
                "Forms": doc_analysis.get("Forms"),
                "Interviews": doc_analysis.get("Interviews"),
                "Logbooks": doc_analysis.get("Logbooks"),
                "Email_references": doc_analysis.get("Email references"),
                "Certificates": doc_analysis.get("Certificates"),
            },
            "message": "File analysis completed successfully"
        }
        return response
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
