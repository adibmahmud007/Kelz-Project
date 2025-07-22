from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .capa_details_logic import CAPADetailsProcessor
from .capa_details_schema import CAPADetailsRequest, CAPADetailsResponse
import tempfile
import os

router = APIRouter(prefix="/capa", tags=["CAPA Details"])

class CAPADetailsRouter:
    """Router class for CAPA details endpoints"""
    
    def __init__(self):
        self.processor = CAPADetailsProcessor()
    
    def setup_routes(self) -> APIRouter:
        """Setup and return configured router"""
        
        @router.post("/audio/", response_model=CAPADetailsResponse)
        async def process_capa_from_audio(audio: UploadFile = File(...)):
            """
            Generate CAPA details from uploaded audio file.
            
            - **audio**: Audio file containing voice recording for CAPA analysis
            
            Returns:
            - Transcribed text
            - CAPA title and description
            - Detailed action items
            - Document references and sections to amend
            - Document type classification
            """
            return self._handle_audio_processing(audio)
        
        @router.post("/text/", response_model=CAPADetailsResponse)
        async def process_capa_from_text(file: UploadFile = File(...)):
            """
            Generate CAPA details from uploaded text file.
            
            - **file**: Text file containing content for CAPA analysis
            
            Returns:
            - CAPA title and description
            - Detailed action items
            - Document references and sections to amend
            - Document type classification
            """
            return self._handle_text_processing(file)
        
        @router.post("/direct-text/", response_model=CAPADetailsResponse)
        async def process_capa_from_direct_text(request: CAPADetailsRequest):
            """
            Generate CAPA details from direct text input.
            
            - **request**: Request containing text content for analysis
            
            Returns:
            - CAPA title and description
            - Detailed action items
            - Document references and sections to amend
            - Document type classification
            """
            return self._handle_direct_text_processing(request)
        
        return router
    
    def _handle_audio_processing(self, audio: UploadFile) -> JSONResponse:
        """Handle audio file processing for CAPA generation"""
        try:
            # Validate file type
            if not audio.content_type or not audio.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Please upload an audio file."
                )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{audio.filename}") as temp_file:
                temp_file.write(audio.file.read())
                temp_path = temp_file.name
            
            # Process audio to CAPA
            result = self.processor.process_audio_to_capa(temp_path)
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "CAPA details generated successfully from audio",
                    "data": result.dict()
                }
            )
            
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    
    def _handle_text_processing(self, file: UploadFile) -> JSONResponse:
        """Handle text file processing for CAPA generation"""
        try:
            # Read and decode text content
            text_content = file.file.read().decode("utf-8", errors="ignore")
            
            if not text_content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No text content found in file."
                )
            
            # Process text to CAPA
            result = self.processor.process_text_to_capa(text_content)
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "CAPA details generated successfully from text",
                    "data": result.dict()
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")
    
    def _handle_direct_text_processing(self, request: CAPADetailsRequest) -> JSONResponse:
        """Handle direct text input processing for CAPA generation"""
        try:
            if not request.text_content or not request.text_content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Text content is required for processing."
                )
            
            # Process text to CAPA
            result = self.processor.process_text_to_capa(request.text_content)
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "CAPA details generated successfully from direct text",
                    "data": result.dict()
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Direct text processing failed: {str(e)}")

# Create router instance
capa_router = CAPADetailsRouter()
router = capa_router.setup_routes()