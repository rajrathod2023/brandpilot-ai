from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from campaign_v2.campaign_v2 import router as campaign_v2_router


app = FastAPI(title="BrandPilot Campaign V2 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaign_v2_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Campaign V2 backend is running"
    }