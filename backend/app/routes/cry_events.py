"""
Cry Events Routes
Endpoints for cry classification (ML inference) and cry event history.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime
from app.middleware.firebase_auth import get_current_user
from app.schemas.cry_event import (
    CryClassifyRequest,
    CryClassifyResponse,
    CryEventResponse,
    CryHistoryResponse,
)
from app.services.cry_service import CryService

router = APIRouter()


@router.post("/classify", response_model=CryClassifyResponse)
async def classify_cry(
    request: CryClassifyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Classify a baby's cry using the ML model.

    The ESP32 extracts MFCC features from audio and sends them here.
    The backend runs the TFLite model and returns the cry type.

    Flow: ESP32 → (MFCC features) → This Endpoint → TFLite Model → Cry Type
    """
    service = CryService()
    result = await service.classify_cry(request)
    return result


@router.post("/predict")
async def predict_cry_audio(
    file: UploadFile = File(...),
):
    """
    New endpoint for Phase 2:
    Receives raw audio bytes from ESP32, extracts features, 
    runs the Keras model inference, and pushes to Firebase RTDB.
    """
    audio_bytes = await file.read()
    service = CryService()
    
    try:
        result = await service.predict_audio(audio_bytes)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{baby_id}", response_model=CryHistoryResponse)
async def get_cry_history(
    baby_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    cry_type: Optional[str] = Query(None, description="Filter by: hungry, tired, discomfort, diaper, unknown"),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """
    Get cry event history for a baby.
    Used by the Flutter Cry History page.
    """
    service = CryService()
    result = await service.get_history(
        baby_id=baby_id,
        start_date=start_date,
        end_date=end_date,
        cry_type=cry_type,
        limit=limit,
    )
    return result


@router.get("/latest/{baby_id}", response_model=CryEventResponse)
async def get_latest_cry_event(
    baby_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get the most recent cry classification for a baby.
    Used by the Flutter Dashboard's cry classification card.
    """
    service = CryService()
    event = await service.get_latest_event(baby_id)

    if not event:
        raise HTTPException(status_code=404, detail="No cry events found")

    return event
