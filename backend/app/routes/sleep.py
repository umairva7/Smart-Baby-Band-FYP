"""
Sleep Tracking Routes
Endpoints for sleep session history and sleep quality analysis.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import datetime
from app.middleware.firebase_auth import get_current_user
from app.schemas.sleep_session import (
    SleepSessionResponse,
    SleepHistoryResponse,
    SleepSummaryResponse,
)
from app.services.sleep_service import SleepService

router = APIRouter()


@router.get("/history/{baby_id}", response_model=SleepHistoryResponse)
async def get_sleep_history(
    baby_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """
    Get sleep session history for a baby.
    Used by the Flutter Sleep History page.
    """
    service = SleepService()
    result = await service.get_history(
        baby_id=baby_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return result


@router.get("/summary/{baby_id}", response_model=SleepSummaryResponse)
async def get_sleep_summary(
    baby_id: str,
    hours: int = Query(24, ge=1, le=168, description="Summary for last N hours"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get aggregated sleep statistics.
    Shows total sleep, deep/light/awake breakdown, quality scores.
    """
    service = SleepService()
    summary = await service.get_summary(baby_id, hours)
    return summary


@router.get("/latest/{baby_id}", response_model=SleepSessionResponse)
async def get_current_sleep_status(
    baby_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get the baby's current sleep status (or most recent session).
    Used by the Dashboard to show current sleep state.
    """
    service = SleepService()
    session = await service.get_latest_session(baby_id)

    if not session:
        raise HTTPException(status_code=404, detail="No sleep data found")

    return session
