from fastapi import APIRouter
from app.services.analytics_service import get_metrics_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def analytics_summary():
    return get_metrics_summary()