from fastapi import APIRouter
from app.firebase_client import get_firestore_client

router = APIRouter()

@router.get("/")
async def get_active_alerts(device_id: str):
    """
    Returns active alerts for a device.
    Expected by the Flutter app for polling real-time danger conditions.
    """
    db = get_firestore_client()
    alerts = []
    
    try:
        # Fetch environment logs for this device
        docs = db.collection("environment_logs").where("device_id", "==", device_id).stream()
        
        # Sort locally to avoid composite index requirement
        logs = [d.to_dict() for d in docs]
        logs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        if logs:
            latest = logs[0]
            # If the latest environment reading is dangerous/warning
            if latest.get("overall") in ["danger", "warning"]:
                alerts.append({
                    "alert_type": "environment_" + latest.get("overall"),
                    "temperature": latest.get("temperature"),
                    "humidity": latest.get("humidity"),
                    "timestamp": latest.get("timestamp")
                })
                
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        
    return alerts
