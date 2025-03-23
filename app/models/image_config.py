from PIL import ImageFont
from pathlib import Path
from app.config import cfg, RESOURCE_PATH

FONT = Path(f"{RESOURCE_PATH}/fonts/AlibabaPuHuiTi-2-45-Light.otf")
BOLD_FONT = Path(f"{RESOURCE_PATH}/fonts/AlibabaPuHuiTi-2-85-Bold.otf")


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
    return ImageFont.truetype(FONT, get_font_size())


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
    return ImageFont.truetype(BOLD_FONT, get_bold_font_size())
