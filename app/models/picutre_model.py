from dataclasses import dataclass
from app.thread.image_handle_thread import ImageHandleStatus


@dataclass
class PictureItem:
    name: str
    original_path: str
    target_path: str
    status: ImageHandleStatus

    def to_dict(self) -> dict:
        """将 PictureItem 实例转换为字典"""
        return {
            "name": self.name,
            "original_path": self.original_path,
            "target_path": self.target_path,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 PictureItem 实例"""
        return cls(name=data["name"], original_path=data["original_path"], target_path=data["target_path"], status=data["status"])
