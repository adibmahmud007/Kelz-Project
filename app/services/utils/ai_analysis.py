#!/usr/bin/env python3
"""
Enhanced AI Analysis Module
Improved incident analysis with better prompting and parsing
"""

import requests
import json
import re
import os
import sys

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

from app.config.config import OPENAI_API_KEY


# Placeholder for AI analysis logic
class AIAnalyzer:
    def __init__(self):
        # Load configuration from environment
        self.openai_api_key = OPENAI_API_KEY
        
        # Validate API key
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def analyze_incident(self, transcribed_text):
        """
        Analyze transcribed text and extract incident information
        
        Args:
            transcribed_text (str): The transcribed text from audio
            
        Returns:
            dict: Structured incident information or None if failed
        """
        try:
            # Get structured analysis
            structured_data = self._get_structured_analysis(transcribed_text)
            
            if structured_data:
                return structured_data
            else:
                print("❌ Structured analysis failed")
                return None
                
        except Exception as e:
            print(f"❌ Error during AI analysis: {str(e)}")
            return None
    
    def _get_structured_analysis(self, transcribed_text):
        """
        Get structured analysis using improved prompting
        """
        try:
            # Enhanced prompt with better instructions
            prompt = f"""
You are an expert incident analyst. Analyze the following transcript and extract incident information. 

IMPORTANT: Generate a descriptive title based on the content, don't just say "Incident Report".

Please provide your analysis in this EXACT format (copy the structure exactly):

===ANALYSIS START===
INCIDENT_TITLE: [Generate a specific, descriptive title based on what happened]
WHO: [People involved, their roles, departments mentioned]
WHAT: [Detailed description of what happened, sequence of events]
WHERE: [Location, department, facility, or area where incident occurred]
IMMEDIATE_ACTION: [What was done immediately after the incident]
QUALITY_CONCERNS: [Quality issues, potential impacts on products/services]
QUALITY_CONTROLS: [Quality control measures that failed or were bypassed]
RCA_TOOL: [Recommend appropriate root cause analysis method]
EXPECTED_INTERIM_ACTION: [Actions needed to prevent immediate recurrence]
CAPA: [Corrective and Preventive Actions needed]
===ANALYSIS END===

TRANSCRIPT TO ANALYZE:
"{transcribed_text}"

INSTRUCTIONS:
- Be specific and detailed in your analysis
- If information is not available, write "Not specified in transcript"
- Generate a meaningful title that describes the actual incident
- Focus on extracting facts from the transcript
- Provide actionable recommendations for RCA_TOOL, EXPECTED_INTERIM_ACTION, and CAPA
"""
            
            # Use OpenAI API for analysis
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Use OpenAI GPT-4o model
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 3000,
                'temperature': 0.2  # Lower temperature for more consistent output
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content'].strip()
                
                # Parse the structured response
                incident_data = self._parse_enhanced_response(analysis_text)
                
                if incident_data and self._validate_analysis(incident_data):
                    print(f"✅ Analysis successful with OpenAI GPT-4o model")
                    return incident_data
                else:
                    print(f"⚠️ Analysis parsing failed with OpenAI GPT-4o model")
                    return None
            else:
                print(f"❌ API Error with OpenAI GPT-4o: {response.status_code}")
                if response.status_code == 429:
                    print("⏳ Rate limit hit, try again later...")
                return None
                
        except Exception as e:
            print(f"❌ Error in structured analysis: {str(e)}")
            return None
    
    def _parse_enhanced_response(self, analysis_text):
        """
        Parse the enhanced AI response with better error handling
        """
        try:
            incident_data = {
                'title': '',
                'who': '',
                'what': '',
                'where': '',
                'immediate_action': '',
                'quality_concerns': '',
                'quality_controls': '',
                'rca_tool': '',
                'expected_interim_action': '',
                'capa': ''
            }
            
            # Extract content between markers if present
            start_marker = "===ANALYSIS START==="
            end_marker = "===ANALYSIS END==="
            
            if start_marker in analysis_text and end_marker in analysis_text:
                content = analysis_text.split(start_marker)[1].split(end_marker)[0]
            else:
                content = analysis_text
            
            # Parse using regex for more robust extraction
            patterns = {
                'title': r'INCIDENT_TITLE:\s*(.+?)(?=\n\w+:|$)',
                'who': r'WHO:\s*(.+?)(?=\n\w+:|$)',
                'what': r'WHAT:\s*(.+?)(?=\n\w+:|$)',
                'where': r'WHERE:\s*(.+?)(?=\n\w+:|$)',
                'immediate_action': r'IMMEDIATE_ACTION:\s*(.+?)(?=\n\w+:|$)',
                'quality_concerns': r'QUALITY_CONCERNS:\s*(.+?)(?=\n\w+:|$)',
                'quality_controls': r'QUALITY_CONTROLS:\s*(.+?)(?=\n\w+:|$)',
                'rca_tool': r'RCA_TOOL:\s*(.+?)(?=\n\w+:|$)',
                'expected_interim_action': r'EXPECTED_INTERIM_ACTION:\s*(.+?)(?=\n\w+:|$)',
                'capa': r'CAPA:\s*(.+?)(?=\n\w+:|$)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the value
                    value = re.sub(r'\n\s*', ' ', value)  # Replace newlines with spaces
                    value = re.sub(r'\s+', ' ', value)    # Normalize whitespace
                    incident_data[key] = value
            
            return incident_data
            
        except Exception as e:
            print(f"❌ Error parsing enhanced response: {str(e)}")
            return None
    
    def _validate_analysis(self, incident_data):
        """
        Validate that the analysis contains meaningful information
        """
        if not incident_data:
            return False
        
        # Check if at least title and what are filled with meaningful content
        title = incident_data.get('title', '').strip()
        what = incident_data.get('what', '').strip()
        
        if not title or title == 'N/A' or len(title) < 5:
            return False
        
        if not what or what == 'N/A' or len(what) < 10:
            return False
        
        return True
    
    def get_summary_analysis(self, transcribed_text):
        """
        Get a quick summary analysis of the incident
        """
        try:
            prompt = f"""
Provide a brief 2-3 sentence summary of this incident:

"{transcribed_text}"

Focus on: what happened, who was involved, and the key concern.
"""
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
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
                'max_tokens': 300,
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
                return result['choices'][0]['message']['content'].strip()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting summary: {str(e)}")
            return None

    
    def analyze_capa(self, transcript):
        """
        Analyze transcript for CAPA information
        """
        try:
            prompt = f"""
You are an expert quality analyst. Analyze the following transcript and extract CAPA (Corrective and Preventive Action) information.

Please provide your analysis in this EXACT format (copy the structure exactly):

===CAPA ANALYSIS START===
CAPA_TITLE: [Generate a brief, descriptive heading of the CAPA based on the transcript]
CAPA_DESCRIPTION: [Generate detailed list of actions from transcript]
CORRECTIVE_ACTIONS: [List specific corrective actions to be taken]
DOCUMENT_REFERENCES: [Identify specific document references to be updated]
DOCUMENT_SECTIONS: [Confirm document sections to be amended]
DOCUMENT_TYPE: [Confirm document type - SOP, Policy, Manual, Form, etc.]
===CAPA ANALYSIS END===

TRANSCRIPT TO ANALYZE:
"{transcript}"

INSTRUCTIONS:
- Generate a brief but descriptive CAPA title
- Extract detailed corrective actions from the transcript
- Identify any documents mentioned that need updating
- Specify sections within documents that require changes
- Determine the type of documents referenced
- If information is not available, write "Not specified in transcript"
"""
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
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
                'max_tokens': 2000,
                'temperature': 0.2
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content'].strip()
                
                # Parse the structured response
                capa_data = self._parse_capa_response(analysis_text)
                
                if capa_data:
                    print(f"✅ CAPA analysis successful with OpenAI GPT-4o model")
                    return capa_data
                else:
                    print(f"⚠️ CAPA analysis parsing failed with OpenAI GPT-4o model")
                    return None
            else:
                print(f"❌ API Error with OpenAI GPT-4o: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error in CAPA analysis: {str(e)}")
            return None

    def _parse_capa_response(self, analysis_text):
        """
        Parse the CAPA AI response
        """
        try:
            capa_data = {
                'title': '',
                'description': '',
                'actions': [],
                'document_refs': [],
                'sections': [],
                'doc_type': ''
            }
            
            # Extract content between markers if present
            start_marker = "===CAPA ANALYSIS START==="
            end_marker = "===CAPA ANALYSIS END==="
            
            if start_marker in analysis_text and end_marker in analysis_text:
                content = analysis_text.split(start_marker)[1].split(end_marker)[0]
            else:
                content = analysis_text
            
            # Parse using regex
            patterns = {
                'title': r'CAPA_TITLE:\s*(.+?)(?=\n\w+:|$)',
                'description': r'CAPA_DESCRIPTION:\s*(.+?)(?=\n\w+:|$)',
                'actions': r'CORRECTIVE_ACTIONS:\s*(.+?)(?=\n\w+:|$)',
                'document_refs': r'DOCUMENT_REFERENCES:\s*(.+?)(?=\n\w+:|$)',
                'sections': r'DOCUMENT_SECTIONS:\s*(.+?)(?=\n\w+:|$)',
                'doc_type': r'DOCUMENT_TYPE:\s*(.+?)(?=\n\w+:|$)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the value
                    value = re.sub(r'\n\s*', ' ', value)  # Replace newlines with spaces
                    value = re.sub(r'\s+', ' ', value)    # Normalize whitespace
                    
                    # For lists, split by common delimiters
                    if key in ['actions', 'document_refs', 'sections'] and value:
                        if ',' in value:
                            capa_data[key] = [item.strip() for item in value.split(',')]
                        elif '\n' in value:
                            capa_data[key] = [item.strip() for item in value.split('\n') if item.strip()]
                        else:
                            capa_data[key] = [value]
                    else:
                        capa_data[key] = value
            
            return capa_data
            
        except Exception as e:
            print(f"❌ Error parsing CAPA response: {str(e)}")
            return None

    def analyze_with_prompt(self, prompt: str) -> str:
        """
        Analyze content with a custom prompt and return the AI's response as a string.
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.2
            }
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error in analyze_with_prompt: {str(e)}")
            return None

    def analyze_investigation_context(self, context: str) -> dict:
        """
        Specialized method for investigation context analysis.
        
        Args:
            context: Investigation context string
            
        Returns:
            Dictionary with investigation analysis
        """
        investigation_prompt = f"""
        Analyze the following deviation investigation context and provide comprehensive insights:
        
        {context}
        
        Please provide analysis covering:
        1. Background summary
        2. Timeline and affected systems
        3. Root cause analysis
        4. Impact assessment
        5. Corrective and preventive action recommendations
        6. Risk evaluation and compliance implications
        
        Format the response as a structured JSON analysis suitable for pharmaceutical deviation investigations.
        
        Use this structure:
        {{
            "background_summary": "Investigation analysis based on provided context and deviation data",
            "discussion": {{
                "timeline": "Event timeline constructed from available information",
                "affected_systems": ["Systems identified from context analysis"],
                "initial_findings": "Preliminary findings based on incident description and background"
            }},
            "root_cause_analysis": {{
                "primary_cause": "Root cause identified through systematic analysis",
                "contributing_factors": ["Contributing factors derived from context"],
                "methodology": "Structured root cause analysis methodology applied",
                "evidence": ["Evidence gathered from provided documentation"]
            }},
            "final_assessment": {{
                "impact_analysis": "Comprehensive impact assessment based on triage data",
                "risk_evaluation": "Risk evaluation considering all factors",
                "compliance_implications": "Regulatory and compliance considerations",
                "recurrence_probability": "Likelihood assessment of similar incidents"
            }},
            "capa_recommendations": {{
                "immediate_actions": ["Immediate corrective actions recommended"],
                "long_term_actions": ["Long-term preventive measures suggested"],
                "responsible_parties": ["Recommended responsible parties"],
                "timeline": "Suggested implementation timeline"
            }},
            "ai_generated_insights": {{
                "pattern_analysis": "Analysis of patterns and trends",
                "risk_mitigation": "Additional risk mitigation strategies",
                "process_improvements": ["Process improvement recommendations"],
                "monitoring_recommendations": ["Ongoing monitoring suggestions"]
            }}
        }}
        """
        
        try:
            response = self.analyze_with_prompt(investigation_prompt)
            
            # Try to parse as JSON first
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If response isn't valid JSON, return structured dict
                return {
                    "analysis": response,
                    "status": "text_response",
                    "requires_manual_parsing": True
                }
                
        except Exception as e:
            print(f"❌ Error in investigation analysis: {str(e)}")
            return {
                "analysis": f"Investigation analysis failed: {str(e)}",
                "status": "error"
            }

    @staticmethod
    def analyze_prompt(prompt):
        """
        Generic method to analyze any prompt using OpenAI

        Args:
            prompt (str): The prompt to analyze

        Returns:
            dict: Analysis results
        """
        try:
            analyzer = AIAnalyzer()

            headers = {
                "Authorization": f"Bearer {analyzer.openai_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert analyst. Analyze the provided content and return structured information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                # Return structured response
                return {
                    "analysis": analysis_text,
                    "status": "success"
                }
            else:
                print(f"❌ API Error with OpenAI GPT-4o: {response.status_code}")
                return {
                    "analysis": "Analysis failed due to API error",
                    "status": "error",
                    "error_code": response.status_code
                }

        except Exception as e:
            print(f"❌ Error in analyze_prompt: {str(e)}")
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "status": "error"
            }