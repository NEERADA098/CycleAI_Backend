import numpy as np
import joblib
import os

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

MODEL_PATH = "app/ml/cycle_predictor.h5"
SCALER_PATH = "app/ml/scaler.pkl"
SEQUENCE_LENGTH = 5


class PredictionService:
    def __init__(self):
        self._model = None
        self._scaler = None
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return self._model is not None

        if not TF_AVAILABLE:
            print("TensorFlow not available. Using fallback prediction.")
            self._initialized = True
            return False

        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            print("Model not trained yet. Using fallback prediction.")
            self._initialized = True
            return False

        try:
            self._model = tf.keras.models.load_model(MODEL_PATH)
            self._scaler = joblib.load(SCALER_PATH)
            self._initialized = True
            print("LSTM model loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            self._initialized = True
            return False

    def predict_next_cycle(self, cycle_lengths: list[float]) -> dict:
        """
        Predicts the next cycle length given a list of past cycle lengths.

        Args:
            cycle_lengths: List of recent cycle lengths in chronological order

        Returns:
            dict with prediction, confidence, and method used
        """
        if len(cycle_lengths) == 0:
            return {
                "predicted_days": 28,
                "confidence": "low",
                "method": "default",
                "message": "No cycle history available"
            }

        model_available = self._initialize()

        if not model_available or len(cycle_lengths) < SEQUENCE_LENGTH:
            avg = sum(cycle_lengths) / len(cycle_lengths)
            return {
                "predicted_days": round(avg, 1),
                "confidence": "medium" if len(cycle_lengths) >= 3 else "low",
                "method": "average",
                "message": f"Based on average of {len(cycle_lengths)} cycles"
            }

        try:
            recent = cycle_lengths[-SEQUENCE_LENGTH:]
            input_array = np.array(recent).reshape(-1, 1)
            normalized = self._scaler.transform(input_array).reshape(
                1, SEQUENCE_LENGTH, 1
            )
            prediction_normalized = self._model.predict(normalized, verbose=0)
            prediction = self._scaler.inverse_transform(
                prediction_normalized
            )[0][0]

            prediction = float(np.clip(prediction, 21, 45))

            variance = np.std(cycle_lengths[-6:]) if len(cycle_lengths) >= 6 else 5
            confidence = "high" if variance < 2 else "medium" if variance < 4 else "low"

            return {
                "predicted_days": round(prediction, 1),
                "confidence": confidence,
                "method": "lstm",
                "message": f"AI prediction based on {len(cycle_lengths)} cycles"
            }

        except Exception as e:
            avg = sum(cycle_lengths) / len(cycle_lengths)
            return {
                "predicted_days": round(avg, 1),
                "confidence": "low",
                "method": "fallback",
                "message": f"Fallback to average: {str(e)}"
            }


prediction_service = PredictionService()
