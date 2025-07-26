import json
import re
from app.services.utils.document_ocr import DocumentOCR
from app.services.utils.ai_analysis import AIAnalyzer

class FileExtractService:
    @staticmethod
    def extract_and_analyze(file_path: str) -> dict:
        # Step 1: Extract text
        ocr = DocumentOCR()
        extracted_text = ocr.extract_text(file_path)
        if not extracted_text or not extracted_text.strip():
            return {
                "error": "No text could be extracted from the document.",
                "extracted_text": "",
                "document_analysis": {},
            }

        # Step 2: AI analysis with explicit title generation
        ai = AIAnalyzer()
        prompt = f"""
You are an expert document analyst. Analyze the following text and extract the following fields as a JSON object:
- 'AI suggested Title': Generate a concise and descriptive title for the document based on its content.
- 'Batch records'
- 'SOP's'
- 'Forms'
- 'Interviews'
- 'Logbooks'
- 'Email references'
- 'Certificates'

TEXT TO ANALYZE:
{extracted_text}

Return ONLY a valid JSON object with these exact keys (no extra text, no explanation). If a field is not found, use 'Not found in document'.
"""
        ai_response = ai.analyze_with_prompt(prompt)
        print("AI RAW RESPONSE:", ai_response)
        ai_result = {}
        if ai_response:
            # Try to extract JSON block if extra text is present
            json_match = re.search(r'(\{[\s\S]*\})', ai_response)
            if json_match:
                try:
                    ai_result = json.loads(json_match.group(1))
                except Exception:
                    ai_result = {}
            else:
                try:
                    ai_result = json.loads(ai_response)
                except Exception:
                    ai_result = {}

        def ensure_string(val):
            if isinstance(val, list):
                return "; ".join(str(v) for v in val)
            return str(val) if val is not None else "Not found in document"

        # Step 3: Structure the response
        return {
            "extracted_text": extracted_text,
            "document_analysis": {
                "AI suggested Title": ensure_string(ai_result.get("AI suggested Title", "Not found in document")),
                "Batch records": ensure_string(ai_result.get("Batch records", "Not found in document")),
                "SOP's": ensure_string(ai_result.get("SOP's", "Not found in document")),
                "Forms": ensure_string(ai_result.get("Forms", "Not found in document")),
                "Interviews": ensure_string(ai_result.get("Interviews", "Not found in document")),
                "Logbooks": ensure_string(ai_result.get("Logbooks", "Not found in document")),
                "Email references": ensure_string(ai_result.get("Email references", "Not found in document")),
                "Certificates": ensure_string(ai_result.get("Certificates", "Not found in document")),
            }
        }
