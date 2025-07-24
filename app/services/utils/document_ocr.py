import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import documentai
from google.api_core.client_options import ClientOptions

# Load environment variables
load_dotenv()

class DocumentOCR:
    def __init__(self):
        """Initialize with environment variables"""
        self.project_id = os.getenv('PROJECT_ID')
        self.location = os.getenv('LOCATION') 
        self.processor_id = os.getenv('PROCESSOR_ID')
        self.processor_version = os.getenv('PROCESSOR_VERSION')
        
        # Set credentials
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    def get_mime_type(self, file_path):
        """Get MIME type from file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png', 
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        extension = Path(file_path).suffix.lower()
        return mime_types.get(extension, 'application/octet-stream')

    def extract_text(self, file_path):
        """Extract text from document using Google Document AI"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type = self.get_mime_type(file_path)
        if mime_type == 'application/octet-stream':
            raise ValueError("Unsupported file type")
        
        # Create client
        client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
        )
        
        # Get processor name
        name = client.processor_version_path(
            self.project_id, self.location, self.processor_id, self.processor_version
        )
        
        # Read file
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Create request
        request = documentai.ProcessRequest(
            name=name,
            raw_document=documentai.RawDocument(
                content=file_content, 
                mime_type=mime_type
            )
        )
        
        # Process document
        result = client.process_document(request=request)
        document = result.document
        if not hasattr(document, 'text') or not document.text.strip():
            print("[WARNING] No text extracted from the document. Check processor type, file content, and configuration.")
        return document.text if hasattr(document, 'text') else ''

    def process_file(self, file_path):
        """Process file and print results"""
        try:
            print(f"Processing: {os.path.basename(file_path)}")
            text = self.extract_text(file_path)
            print(f"Extracted text:\n{text}")
            return text
        except Exception as e:
            print(f"Error: {e}")
            return None
