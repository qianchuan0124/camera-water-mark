import os
from dataclasses import dataclass
from typing import List
from pathlib import Path
from app.config import FONT_PATH
from PIL import ImageFont
from pathlib import Path
from app.config import cfg


@dataclass
class FontItem:
    name: str
    path: Path


class FontManager:
    def __init__(self):
        self.items: List[FontItem] = []
        self.load_fonts()

    def load_fonts(self):
        """
        使用 os.walk 获取指定目录及其子目录中的所有 .otf 和 .ttf 文件名称。

        :param directory: 要搜索的目录路径
        :return: 一个包含所有 .otf 和 .ttf 文件名称的列表
        """
        for root, _, files in os.walk(FONT_PATH):
            for file in files:
                if file.lower().endswith(('.otf', '.ttf')):
                    font_name, _ = os.path.splitext(file)
                    font_path = os.path.join(root, file)
                    item = FontItem(font_name, Path(font_path))
                    self.items.append(item)

    def font_families(self) -> List[str]:
        return [item.name for item in self.items]

    def font_path(self, name: str) -> Path:
        if len(self.items) <= 0:
            return ""

        for item in self.items:
            if item.name.lower() == name.lower():
                return item.path

        return Path(self.items[0].path)

    def get_font_size(self):
        font_size = cfg.baseFontSize.value
        if font_size == 1:
            return 240
        elif font_size == 2:
            return 250
        elif font_size == 3:
            return 300
        else:
            return 240

    def get_font(self):
        return ImageFont.truetype(self.font_path(cfg.baseFontName.value), self.get_font_size())

    def get_bold_font_size(self):
        font_size = cfg.boldFontSize.value
        if font_size == 1:
            return 260
        elif font_size == 2:
            return 290
        elif font_size == 3:
            return 320
        else:
            return 260

    def get_bold_font(self):
        return ImageFont.truetype(self.font_path(cfg.boldFontName.value), self.get_bold_font_size())


font_manager = FontManager()
