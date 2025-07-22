from fastapi import APIRouter, UploadFile, File
from app.services.deviation.quality_review.quality_review import QualityReviewService
from app.services.deviation.quality_review.quality_review_schema import QualityReviewResponse

router = APIRouter(prefix="/quality_review", tags=["Quality Review"])

@router.post("/", response_model=QualityReviewResponse)
async def quality_review(audio: UploadFile = File(...)):
    result = await QualityReviewService.process_quality_review(audio)
    return result
