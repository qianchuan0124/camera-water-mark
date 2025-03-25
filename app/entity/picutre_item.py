from dataclasses import dataclass
from app.thread.image_handle_thread import ImageHandleStatus


@dataclass
class PictureItem:
    name: str
    original_path: str
    target_path: str
    status: ImageHandleStatus
    errorInfo: str = ""
