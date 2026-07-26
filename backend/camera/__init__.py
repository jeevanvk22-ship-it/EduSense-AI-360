"""Camera subsystem: capture, buffering, frame processing, recovery."""
from backend.camera.frame_buffer import FrameBuffer, BufferedFrame  # noqa: F401
from backend.camera.frame_processor import FrameProcessor, ProcessedFrame  # noqa: F401
from backend.camera.camera_manager import CameraManager  # noqa: F401
