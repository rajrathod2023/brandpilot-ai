from fastapi import APIRouter
from pydantic import BaseModel

from campaign_v2.orchestrator import build_campaign


router = APIRouter(
    prefix="/api/campaign-v2",
    tags=["Campaign V2"]
)


class CampaignV2Request(BaseModel):
    websiteUrl: str
    topic: str
    targetAudience: str = ""
    ctaText: str = ""
    ctaLink: str = ""
    offerPromotion: str = ""
    photoCount: int = 1
    textCount: int = 1


@router.post("/generate")
def generate_campaign_v2(request: CampaignV2Request):
    result = build_campaign(
        website_url=request.websiteUrl,
        topic=request.topic,
        target_audience=request.targetAudience,
        cta_text=request.ctaText,
        cta_link=request.ctaLink,
        offer_promotion=request.offerPromotion,
        photo_count=request.photoCount,
        text_count=request.textCount
    )

    return {
        "success": True,
        "result": result
    }