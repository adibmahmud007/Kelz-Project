from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.deviation.file_extract.file_extract import FileExtractService
from app.services.deviation.file_extract.file_extract_schema import FileExtractResponse

router = APIRouter(prefix="/file_extract", tags=["File Extract"])

@router.post("/", response_model=FileExtractResponse)
async def file_extract(document: UploadFile = File(...)):
    """
    Extract and analyze text from uploaded document using OCR and AI analysis
    
    NOW SUPPORTS ANY FILE FORMAT! Files are automatically converted to PDF if needed.

    Supported formats include:
    - Document formats: PDF, DOCX, DOC, ODT, RTF, TXT, MD
    - Spreadsheet formats: XLSX, XLS, CSV
    - Presentation formats: PPTX, PPT
    - Image formats: JPG, JPEG, PNG, BMP, TIFF, GIF, WEBP
    - And more!

    Processing workflow:
    1. File upload and validation
    2. Automatic conversion to PDF (if needed)
    3. OCR text extraction using Google Document AI
    4. AI analysis and categorization
    5. Cleanup of temporary files

    Returns structured analysis with:
    - AI suggested title
    - Batch records
    - SOP's
    - Forms
    - Interviews
    - Logbooks
    - Email references
    - Certificates
    - Processing metadata
    """
    try:
        # Validate file size (optional - add your limits)
        max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Read file content to check size
        file_content = await document.read()
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {max_file_size // (1024*1024)}MB"
            )
        
        # Reset file position
        await document.seek(0)
        
        # Process the file
        result = await FileExtractService.process_file_extract(document)

        # Convert the result to match the response model
        response_data = {
            "ai_suggested_title": result.get("AI suggested Title", "Document Analysis"),
            "batch_records": result.get("Batch records", "Not found in document"),
            "sops": result.get("SOP's", "Not found in document"),
            "forms": result.get("Forms", "Not found in document"),
            "interviews": result.get("Interviews", "Not found in document"),
            "logbooks": result.get("Logbooks", "Not found in document"),
            "email_references": result.get("Email references", "Not found in document"),
            "certificates": result.get("Certificates", "Not found in document"),
            "error": result.get("error"),
            "processing_info": result.get("processing_info", {})
        }

        return FileExtractResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get comprehensive information about supported file formats
    
    Returns:
    - List of all supported file formats
    - Formats that can be processed directly vs need conversion
    - Available conversion libraries
    - Google Document AI processor information
    """
    try:
        formats_info = FileExtractService.get_supported_formats()
        
        # Add helpful categorization
        if "supported_formats" in formats_info:
            formats_info["format_categories"] = {
                "documents": [f for f in formats_info["supported_formats"] if f in ['.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt', '.md']],
                "spreadsheets": [f for f in formats_info["supported_formats"] if f in ['.xlsx', '.xls', '.csv']],
                "presentations": [f for f in formats_info["supported_formats"] if f in ['.pptx', '.ppt']],
                "images": [f for f in formats_info["supported_formats"] if f in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp']]
            }
        
        return formats_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supported formats: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify service availability
    
    Returns:
    - Service status
    - Available components
    - System readiness
    """
    try:
        from app.services.deviation.file_extract.convert_file import DocumentOCRProcessor
        from app.services.deviation.file_extract.file_extract import FileExtractService
        
        # Check if core components are available
        health_status = {
            "status": "healthy",
            "components": {
                "google_document_ai": False,
                "file_converter": False,
                "ai_analyzer": False
            },
            "timestamp": None
        }
        
        # Test Google Document AI
        try:
            processor = DocumentOCRProcessor()
            health_status["components"]["google_document_ai"] = True
        except Exception as e:
            health_status["components"]["google_document_ai"] = f"Error: {str(e)}"
        
        # Test File Converter
        try:
            from app.services.deviation.file_extract.convert_file import FileConverterService
            converter = FileConverterService()
            health_status["components"]["file_converter"] = True
        except Exception as e:
            health_status["components"]["file_converter"] = f"Error: {str(e)}"
        
        # Test AI Analyzer
        try:
            from app.services.utils.ai_analysis import AIAnalyzer
            analyzer = AIAnalyzer()
            health_status["components"]["ai_analyzer"] = True
        except Exception as e:
            health_status["components"]["ai_analyzer"] = f"Error: {str(e)}"
        
        # Set overall status
        if all(isinstance(v, bool) and v for v in health_status["components"].values()):
            health_status["status"] = "healthy"
        elif any(isinstance(v, bool) and v for v in health_status["components"].values()):
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        # Add timestamp
        from datetime import datetime
        health_status["timestamp"] = datetime.now().isoformat()
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/conversion-status")
async def get_conversion_status():
    """
    Get detailed information about file conversion capabilities
    
    Returns:
    - Available conversion libraries
    - Supported conversion paths
    - Library versions (if available)
    """
    try:
        from app.services.deviation.file_extract.file_extract import FileConverterService
        
        converter = FileConverterService()
        conversion_info = converter.get_supported_formats()
        
        # Add more detailed information
        conversion_status = {
            "conversion_libraries": conversion_info.get("libraries_available", {}),
            "supported_conversions": {},
            "recommendations": []
        }
        
        # Map conversion paths
        supported_formats = conversion_info.get("supported_formats", [])
        conversion_needed = conversion_info.get("conversion_needed", [])
        
        for format_ext in supported_formats:
            if format_ext in conversion_needed:
                conversion_status["supported_conversions"][format_ext] = "converts_to_pdf"
            else:
                conversion_status["supported_conversions"][format_ext] = "direct_processing"
        
        # Add recommendations for missing libraries
        libraries = conversion_info.get("libraries_available", {})
        if not libraries.get("docx2pdf"):
            conversion_status["recommendations"].append("Install docx2pdf for better Word document conversion")
        if not libraries.get("pptx"):
            conversion_status["recommendations"].append("Install python-pptx for PowerPoint support")
        if not libraries.get("pil"):
            conversion_status["recommendations"].append("Install Pillow for image processing")
        
        return conversion_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion status: {str(e)}")
