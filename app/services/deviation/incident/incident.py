#!/usr/bin/env python3
"""
Incident Service Module
Handles incident processing, transcription, and AI analysis
"""

import os
import tempfile
from typing import Optional, Tuple
from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.ai_analysis import AIAnalyzer
from incident_schema import IncidentAnalysis, IncidentResponse, IncidentSummaryResponse, ErrorResponse

class IncidentManager:
    """
    Main incident management class that orchestrates transcription and AI analysis
    """
    
    def __init__(self):
        """Initialize transcriber and analyzer"""
        self.transcriber = VoiceTranscriber()
        self.analyzer = AIAnalyzer()
        
    def process_incident_from_audio(self, audio_file_path: str) -> IncidentResponse:
        """
        Process incident from audio file - transcribe and analyze
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            IncidentResponse: Complete incident processing response
        """
        try:
            # Step 1: Transcribe audio
            print("🎤 Starting audio transcription...")
            transcription = self.transcriber.transcribe_audio(audio_file_path)
            
            if not transcription:
                return IncidentResponse(
                    success=False,
                    message="Failed to transcribe audio file",
                    transcription=None,
                    incident_description=None,
                    headline=None,
                    analysis=None
                )
            
            print(f"✅ Transcription completed: {len(transcription)} characters")
            
            # Step 2: Process the transcribed text
            return self.process_incident_from_text(transcription)
            
        except Exception as e:
            print(f"❌ Error processing incident from audio: {str(e)}")
            return IncidentResponse(
                success=False,
                message=f"Error processing incident: {str(e)}",
                transcription=None,
                incident_description=None,
                headline=None,
                analysis=None
            )
    
    def process_incident_from_text(self, transcribed_text: str) -> IncidentResponse:
        """
        Process incident from transcribed text
        
        Args:
            transcribed_text (str): Transcribed text to analyze
            
        Returns:
            IncidentResponse: Complete incident processing response
        """
        try:
            # Step 1: Get incident description and headline
            print("🤖 Generating incident description...")
            incident_description, headline = self._generate_incident_description(transcribed_text)
            
            # Step 2: Get detailed analysis
            print("🔍 Performing detailed incident analysis...")
            analysis_data = self.analyzer.analyze_incident(transcribed_text)
            
            if not analysis_data:
                return IncidentResponse(
                    success=False,
                    message="Failed to analyze incident",
                    transcription=transcribed_text,
                    incident_description=incident_description,
                    headline=headline,
                    analysis=None
                )
            
            # Step 3: Create structured analysis object
            analysis = IncidentAnalysis(
                title=analysis_data.get('title', 'Unknown Incident'),
                who=analysis_data.get('who', 'Not specified'),
                what=analysis_data.get('what', 'Not specified'),
                where=analysis_data.get('where', 'Not specified'),
                immediate_action=analysis_data.get('immediate_action', 'Not specified'),
                quality_concerns=analysis_data.get('quality_concerns', 'Not specified'),
                quality_controls=analysis_data.get('quality_controls', 'Not specified'),
                rca_tool=analysis_data.get('rca_tool', 'Not specified'),
                expected_interim_action=analysis_data.get('expected_interim_action', 'Not specified'),
                capa=analysis_data.get('capa', 'Not specified')
            )
            
            print("✅ Incident analysis completed successfully")
            
            return IncidentResponse(
                success=True,
                message="Incident processed successfully",
                transcription=transcribed_text,
                incident_description=incident_description,
                headline=headline,
                analysis=analysis
            )
            
        except Exception as e:
            print(f"❌ Error processing incident from text: {str(e)}")
            return IncidentResponse(
                success=False,
                message=f"Error processing incident: {str(e)}",
                transcription=transcribed_text,
                incident_description=None,
                headline=None,
                analysis=None
            )
    
    def _generate_incident_description(self, transcribed_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate incident description and headline
        
        Args:
            transcribed_text (str): Transcribed text
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (incident_description, headline)
        """
        try:
            # Use AI analyzer to get summary and generate headline
            summary = self.analyzer.get_summary_analysis(transcribed_text)
            
            if not summary:
                return None, None
            
            # Generate headline from summary
            headline = self._generate_headline(summary)
            
            return summary, headline
            
        except Exception as e:
            print(f"❌ Error generating incident description: {str(e)}")
            return None, None
    
    def _generate_headline(self, incident_description: str) -> Optional[str]:
        """
        Generate a succinct headline from incident description
        
        Args:
            incident_description (str): Full incident description
            
        Returns:
            Optional[str]: Succinct headline
        """
        try:
            # Use AI to generate a headline
            prompt = f"""
Create a succinct, professional headline (maximum 10 words) for this incident:

"{incident_description}"

The headline should be:
- Clear and specific
- Professional tone
- Maximum 10 words
- Capture the essence of the incident

Provide ONLY the headline, no additional text.
"""
            
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.analyzer.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 50,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                headline = result['choices'][0]['message']['content'].strip()
                # Remove quotes if present
                headline = headline.strip('"\'')
                return headline
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error generating headline: {str(e)}")
            return None
    
    def get_incident_summary(self, transcribed_text: str) -> IncidentSummaryResponse:
        """
        Get a quick summary of the incident
        
        Args:
            transcribed_text (str): Transcribed text
            
        Returns:
            IncidentSummaryResponse: Summary response
        """
        try:
            summary = self.analyzer.get_summary_analysis(transcribed_text)
            headline = self._generate_headline(summary) if summary else None
            
            if summary:
                return IncidentSummaryResponse(
                    success=True,
                    message="Summary generated successfully",
                    summary=summary,
                    headline=headline
                )
            else:
                return IncidentSummaryResponse(
                    success=False,
                    message="Failed to generate summary",
                    summary=None,
                    headline=None
                )
                
        except Exception as e:
            print(f"❌ Error getting incident summary: {str(e)}")
            return IncidentSummaryResponse(
                success=False,
                message=f"Error generating summary: {str(e)}",
                summary=None,
                headline=None
            )
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate audio file before processing
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ Audio file not found: {file_path}")
                return False
            
            # Check file size (25MB limit for Whisper)
            file_size = os.path.getsize(file_path)
            if file_size > 25 * 1024 * 1024:
                print(f"❌ File too large: {file_size} bytes (max 25MB)")
                return False
            
            # Check file extension
            valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension not in valid_extensions:
                print(f"❌ Unsupported file format: {file_extension}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating audio file: {str(e)}")
            return False
    
    def process_uploaded_file(self, file_content: bytes, filename: str) -> IncidentResponse:
        """
        Process uploaded file content
        
        Args:
            file_content (bytes): File content
            filename (str): Original filename
            
        Returns:
            IncidentResponse: Processing response
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process the temporary file
                result = self.process_incident_from_audio(tmp_file_path)
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            print(f"❌ Error processing uploaded file: {str(e)}")
            return IncidentResponse(
                success=False,
                message=f"Error processing uploaded file: {str(e)}",
                transcription=None,
                incident_description=None,
                headline=None,
                analysis=None
            )
    
    def display_incident_results(self, response: IncidentResponse):
        """
        Display incident results in a formatted way
        
        Args:
            response (IncidentResponse): Incident response to display
        """
        print("\n" + "="*50)
        print("INCIDENT ANALYSIS RESULTS")
        print("="*50)
        
        if not response.success:
            print(f"❌ Error: {response.message}")
            return
        
        # Display headline
        if response.headline:
            print(f"\n📌 HEADLINE: {response.headline}")
        
        # Display incident description
        if response.incident_description:
            print(f"\n📝 INCIDENT DESCRIPTION:")
            print(f"{response.incident_description}")
        
        # Display detailed analysis
        if response.analysis:
            print(f"\n🔍 DETAILED ANALYSIS:")
            print(f"Title: {response.analysis.title}")
            print(f"Who: {response.analysis.who}")
            print(f"What: {response.analysis.what}")
            print(f"Where: {response.analysis.where}")
            print(f"Immediate Action: {response.analysis.immediate_action}")
            print(f"Quality Concerns: {response.analysis.quality_concerns}")
            print(f"Quality Controls: {response.analysis.quality_controls}")
            print(f"RCA Tool: {response.analysis.rca_tool}")
            print(f"Expected Interim Action: {response.analysis.expected_interim_action}")
            print(f"CAPA: {response.analysis.capa}")
        
        # Display transcription
        if response.transcription:
            print(f"\n🎤 ORIGINAL TRANSCRIPTION:")
            print(f"{response.transcription}")
        
        print(f"\n⏰ Processed at: {response.timestamp}")
        print("="*50)