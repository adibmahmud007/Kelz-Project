from fastapi import APIRouter, UploadFile, File
from app.services.utils.transcription import VoiceTranscriber
from app.services.utils.ai_analysis import AIAnalyzer
import os

class QualityReviewService:
    @staticmethod
    async def process_quality_review(audio: UploadFile):
        audio_path = f"temp_{audio.filename}"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
        transcriber = VoiceTranscriber()
        transcript = transcriber.transcribe_audio(audio_path)
        os.remove(audio_path)
        prompt = (
            f"Quality Review: {transcript}\n"
            "Return the following fields: Quality Review, Has investigation been completed satisfactorily?, has adequate root cause and CAPA actions identified to prevent reoccurrence?, Has identified risks been discussed and mitigated?, AI-Generated Text, Observed temperature excursion in storage area. Product stored above acceptable limits."
        )
        result = AIAnalyzer.analyze_prompt(prompt)
        return result
