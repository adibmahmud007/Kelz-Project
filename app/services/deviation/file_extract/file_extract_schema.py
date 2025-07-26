from pydantic import BaseModel

class DocumentAnalysis(BaseModel):
    AI_suggested_Title: str
    Batch_records: str
    SOP_s: str
    Forms: str
    Interviews: str
    Logbooks: str
    Email_references: str
    Certificates: str

class FileExtractResponse(BaseModel):
    status: str
    filename: str
    file_type: str
    extracted_content: str
    document_analysis: DocumentAnalysis
    message: str
