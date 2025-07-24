from app.services.utils.document_ocr import DocumentOCR
import os

class FileExtractService:
    """
    Service class for file extraction operations
    """

    @staticmethod
    async def process_file_extract(document_file) -> dict:
        """
        Process uploaded document file using OCR and AI analysis

        Args:
            document_file: Uploaded file object

        Returns:
            dict: Analysis results with AI suggested title and categorized content
        """
        doc_path = f"temp_{document_file.filename}"

        try:
            # Save uploaded file temporarily
            with open(doc_path, "wb") as f:
                f.write(await document_file.read())

            # Process with DocumentOCRProcessor
            processor = DocumentOCR()
            result = processor.process_file(doc_path)

            # Clean up temporary file
            if os.path.exists(doc_path):
                os.remove(doc_path)

            if result.get("success"):
                # Here you would typically use AI analysis to categorize the content
                # For now, returning mock categorized data
                return {
                    "AI suggested Title": "Document Analysis",
                    "Batch records": "Not found in document",
                    "SOP's": "Not found in document",
                    "Forms": "Not found in document",
                    "Interviews": "Not found in document",
                    "Logbooks": "Not found in document",
                    "Email references": "Not found in document",
                    "Certificates": "Not found in document",
                    "processing_info": {
                        "file_type": result.get("file_type"),
                        "text_length": result.get("text_length"),
                        "processing_method": result.get("processing_method")
                    }
                }
            else:
                return {
                    "error": result.get("error", "Processing failed"),
                    "processing_info": result
                }

        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(doc_path):
                os.remove(doc_path)
            raise Exception(f"File processing failed: {str(e)}")

    @staticmethod
    def get_supported_formats():
        """
        Get supported file formats information
        """
        try:
            processor = DocumentOCR()
            return processor.get_supported_formats()
        except Exception as e:
            return {
                "error": str(e),
                "supported_formats": [],
                "google_documentai_available": False
            }
