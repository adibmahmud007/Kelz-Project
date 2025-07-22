#!/usr/bin/env python3
"""
File Conversion Workflow

- file_extract will send any file to file_convert.py.
- file_convert.py will check if the file is a PDF or an image.
- If the file is neither a PDF nor an image, it will convert the file to PDF.
- Image files will not be converted.
"""

import os
import sys
from typing import Optional
from pathlib import Path

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

try:
    from google.cloud import documentai
    GOOGLE_DOCUMENTAI_AVAILABLE = True
except ImportError:
    GOOGLE_DOCUMENTAI_AVAILABLE = False
    print("❌ Google Cloud Document AI not available. Please install google-cloud-documentai")

class DocumentOCRProcessor:
    """
    Document OCR processor that uses Google Cloud Document AI exclusively
    """
    
    def __init__(self):
        """Initialize the Google Document AI processor"""
        if not GOOGLE_DOCUMENTAI_AVAILABLE:
            raise ImportError("Google Cloud Document AI is required but not available")
        
        # Load configuration from environment
        self.project_id = os.getenv('PROJECT_ID')
        self.location = os.getenv('LOCATION', 'eu')
        self.processor_id = os.getenv('PROCESSOR_ID')
        self.processor_version = os.getenv('PROCESSOR_VERSION', 'rc')
        
        if not all([self.project_id, self.processor_id]):
            raise ValueError("PROJECT_ID and PROCESSOR_ID must be set in environment variables")
        
        # Initialize Document AI client
        self.client = documentai.DocumentProcessorServiceClient()
        
        # Build processor name
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )
        
        # Supported formats by Google Document AI
        self.supported_formats = [
            '.pdf', '.gif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp', '.webp'
        ]
        
        print(f"✅ Google Document AI initialized with processor: {self.processor_name}")
    
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
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension not in self.supported_formats:
                print(f"❌ Unsupported file format: {file_extension}")
                print(f"Supported formats: {', '.join(self.supported_formats)}")
                return None
            
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
            print(f"🔄 Processing document with Google Document AI...")
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract text
            extracted_text = document.text
            
            if extracted_text and extracted_text.strip():
                print(f"✅ Text extracted successfully: {len(extracted_text)} characters")
                return extracted_text
            else:
                print("⚠️  No text found in document")
                return "No text detected in document"
                
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {str(e)}")
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
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        
        return mime_types.get(file_extension.lower(), 'application/octet-stream')
    
    def get_supported_formats(self) -> dict:
        """Get list of supported file formats"""
        return {
            "supported_formats": self.supported_formats,
            "processor_info": {
                "project_id": self.project_id,
                "location": self.location,
                "processor_id": self.processor_id,
                "processor_version": self.processor_version
            },
            "google_documentai_available": GOOGLE_DOCUMENTAI_AVAILABLE
        }
    
    def get_document_analysis(self, file_path: str) -> Optional[dict]:
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
                return None
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension not in self.supported_formats:
                print(f"❌ Unsupported file format: {file_extension}")
                return None
            
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
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract comprehensive information
            analysis = {
                "text": document.text,
                "pages": len(document.pages),
                "entities": [],
                "confidence": 0.0
            }
            
            # Extract entities if available
            for entity in document.entities:
                analysis["entities"].append({
                    "type": entity.type_,
                    "mention_text": entity.mention_text,
                    "confidence": entity.confidence
                })
            
            # Calculate average confidence
            if analysis["entities"]:
                analysis["confidence"] = sum(e["confidence"] for e in analysis["entities"]) / len(analysis["entities"])
            
            print(f"✅ Document analysis completed: {len(analysis['entities'])} entities found")
            return analysis
                
        except Exception as e:
            print(f"❌ Error analyzing document {file_path}: {str(e)}")
            return None
