from PIL import ImageFont
from pathlib import Path
from app.config import cfg
from app.entity.font_manager import font_manager


def get_font_size():
    font_size = cfg.baseFontSize.value
    if font_size == 1:
        return 240
    elif font_size == 2:
        return 250
    elif font_size == 3:
        return 300
    else:
        return 240


def get_font():
    return ImageFont.truetype(font_manager.font_path(cfg.baseFontName.value), get_font_size())


def get_bold_font_size():
    font_size = cfg.boldFontSize.value
    if font_size == 1:
        return 260
    elif font_size == 2:
        return 290
    elif font_size == 3:
        return 320
    else:
        return 260


def get_bold_font():
    return ImageFont.truetype(font_manager.font_path(cfg.boldFontName.value), get_bold_font_size())
