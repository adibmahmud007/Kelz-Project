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
        import re, json
        from app.services.utils.ai_analysis import AIAnalyzer

        prompt = f'''
You are an expert pharmaceutical deviation investigator. Analyze the following transcript and extract the following sections as a JSON object:
- Background
- Deviation Triage
- Discussion (with subfields: process, equipment, environment_people, documentation)
- Root Cause Analysis (with subfields: 5_why, Fishbone, 5Ms, FMEA)
- Final Assessment (with subfields: Patient_Safety, Product_Quality, Compliance_Impact, Validation_Impact, Regulatory_Impact)
- Historic Review (with subfields: previous_occurrence, impact_to_adequacy_of_RCA_and_CAPA)
- CAPA (with subfields: Correction, Interim_Action, Corrective_Action, Preventive_Action)
- Investigation Summary

TRANSCRIPT TO ANALYZE:
"""{transcribed_text}"""

Return ONLY a valid JSON object with these exact keys and subkeys. Do NOT include any explanation, markdown, or extra text. Only output the JSON object. If a field is not found, use 'Not found in document'.
'''
        ai = AIAnalyzer()
        ai_response = ai.analyze_with_prompt(prompt)
        ai_result = {}
        if ai_response:
            json_match = re.search(r'({[\s\S]*})', ai_response)
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
        return ai_result
