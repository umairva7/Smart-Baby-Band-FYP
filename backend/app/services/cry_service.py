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

# Cry type labels — must match your training labels
CRY_LABELS = ["hunger", "pain", "discomfort", "tired", "normal"]


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

        TODO: Implement in Phase 4 — load the .tflite model from ml_models/
        """
        if self._model is not None:
            return

        settings = get_settings()
        # TODO: Load TFLite model
        # import tensorflow as tf
        # self._model = tf.lite.Interpreter(model_path=settings.CRY_MODEL_PATH)
        # self._model.allocate_tensors()
        print(f"⚠️  ML Model not loaded yet. Path: {settings.CRY_MODEL_PATH}")

    async def classify_cry(self, request: CryClassifyRequest) -> CryClassifyResponse:
        """
        Run ML inference on MFCC audio features.

        TODO (Phase 4): Replace this stub with actual TFLite inference.
        """
        self._load_model()

        # ── STUB: Return dummy prediction until model is integrated ──
        # In Phase 4, this will:
        # 1. Reshape the input features
        # 2. Run the TFLite interpreter
        # 3. Get output probabilities
        # 4. Return the top prediction

        predictions = {label: 0.0 for label in CRY_LABELS}
        predictions["hunger"] = 0.85  # Dummy response

        cry_type = max(predictions, key=predictions.get)
        confidence = predictions[cry_type]

        # Store the event in Firestore
        event_data = {
            "baby_id": request.baby_id,
            "cry_type": cry_type,
            "confidence": confidence,
            "duration_seconds": request.duration_seconds,
            "timestamp": datetime.utcnow(),
        }
        self.db.collection(self.collection).add(event_data)

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
