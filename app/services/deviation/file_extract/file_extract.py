#!/usr/bin/env python3
"""
Google Document AI OCR Processor Module
Handles text extraction from various document formats using Google Cloud Document AI
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import json

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

try:
    from google.cloud import documentai
    from google.api_core import exceptions as google_exceptions
    GOOGLE_DOCUMENTAI_AVAILABLE = True
except ImportError as e:
    GOOGLE_DOCUMENTAI_AVAILABLE = False
    print(f"❌ Google Cloud Document AI not available: {e}")
    print("Please install: pip install google-cloud-documentai")

class DocumentOCRProcessor:
    """
    Document OCR processor that uses Google Cloud Document AI exclusively
    """
    def __init__(self):
        """Initialize the Google Document AI processor"""
        if not GOOGLE_DOCUMENTAI_AVAILABLE:
            raise ImportError("Google Cloud Document AI is required but not available")

        # Load configuration from environment with validation
        self.project_id = os.getenv('PROJECT_ID') or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = os.getenv('LOCATION', 'us')  # Changed default from 'eu' to 'us'
        self.processor_id = os.getenv('PROCESSOR_ID')
        self.processor_version = os.getenv('PROCESSOR_VERSION', 'rc')

        # Validate required environment variables
        missing_vars = []
        if not self.project_id:
            missing_vars.append('PROJECT_ID or GOOGLE_CLOUD_PROJECT')
        if not self.processor_id:
            missing_vars.append('PROCESSOR_ID')
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        try:
            # Initialize Document AI client with explicit client options if needed
            client_options = None
            if self.location != 'us':
                # For non-US locations, we need to specify the API endpoint
                api_endpoint = f"{self.location}-documentai.googleapis.com"
                from google.api_core import ClientOptions
                client_options = ClientOptions(api_endpoint=api_endpoint)
            self.client = documentai.DocumentProcessorServiceClient(
                client_options=client_options
            )
            # Build processor name
            self.processor_name = self.client.processor_path(
                self.project_id, self.location, self.processor_id
            )
            # Test the connection by attempting to get processor info
            try:
                processor_info = self.client.get_processor(name=self.processor_name)
                print(f"✅ Connected to processor: {processor_info.display_name}")
            except google_exceptions.GoogleAPICallError as e:
                print(f"⚠️ Warning: Could not verify processor connection: {e}")
                print("This might be due to permissions or processor configuration")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Document AI client: {e}")

        # Supported formats by Google Document AI
        self.supported_formats = [
            '.pdf', '.gif', '.tiff', '.tif', '.jpg', '.jpeg', '.png', '.bmp', '.webp'
        ]
        print(f"✅ Google Document AI initialized")
        print(f"  Project ID: {self.project_id}")
        print(f"  Location: {self.location}")
        print(f"  Processor ID: {self.processor_id}")
        print(f"  Processor Name: {self.processor_name}")

    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if the file format is supported for OCR processing
        Args:
            file_path (str): Path to the file
        Returns:
            bool: True if format is supported
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to process a file and return structured results
        Args:
            file_path (str): Path to the file to process
        Returns:
            Dict[str, Any]: Processing results with extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "content_preview": None,
                    "document_analysis": None
                }
            file_extension = Path(file_path).suffix.lower()
            # Check if this is a supported format for OCR
            if not self.is_supported_format(file_path):
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_extension}",
                    "supported_formats": self.supported_formats,
                    "content_preview": None,
                    "document_analysis": None
                }
            # For supported formats, extract text using Document AI
            print(f"🔄 Processing {file_extension} file with Google Document AI...")
            # Extract text
            extracted_text = self.extract_text_from_document(file_path)
            # Get detailed analysis
            document_analysis = self.get_document_analysis(file_path)
            if extracted_text:
                return {
                    "success": True,
                    "file_type": file_extension,
                    "extracted_text": extracted_text,
                    "content_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                    "document_analysis": document_analysis,
                    "text_length": len(extracted_text),
                    "processing_method": "google_document_ai"
                }
            else:
                return {
                    "success": False,
                    "error": "Could not extract text from document",
                    "file_type": file_extension,
                    "content_preview": None,
                    "document_analysis": document_analysis
                }
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_preview": None,
                "document_analysis": None
            }

    def extract_text_from_document(self, file_path: str) -> Optional[str]:
        """
        Extract text from a document file using Google Document AI
        Args:
            file_path (str): Path to the document file
        Returns:
            Optional[str]: Extracted text or None if extraction failed
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return None
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()
            if file_extension not in self.supported_formats:
                print(f"❌ Unsupported file format: {file_extension}")
                print(f"Supported formats: {', '.join(self.supported_formats)}")
                return None
            # Check file size (Document AI has limits)
            file_size = os.path.getsize(file_path)
            max_size = 20 * 1024 * 1024  # 20MB limit for Document AI
            if file_size > max_size:
                print(f"❌ File too large: {file_size} bytes (max: {max_size} bytes)")
                return None
            print(f"📁 Processing file: {file_path}")
            print(f"📊 File size: {file_size} bytes")
            print(f"📋 File extension: {file_extension}")
            # Read the file in binary mode
            with open(file_path, 'rb') as file:
                file_content = file.read()
            if not file_content:
                print("❌ File is empty")
                return None
            # Determine MIME type
            mime_type = self._get_mime_type(file_extension)
            print(f"🔍 MIME type: {mime_type}")
            # Create the document object
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            # Create the request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            # Process the document
            print(f"🔄 Processing document with Google Document AI...")
            try:
                result = self.client.process_document(request=request)
                document = result.document
                # Extract text
                extracted_text = document.text
                if extracted_text and extracted_text.strip():
                    print(f"✅ Text extracted successfully: {len(extracted_text)} characters")
                    return extracted_text
                else:
                    print("⚠️ No text found in document")
                    return "No text detected in document"
            except google_exceptions.GoogleAPICallError as e:
                print(f"❌ Google API Error: {e}")
                if "PERMISSION_DENIED" in str(e):
                    print("💡 Check if your service account has the correct permissions")
                elif "NOT_FOUND" in str(e):
                    print("💡 Check if your processor ID and location are correct")
                elif "QUOTA_EXCEEDED" in str(e):
                    print("💡 You have exceeded your API quota")
                return None
            except Exception as e:
                print(f"❌ Error extracting text from {file_path}: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _get_mime_type(self, file_extension: str) -> str:
        """
        Get MIME type based on file extension
        Args:
            file_extension (str): File extension (with dot)
        Returns:
            str: MIME type
        """
        mime_types = {
            '.pdf': 'application/pdf',
            '.gif': 'image/gif',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(file_extension.lower(), 'application/octet-stream')

    def get_supported_formats(self) -> Dict[str, Any]:
        """Get list of supported file formats"""
        return {
            "supported_formats": self.supported_formats,
            "processor_info": {
                "project_id": self.project_id,
                "location": self.location,
                "processor_id": self.processor_id,
                "processor_version": self.processor_version,
                "processor_name": self.processor_name
            },
            "google_documentai_available": GOOGLE_DOCUMENTAI_AVAILABLE
        }

    def get_document_analysis(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed document analysis including entities and structure
        Args:
            file_path (str): Path to the document file
        Returns:
            Optional[dict]: Document analysis results
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return {"error": "File not found", "exception": True}
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in self.supported_formats:
                print(f"❌ Unsupported file format: {file_extension}")
                return {"error": f"Unsupported file format: {file_extension}", "exception": True}
            # Read the file
            with open(file_path, 'rb') as file:
                file_content = file.read()
            # Determine MIME type
            mime_type = self._get_mime_type(file_extension)
            # Create the document object
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            # Create the request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            # Process the document
            print(f"🔄 Analyzing document with Google Document AI...")
            try:
                result = self.client.process_document(request=request)
                document = result.document
            except google_exceptions.GoogleAPICallError as e:
                print(f"❌ Google API Error: {e}")
                return {"error": str(e), "api_error": True}
            except Exception as e:
                print(f"❌ Unexpected error from Document AI: {e}")
                return {"error": str(e), "api_error": True}
            # Extract comprehensive information
            analysis = {
                "text": document.text,
                "pages": len(document.pages) if document.pages else 0,
                "entities": [],
                "confidence": 0.0,
                "page_info": []
            }
            # Extract page information
            for i, page in enumerate(document.pages):
                page_info = {
                    "page_number": i + 1,
                    "width": page.dimension.width if page.dimension else 0,
                    "height": page.dimension.height if page.dimension else 0,
                    "blocks": len(page.blocks) if page.blocks else 0,
                    "paragraphs": len(page.paragraphs) if page.paragraphs else 0,
                    "lines": len(page.lines) if page.lines else 0,
                    "tokens": len(page.tokens) if page.tokens else 0
                }
                analysis["page_info"].append(page_info)
            # Extract entities if available
            for entity in document.entities:
                entity_info = {
                    "type": entity.type_,
                    "mention_text": entity.mention_text,
                    "confidence": entity.confidence,
                    "normalized_value": getattr(entity, 'normalized_value', None)
                }
                analysis["entities"].append(entity_info)
            # Calculate average confidence
            if analysis["entities"]:
                analysis["confidence"] = sum(e["confidence"] for e in analysis["entities"]) / len(analysis["entities"])
            print(f"✅ Document analysis completed:")
            print(f"  Pages: {analysis['pages']}")
            print(f"  Entities: {len(analysis['entities'])}")
            print(f"  Confidence: {analysis['confidence']:.2f}")
            return analysis
        except Exception as e:
            print(f"❌ Error analyzing document {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "exception": True}

    def test_connection(self) -> bool:
        """
        Test the connection to Google Document AI
        Returns:
            bool: True if connection is successful
        """
        try:
            # Try to get processor information
            processor_info = self.client.get_processor(name=self.processor_name)
            print(f"✅ Connection test successful")
            print(f"  Processor: {processor_info.display_name}")
            print(f"  Type: {processor_info.type_}")
            print(f"  State: {processor_info.state}")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

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
            processor = DocumentOCRProcessor()
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
            processor = DocumentOCRProcessor()
            return processor.get_supported_formats()
        except Exception as e:
            return {
                "error": str(e),
                "supported_formats": [],
                "google_documentai_available": GOOGLE_DOCUMENTAI_AVAILABLE
            }

def main():
    """
    Main function to demonstrate usage
    """
    if len(sys.argv) < 2:
        print("Usage: python file_extract.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    try:
        processor = DocumentOCRProcessor()
        # Process the file
        result = processor.process_file(file_path)
        # Print results as JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "content_preview": None,
            "document_analysis": None
        }
        print(json.dumps(error_result, indent=2))

