"""
Sensor Data Routes
Endpoints for querying sensor data stored in Firestore.

NOTE: Sensor data is WRITTEN by AWS Lambda (from MQTT/IoT Core), not by this API.
These endpoints are for READING data — used by the Flutter app.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import datetime
from app.middleware.firebase_auth import get_current_user
from app.services.sensor_service import SensorService

router = APIRouter()


@router.get("/latest/{baby_id}")
async def get_latest_sensor_data(
    baby_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get the most recent sensor reading for a baby.
    Used by the Flutter Dashboard to show current vitals.
    """
    service = SensorService()
    data = await service.get_latest_reading(baby_id)

    if not data:
        raise HTTPException(status_code=404, detail="No sensor data found")

    return data


@router.get("/history/{baby_id}")
async def get_sensor_history(
    baby_id: str,
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter until this date"),
    data_type: Optional[str] = Query(None, description="Filter by type: heart_rate, temperature, humidity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """
    Get sensor reading history for a baby with optional date filtering.
    Used by Flutter History pages (Heart Rate, Temperature).
    """
    service = SensorService()
    result = await service.get_history(
        baby_id=baby_id,
        start_date=start_date,
        end_date=end_date,
        data_type=data_type,
        page=page,
        page_size=page_size,
    )
    return result


@router.get("/stats/{baby_id}")
async def get_sensor_stats(
    baby_id: str,
    hours: int = Query(24, ge=1, le=168, description="Stats for last N hours"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get aggregated statistics (min, max, avg) for sensor data.
    Useful for health reports and dashboard summaries.
    """
    service = SensorService()
    stats = await service.get_stats(baby_id, hours)
    return stats
