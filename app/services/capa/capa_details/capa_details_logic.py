from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.ai_analysis import AIAnalyzer
from .capa_details_schema import CAPADetailsResponse, CAPAAnalysisInput
import json
import os
from typing import Optional

class CAPADetailsProcessor:
    """Factory class for processing CAPA details from voice or text input"""
    
    def __init__(self):
        self.transcriber = VoiceTranscriber()
        self.ai_analyzer = AIAnalyzer()
        
    def process_audio_to_capa(self, audio_file_path: str) -> CAPADetailsResponse:
        """Process audio file to generate CAPA details"""
        try:
            # Transcribe audio using the transcription service
            transcribed_text = self.transcriber.transcribe_audio(audio_file_path)
            
            if not transcribed_text:
                raise ValueError("Failed to transcribe audio file")
                
            # Clean up temp file if needed
            if os.path.exists(audio_file_path) and "temp_" in audio_file_path:
                os.remove(audio_file_path)
                
            return self._generate_capa_from_text(transcribed_text)
            
        except Exception as e:
            raise Exception(f"Error processing audio to CAPA: {str(e)}")
    
    def process_text_to_capa(self, text_content: str) -> CAPADetailsResponse:
        """Process text content to generate CAPA details"""
        try:
            return self._generate_capa_from_text(text_content, transcription=None)
        except Exception as e:
            raise Exception(f"Error processing text to CAPA: {str(e)}")
    
    def _generate_capa_from_text(self, text_content: str, transcription: Optional[str] = None) -> CAPADetailsResponse:
        """Generate CAPA details using AI analysis"""
        try:
            # Use the specialized CAPA analysis method
            capa_data = self.ai_analyzer.analyze_capa_requirements(text_content)
            
            if not capa_data:
                # Fallback to basic prompt analysis if specialized method fails
                capa_prompt = self._create_capa_analysis_prompt(text_content)
                ai_response = self.ai_analyzer.analyze_text_with_prompt(capa_prompt)
                capa_data = self._parse_ai_response(ai_response)
            
            if not capa_data:
                raise ValueError("Failed to generate CAPA analysis")
            
            return CAPADetailsResponse(
                transcription=transcription or text_content if transcription else None,
                capa_title=capa_data.get("capa_title", "Generated CAPA"),
                capa_description=capa_data.get("capa_description", ""),
                detailed_actions=capa_data.get("detailed_actions", []),
                document_references=capa_data.get("document_references", []),
                document_sections_to_amend=capa_data.get("document_sections_to_amend", []),
                document_type=capa_data.get("document_type", "Standard Operating Procedure")
            )
            
        except Exception as e:
            raise Exception(f"Error generating CAPA from text: {str(e)}")
    
    def _create_capa_analysis_prompt(self, text_content: str) -> str:
        """Create structured prompt for AI analysis"""
        prompt = f"""
        Analyze the following content and generate a Corrective Action and Preventive Action (CAPA) report:

        Content to analyze:
        {text_content}

        Please provide a structured response in JSON format with the following fields:

        {{
            "capa_title": "Brief heading of CAPA description",
            "capa_description": "Detailed description of the corrective action",
            "detailed_actions": ["Action 1", "Action 2", "Action 3"...],
            "document_references": ["Document ref 1", "Document ref 2"...],
            "document_sections_to_amend": ["Section 1", "Section 2"...],
            "document_type": "Type of document (SOP, Policy, Procedure, etc.)"
        }}

        Requirements:
        1. Generate detailed list of actions from the content
        2. Identify specific document references that need to be updated
        3. Confirm document sections that need to be amended
        4. Determine the appropriate document type as output
        5. Ensure the CAPA title is concise but descriptive
        6. Make the description comprehensive and actionable

        Provide only the JSON response without additional formatting.
        """
        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> dict:
        """Parse AI response and extract CAPA components"""
        try:
            # Try to parse as JSON first
            if ai_response.strip().startswith('{'):
                return json.loads(ai_response)
            
            # If not JSON, create fallback structure
            return self._create_fallback_capa_structure(ai_response)
            
        except json.JSONDecodeError:
            # Fallback parsing if JSON parsing fails
            return self._create_fallback_capa_structure(ai_response)
    
    def _create_fallback_capa_structure(self, response_text: str) -> dict:
        """Create fallback CAPA structure when JSON parsing fails"""
        lines = response_text.split('\n')
        
        return {
            "capa_title": "CAPA Generated from Analysis",
            "capa_description": response_text[:500] + "..." if len(response_text) > 500 else response_text,
            "detailed_actions": [
                "Review and analyze the identified issues",
                "Implement corrective measures",
                "Update relevant documentation",
                "Verify effectiveness of actions"
            ],
            "document_references": [
                "Standard Operating Procedures",
                "Quality Management System"
            ],
            "document_sections_to_amend": [
                "Process Controls",
                "Quality Assurance"
            ],
            "document_type": "Standard Operating Procedure"
        }