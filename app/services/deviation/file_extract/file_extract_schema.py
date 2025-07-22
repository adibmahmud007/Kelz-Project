from pydantic import BaseModel
from typing import Optional, Dict, Any

class FileExtractResponse(BaseModel):
    """
    Response model for file extraction and analysis
    """
    ai_suggested_title: str
    batch_records: str
    sops: str
    forms: str
    interviews: str
    logbooks: str
    email_references: str
    certificates: str
    error: Optional[str] = None
    processing_info: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }
        schema_extra = {
            "example": {
                "ai_suggested_title": "Quality Control Document Analysis",
                "batch_records": "Found batch records for products A, B, C",
                "sops": "Standard Operating Procedures for manufacturing process",
                "forms": "Quality inspection forms and checklists",
                "interviews": "Not found in document",
                "logbooks": "Production logbook entries from 2024",
                "email_references": "Email correspondence with quality team",
                "certificates": "ISO 9001 certification documents",
                "error": None,
                "processing_info": {
                    "file_type": "pdf",
                    "pages_processed": 5,
                    "processing_time": 2.3
                }
            }
        }
