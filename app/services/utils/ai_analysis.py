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

class AIAnalyzer:
    def __init__(self):
        # Load configuration from environment
        self.openai_api_key = OPENAI_API_KEY
        
        # Validate API key
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def analyze_with_prompt(self, prompt: str) -> str:
        """
        Analyze content with a custom prompt and return the AI's response as a string.
        Enhanced with better error handling and debugging.
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert pharmaceutical deviation investigator with extensive experience in GMP compliance, quality systems, and regulatory requirements. Provide detailed, actionable analysis based on industry best practices.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 4000,
                'temperature': 0.3,
                'top_p': 0.9
            }
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                if not ai_response:
                    return None
                if len(ai_response) < 100:
                    return ai_response
                return ai_response
            elif response.status_code == 429:
                return None
            elif response.status_code == 401:
                return None
            elif response.status_code == 400:
                return None
            else:
                return None
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.RequestException:
            return None
        except json.JSONDecodeError:
            return None
        except Exception:
            import traceback
            return None

    def analyze_incident(self, transcribed_text):
        """
        Analyze transcribed text and extract incident information
        """
        try:
            structured_data = self._get_structured_analysis(transcribed_text)
            if structured_data:
                return structured_data
            else:
                return None
        except Exception as e:
            return None

    def _get_structured_analysis(self, transcribed_text):
        """
        Get structured analysis using improved prompting
        """
        try:
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
            analysis_text = self.analyze_with_prompt(prompt)
            if analysis_text and self._validate_analysis_text(analysis_text):
                incident_data = self._parse_enhanced_response(analysis_text)
                if incident_data and self._validate_analysis(incident_data):
                    return incident_data
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None

    def _validate_analysis_text(self, analysis_text):
        """Validate that the analysis text contains meaningful content"""
        if not analysis_text or len(analysis_text) < 50:
            return False
        required_markers = ['INCIDENT_TITLE:', 'WHO:', 'WHAT:', 'WHERE:']
        found_markers = sum(1 for marker in required_markers if marker in analysis_text)
        return found_markers >= 3

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
            start_marker = "===ANALYSIS START==="
            end_marker = "===ANALYSIS END==="
            if start_marker in analysis_text and end_marker in analysis_text:
                content = analysis_text.split(start_marker)[1].split(end_marker)[0]
            else:
                content = analysis_text
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
                    value = re.sub(r'\n\s*', ' ', value)
                    value = re.sub(r'\s+', ' ', value)
                    incident_data[key] = value
            return incident_data
        except Exception as e:
            return None

    def _validate_analysis(self, incident_data):
        """
        Validate that the analysis contains meaningful information
        """
        if not incident_data:
            return False
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
            return self.analyze_with_prompt(prompt)
        except Exception as e:
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
            analysis_text = self.analyze_with_prompt(prompt)
            if analysis_text:
                capa_data = self._parse_capa_response(analysis_text)
                if capa_data:
                    return capa_data
                else:
                    return None
            else:
                return None
        except Exception as e:
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
            start_marker = "===CAPA ANALYSIS START==="
            end_marker = "===CAPA ANALYSIS END==="
            if start_marker in analysis_text and end_marker in analysis_text:
                content = analysis_text.split(start_marker)[1].split(end_marker)[0]
            else:
                content = analysis_text
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
                    value = re.sub(r'\n\s*', ' ', value)
                    value = re.sub(r'\s+', ' ', value)
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
            return None

    def analyze_investigation_context(self, context: str) -> dict:
        """
        Specialized method for investigation context analysis.
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
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "analysis": response,
                    "status": "text_response",
                    "requires_manual_parsing": True
                }
        except Exception as e:
            return {
                "analysis": f"Investigation analysis failed: {str(e)}",
                "status": "error"
            }

    @staticmethod
    def analyze_prompt(prompt):
        """
        Generic method to analyze any prompt using OpenAI
        """
        try:
            analyzer = AIAnalyzer()
            response_text = analyzer.analyze_with_prompt(prompt)
            if response_text:
                return {
                    "analysis": response_text,
                    "status": "success"
                }
            else:
                return {
                    "analysis": "Analysis failed - no response received",
                    "status": "error"
                }
        except Exception as e:
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "status": "error"
            }
