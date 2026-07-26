"""AI model wrappers: face detection, eye tracking, emotion, and the registry."""
from backend.ai_models.face_detection import FaceDetector, FaceTracker  # noqa: F401
from backend.ai_models.eye_tracking import EyeTracker  # noqa: F401
from backend.ai_models.emotion_detection import EmotionDetector  # noqa: F401
from backend.ai_models.model_registry import ModelRegistry  # noqa: F401
