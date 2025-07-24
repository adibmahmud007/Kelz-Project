from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from app.services.utils.ai_analysis import AIAnalyzer
from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.document_ocr import DocumentOCR
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class InvestigationService:
    """
    Service for processing deviation investigations including analysis,
    root cause determination, and corrective action recommendations.
    """
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.transcriber = VoiceTranscriber()
        self.text_extract = DocumentOCRProcessor()
    
    def process_investigation(self, 
                            incident_description: str,
                            background_details: str,
                            deviation_triage: Dict[str, Any],
                            attachments: List[str] = None) -> Dict[str, Any]:
        """
        Process a complete investigation based on deviation report data.
        
        Args:
            incident_description: Description of the incident from transcription
            background_details: Background details from deviation report
            deviation_triage: Triage information selected by user
            attachments: List of attachment file paths
            
        Returns:
            Dict containing complete investigation analysis
        """
        try:
            # Extract attachment content if provided
            attachment_content = []
            if attachments:
                for attachment_path in attachments:
                    content = self.text_extractor.extract_text(attachment_path)
                    if content:
                        attachment_content.append(content)
            
            # Prepare investigation context
            investigation_context = self._prepare_investigation_context(
                incident_description, 
                background_details, 
                deviation_triage, 
                attachment_content
            )
            
            # Generate investigation analysis
            investigation_result = self._generate_investigation_analysis(investigation_context)
            
            return investigation_result
            
        except Exception as e:
            logger.error(f"Error processing investigation: {str(e)}")
            raise Exception(f"Investigation processing failed: {str(e)}")
    
    def _prepare_investigation_context(self, 
                                     incident_description: str,
                                     background_details: str,
                                     deviation_triage: Dict[str, Any],
                                     attachment_content: List[str]) -> str:
        """
        Prepare comprehensive context for AI analysis.
        
        Args:
            incident_description: Incident description
            background_details: Background information
            deviation_triage: Triage assessment data
            attachment_content: Content from attachments
            
        Returns:
            Formatted context string for AI analysis
        """
        context_parts = [
            "=== DEVIATION INVESTIGATION CONTEXT ===\n",
            f"INCIDENT DESCRIPTION:\n{incident_description}\n",
            f"BACKGROUND DETAILS:\n{background_details}\n",
            "\nTRIAGE ASSESSMENT:",
            f"- Deviation Theme: {deviation_triage.get('deviation_theme', 'Not specified')}",
            f"- Impact Assessment: {deviation_triage.get('impact_assessment', 'Not specified')}",
            f"- Product Quality: {deviation_triage.get('product_quality', 'Not specified')}",
            f"- Patient Safety: {deviation_triage.get('patient_safety', 'Not specified')}",
            f"- Regulatory Impact: {deviation_triage.get('regulatory_impact', 'Not specified')}",
            f"- Validation Impact: {deviation_triage.get('validation_impact', 'Not specified')}",
            f"- Criticality: {deviation_triage.get('criticality', 'Not specified')}\n"
        ]
        
        if attachment_content:
            context_parts.append("\nATTACHMENT CONTENT:")
            for i, content in enumerate(attachment_content, 1):
                context_parts.append(f"--- Attachment {i} ---")
                context_parts.append(content[:1000] + "..." if len(content) > 1000 else content)
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_investigation_analysis(self, context: str) -> Dict[str, Any]:
        """
        Generate comprehensive investigation analysis using AI.
        
        Args:
            context: Investigation context for analysis
            
        Returns:
            Dict containing investigation results
        """
        investigation_prompt = f"""
        Based on the following deviation investigation context, provide a comprehensive analysis:

        {context}

        Please provide a detailed investigation analysis in the following JSON format:
        {{
            "background_summary": "Concise summary of the incident background",
            "discussion": {{
                "timeline": "Detailed timeline of events",
                "affected_systems": ["List of affected systems/processes"],
                "initial_findings": "Key initial findings from the investigation"
            }},
            "root_cause_analysis": {{
                "primary_cause": "Main root cause identified",
                "contributing_factors": ["List of contributing factors"],
                "methodology": "Root cause analysis methodology used",
                "evidence": ["Supporting evidence for the root cause"]
            }},
            "final_assessment": {{
                "impact_analysis": "Detailed impact assessment",
                "risk_evaluation": "Risk evaluation and classification",
                "compliance_implications": "Regulatory and compliance implications",
                "recurrence_probability": "Assessment of recurrence likelihood"
            }},
            "capa_recommendations": {{
                "immediate_actions": ["Immediate corrective actions needed"],
                "long_term_actions": ["Long-term preventive actions"],
                "responsible_parties": ["Departments/roles responsible for actions"],
                "timeline": "Recommended timeline for CAPA implementation"
            }},
            "ai_generated_insights": {{
                "pattern_analysis": "Analysis of similar incidents or patterns",
                "risk_mitigation": "Additional risk mitigation suggestions",
                "process_improvements": ["Suggested process improvements"],
                "monitoring_recommendations": ["Ongoing monitoring recommendations"]
            }}
        }}

        Ensure the analysis is thorough, professional, and follows pharmaceutical industry standards for deviation investigations.
        """
        
        try:
            # Use the AI analyzer to process the investigation
            raw_analysis = self.ai_analyzer.analyze_with_prompt(investigation_prompt)
            
            # Parse and structure the response
            investigation_result = self._parse_investigation_response(raw_analysis)
            
            return investigation_result
            
        except Exception as e:
            logger.error(f"Error generating investigation analysis: {str(e)}")
            # Return a fallback structure if AI analysis fails
            return self._get_fallback_investigation_result()
    
    def _parse_investigation_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse AI response and ensure proper structure.
        
        Args:
            raw_response: Raw response from AI analyzer
            
        Returns:
            Structured investigation result
        """
        try:
            import json
            
            # Try to parse as JSON first
            if raw_response.strip().startswith('{'):
                return json.loads(raw_response)
            
            # If not JSON, create structured response from text
            return {
                "background_summary": self._extract_section(raw_response, "background", "summary"),
                "discussion": {
                    "timeline": self._extract_section(raw_response, "timeline", "events"),
                    "affected_systems": self._extract_list_items(raw_response, "affected", "systems"),
                    "initial_findings": self._extract_section(raw_response, "findings", "initial")
                },
                "root_cause_analysis": {
                    "primary_cause": self._extract_section(raw_response, "root cause", "primary"),
                    "contributing_factors": self._extract_list_items(raw_response, "contributing", "factors"),
                    "methodology": self._extract_section(raw_response, "methodology", "analysis"),
                    "evidence": self._extract_list_items(raw_response, "evidence", "support")
                },
                "final_assessment": {
                    "impact_analysis": self._extract_section(raw_response, "impact", "assessment"),
                    "risk_evaluation": self._extract_section(raw_response, "risk", "evaluation"),
                    "compliance_implications": self._extract_section(raw_response, "compliance", "regulatory"),
                    "recurrence_probability": self._extract_section(raw_response, "recurrence", "probability")
                },
                "capa_recommendations": {
                    "immediate_actions": self._extract_list_items(raw_response, "immediate", "actions"),
                    "long_term_actions": self._extract_list_items(raw_response, "long.term", "preventive"),
                    "responsible_parties": self._extract_list_items(raw_response, "responsible", "parties"),
                    "timeline": self._extract_section(raw_response, "timeline", "implementation")
                },
                "ai_generated_insights": {
                    "pattern_analysis": self._extract_section(raw_response, "pattern", "analysis"),
                    "risk_mitigation": self._extract_section(raw_response, "mitigation", "risk"),
                    "process_improvements": self._extract_list_items(raw_response, "improvements", "process"),
                    "monitoring_recommendations": self._extract_list_items(raw_response, "monitoring", "recommendations")
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing investigation response: {str(e)}")
            return self._get_fallback_investigation_result()
    
    def _extract_section(self, text: str, *keywords) -> str:
        """Extract a text section based on keywords."""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Simple extraction logic - can be enhanced
                start_idx = text_lower.find(keyword.lower())
                if start_idx != -1:
                    # Extract following 200 characters as a simple heuristic
                    return text[start_idx:start_idx + 200].strip()
        return "Analysis not available in current response format"
    
    def _extract_list_items(self, text: str, *keywords) -> List[str]:
        """Extract list items based on keywords."""
        # Simple implementation - can be enhanced with better parsing
        items = []
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword.lower() in line_lower for keyword in keywords):
                if '-' in line or '•' in line or line.strip().startswith(('1.', '2.', '3.')):
                    items.append(line.strip())
        return items[:5] if items else ["Items not identified in current analysis"]
    
    def _get_fallback_investigation_result(self) -> Dict[str, Any]:
        """
        Provide fallback investigation structure when AI analysis fails.
        
        Returns:
            Basic investigation structure
        """
        return {
            "background_summary": "Investigation analysis is being processed. Please review manually.",
            "discussion": {
                "timeline": "Timeline analysis pending manual review.",
                "affected_systems": ["System analysis pending"],
                "initial_findings": "Initial findings require manual assessment."
            },
            "root_cause_analysis": {
                "primary_cause": "Root cause analysis in progress.",
                "contributing_factors": ["Contributing factors analysis pending"],
                "methodology": "Standard root cause analysis methodology to be applied.",
                "evidence": ["Evidence collection and analysis pending"]
            },
            "final_assessment": {
                "impact_analysis": "Impact assessment requires detailed review.",
                "risk_evaluation": "Risk evaluation pending.",
                "compliance_implications": "Compliance review required.",
                "recurrence_probability": "Recurrence assessment pending."
            },
            "capa_recommendations": {
                "immediate_actions": ["Immediate containment measures to be determined"],
                "long_term_actions": ["Long-term preventive actions to be defined"],
                "responsible_parties": ["Responsibility assignment pending"],
                "timeline": "CAPA timeline to be established."
            },
            "ai_generated_insights": {
                "pattern_analysis": "Pattern analysis requires historical data review.",
                "risk_mitigation": "Additional risk mitigation strategies to be identified.",
                "process_improvements": ["Process improvement opportunities to be assessed"],
                "monitoring_recommendations": ["Monitoring strategy to be developed"]
            }
        }
    
    def get_investigation_summary(self, investigation_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a concise summary of the investigation results.
        
        Args:
            investigation_data: Complete investigation analysis
            
        Returns:
            Dict containing summary information
        """
        return {
            "summary": investigation_data.get("background_summary", ""),
            "primary_cause": investigation_data.get("root_cause_analysis", {}).get("primary_cause", ""),
            "impact_level": investigation_data.get("final_assessment", {}).get("risk_evaluation", ""),
            "immediate_actions_count": len(investigation_data.get("capa_recommendations", {}).get("immediate_actions", [])),
            "long_term_actions_count": len(investigation_data.get("capa_recommendations", {}).get("long_term_actions", []))
        }