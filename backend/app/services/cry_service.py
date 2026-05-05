"""
Cry Service — Business logic for cry classification and cry event management.

This service:
1. Loads the TFLite cry detection model
2. Runs inference on MFCC features from ESP32
3. Stores classification results in Firestore
4. Queries cry event history
"""

from datetime import datetime, timedelta
from typing import Optional, List
from app.firebase_client import get_firestore_client
from app.schemas.cry_event import CryClassifyRequest, CryClassifyResponse
from app.config import get_settings
from app.services.notification_service import NotificationService

# Cry type labels — must match your training labels
CRY_LABELS = ["hungry", "tired", "discomfort", "diaper"]


class CryService:
    """Service for cry classification and event management."""

    def __init__(self):
        self.db = get_firestore_client()
        self.collection = "cry_events"
        self._model = None

    def _load_model(self):
        """
        Lazy-load the TFLite model.
        Called only when classify_cry() is first used.
        """
        if self._model is not None:
            return

        settings = get_settings()
        import tensorflow as tf
        print(f"Loading ML Model from: {settings.CRY_MODEL_PATH}")
        self._model = tf.lite.Interpreter(model_path=settings.CRY_MODEL_PATH)
        self._model.allocate_tensors()
        
        self.input_details = self._model.get_input_details()
        self.output_details = self._model.get_output_details()

    async def classify_cry(self, request: CryClassifyRequest) -> CryClassifyResponse:
        """
        Run ML inference on MFCC audio features.
        """
        self._load_model()
        import numpy as np

        # Convert to numpy array
        input_data = np.array(request.audio_features, dtype=np.float32)

        # Reshape to expected input shape
        expected_shape = self.input_details[0]['shape']
        input_data = input_data.reshape(expected_shape)

        # Run inference
        self._model.set_tensor(self.input_details[0]['index'], input_data)
        self._model.invoke()

        # Get output
        output_data = self._model.get_tensor(self.output_details[0]['index'])[0]

        # Map predictions to labels
        predictions = {label: float(prob) for label, prob in zip(CRY_LABELS, output_data)}
        
        cry_type = max(predictions, key=predictions.get)
        confidence = predictions[cry_type]

        # If confidence is lower than 72%, classify as "unknown"
        if confidence < 0.72:
            cry_type = "unknown"

        # Store the event in Firestore
        event_data = {
            "baby_id": request.baby_id,
            "cry_type": cry_type,
            "confidence": confidence,
            "duration_seconds": request.duration_seconds,
            "timestamp": datetime.utcnow(),
        }
        self.db.collection(self.collection).add(event_data)

        # Trigger Real-Time Notification
        try:
            # 1. Fetch the baby profile to find the parent's user_id
            baby_doc = self.db.collection("babies").document(request.baby_id).get()
            if baby_doc.exists:
                user_id = baby_doc.to_dict().get("user_id")
                
                if user_id:
                    # 2. Determine the notification message
                    title = "Baby Cry Alert 🍼"
                    if cry_type == "hungry":
                        message = "Your baby might be hungry."
                    elif cry_type == "tired":
                        message = "Your baby seems tired and needs sleep."
                    elif cry_type == "discomfort":
                        message = "Your baby is experiencing discomfort."
                    elif cry_type == "diaper":
                        message = "Your baby might need a diaper change."
                    else:
                        message = "Your baby is crying! (Unknown reason)"
                        
                    # 3. Call the notification service
                    notif_service = NotificationService()
                    # We only await this because we want to trigger the push notification
                    await notif_service.create_notification(
                        user_id=user_id,
                        baby_id=request.baby_id,
                        title=title,
                        message=message,
                        notif_type="cry_alert"
                    )
        except Exception as e:
            print(f"Failed to send notification: {e}")

        return CryClassifyResponse(
            cry_type=cry_type,
            confidence=confidence,
            all_predictions=predictions,
        )

    async def get_history(
        self,
        baby_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cry_type: Optional[str] = None,
        limit: int = 50,
    ) -> dict:
        """Get cry event history with optional filtering."""
        query = (
            self.db.collection(self.collection)
            .where("baby_id", "==", baby_id)
        )

        if start_date:
            query = query.where("timestamp", ">=", start_date)
        if end_date:
            query = query.where("timestamp", "<=", end_date)
        if cry_type:
            query = query.where("cry_type", "==", cry_type)

        query = query.order_by("timestamp", direction="DESCENDING").limit(limit)

        docs = list(query.stream())
        data = []
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id
            data.append(item)

        return {"data": data, "total": len(data)}

    async def get_latest_event(self, baby_id: str) -> Optional[dict]:
        """Get the most recent cry event for a baby."""
        docs = (
            self.db.collection(self.collection)
            .where("baby_id", "==", baby_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(1)
            .stream()
        )

        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            return data

        return None
