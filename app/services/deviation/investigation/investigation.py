import re
import json
from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.ai_analysis import AIAnalyzer

class InvestigationService:
    @staticmethod
    def analyze_voice_file(voice_file_path: str) -> dict:
        # Step 1: Transcribe the voice file
        transcriber = VoiceTranscriber()
        transcribed_text = transcriber.transcribe_audio(voice_file_path)
        if not transcribed_text or not transcribed_text.strip():
            return {"error": "Transcription failed or returned empty text."}
        return InvestigationService.analyze_transcript(transcribed_text)

    @staticmethod
    def analyze_transcript(transcribed_text: str) -> dict:
        from app.services.utils.ai_analysis import AIAnalyzer

        # Enhanced prompt that encourages inference and analysis
        prompt = f'''
You are an expert pharmaceutical deviation investigator with 20+ years of experience in GMP, quality systems, and regulatory compliance. Analyze the following transcript and provide a comprehensive investigation analysis.

CRITICAL INSTRUCTIONS:
1. Even if specific sections are not explicitly mentioned, use your pharmaceutical expertise to provide reasonable analysis based on context clues, industry standards, and best practices
2. Generate meaningful insights and recommendations based on the incident described
3. Use pharmaceutical industry knowledge to fill gaps where transcript is unclear
4. Provide actionable insights even from limited information
5. Only use "Not found in document" if absolutely no relevant information or context exists for that specific field
6. Think like a seasoned investigator - what would you look for, what questions would you ask, what actions would you recommend?

TRANSCRIPT TO ANALYZE:
"""{transcribed_text}"""

Based on your analysis, provide a comprehensive investigation covering these areas:

**Background**: Summarize the incident, what happened, when, where, and initial circumstances
**Deviation Triage**: Classify severity, impact level, immediate risk assessment
**Discussion**: 
  - Process: What process was involved, potential process failures or gaps
  - Equipment: Equipment involved, potential equipment issues or malfunctions  
  - Environment/People: Environmental factors, human factors, training issues
  - Documentation: Document adequacy, procedure compliance, record keeping
**Root Cause Analysis**:
  - 5 Why: Recommend 5 Why analysis approach for this incident type
  - Fishbone: Suggest Fishbone categories relevant to this deviation
  - 5Ms: Analyze Man, Machine, Method, Material, Measurement factors
  - FMEA: Recommend FMEA approach if applicable
**Final Assessment**:
  - Patient Safety: Potential patient safety impact and risk level
  - Product Quality: Impact on product quality and specifications
  - Compliance Impact: GMP, regulatory compliance implications
  - Validation Impact: Impact on validated systems or processes
  - Regulatory Impact: Potential regulatory reporting or actions needed
**Historic Review**:
  - Previous Occurrence: Likelihood this has occurred before based on incident type
  - RCA/CAPA Adequacy: Assessment of what investigation depth and CAPA scope needed
**CAPA**:
  - Correction: Immediate fixes to address the specific incident
  - Interim Action: Short-term measures to prevent immediate recurrence
  - Corrective Action: Address root cause to prevent recurrence
  - Preventive Action: Broader measures to prevent similar issues
**Investigation Summary**: Comprehensive summary including key findings, conclusions, and overall assessment

Return ONLY a valid JSON object with this exact structure (use underscores in key names):

{{
  "Background": "Detailed background analysis based on transcript",
  "Deviation_Triage": "Triage classification and risk assessment", 
  "Discussion": {{
    "process": "Process analysis and potential gaps",
    "equipment": "Equipment factors and considerations",
    "environment_people": "Environmental and human factors analysis", 
    "documentation": "Documentation adequacy assessment"
  }},
  "Root_Cause_Analysis": {{
    "5_why": "5 Why methodology recommendation and initial analysis",
    "Fishbone": "Fishbone analysis categories and approach",
    "5Ms": "5Ms analysis covering all relevant factors",
    "FMEA": "FMEA recommendation and applicability"
  }},
  "Final_Assessment": {{
    "Patient_Safety": "Patient safety impact assessment and risk level",
    "Product_Quality": "Product quality impact and implications",
    "Compliance_Impact": "Regulatory compliance and GMP implications", 
    "Validation_Impact": "Impact on validated systems and processes",
    "Regulatory_Impact": "Regulatory reporting and authority notification needs"
  }},
  "Historic_Review": {{
    "previous_occurrence": "Assessment of recurrence likelihood and historical context",
    "impact_to_adequacy_of_RCA_and_CAPA": "Required investigation depth and CAPA scope assessment"
  }},
  "CAPA": {{
    "Correction": "Immediate corrective measures to address the specific incident",
    "Interim_Action": "Short-term actions to prevent immediate recurrence",
    "Corrective_Action": "Root cause addressing actions to prevent recurrence", 
    "Preventive_Action": "Preventive measures to avoid similar issues system-wide"
  }},
  "Investigation_Summary": "Comprehensive investigation summary with key findings, conclusions, risk assessment, and overall incident characterization"
}}
'''
        ai = AIAnalyzer()
        ai_response = ai.analyze_with_prompt(prompt)
        if not ai_response:
            return {"error": "AI analysis failed - no response received"}
        ai_result = {}
        json_match = re.search(r'({[\s\S]*})', ai_response)
        if json_match:
            try:
                ai_result = json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                ai_result = {"error": f"JSON parsing failed: {str(e)}"}
        else:
            try:
                ai_result = json.loads(ai_response)
            except json.JSONDecodeError as e:
                ai_result = {"error": "Response is not valid JSON", "raw_response": ai_response[:500]}
        return ai_result
