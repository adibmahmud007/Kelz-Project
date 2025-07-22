from pydantic import BaseModel
from typing import Dict

class QualityReviewResponse(BaseModel):
    ai_generated_text: str
    fields: Dict[str, str]
