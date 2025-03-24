import logging
from pathlib import Path
from enum import Enum
from qfluentwidgets import (
    QConfig,
    qconfig,
    ConfigItem
)

LOG_LEVEL = logging.INFO
ROOT_PATH = Path(__file__).parent
APPDATA_PATH = ROOT_PATH.parent / "AppData"
RESOURCE_PATH = ROOT_PATH.parent / "resource"
LOG_PATH = APPDATA_PATH / "logs"
ASSETS_PATH = RESOURCE_PATH / "assets"
CACHE_PATH = APPDATA_PATH / "cache"
SETTINGS_PATH = APPDATA_PATH / "settings.json"
STYLE_PATH = RESOURCE_PATH / "style"
EXIFTOOL_PATH = APPDATA_PATH / "exiftool"
OUTPUT_PATH = APPDATA_PATH / "output"
ENCODING = 'gbk'


class SupportedImageFormats(Enum):
    """支持的视频格式"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"


class ElementConfig(object):
    """
    布局中元素的配置对象
    """

    def __init__(self, element):
        self.element = element

    def get_name(self):
        return self.element['name']

    def is_bold(self):
        return self.element['is_bold']

    def get_value(self):
        return self.element['value'] if 'value' in self.element else None

    def get_color(self):
        if 'color' in self.element:
            return self.element['color']
        else:
            return '#212121'


LOGO_PATH = {
    "default": Path(f"{RESOURCE_PATH}/logos/empty.png"),
    "APPLE": Path(f"{RESOURCE_PATH}/logos/apple.png"),
    "Canon": Path(f"{RESOURCE_PATH}/logos/canon.png"),
    "DJI": Path(f"{RESOURCE_PATH}/logos/DJI.png"),
    "\u7A7A": Path(f"{RESOURCE_PATH}/logos/empty.png"),
    "FUJIFILM": Path(f"{RESOURCE_PATH}/logos/fujifilm.png"),
    "HASSELBLAD": Path(f"{RESOURCE_PATH}/logos/hasselblad.png"),
    "HUAWEI": Path(f"{RESOURCE_PATH}/logos/xmage.png"),
    "leica": Path(f"{RESOURCE_PATH}/logos/leica_logo.png"),
    "NIKON": Path(f"{RESOURCE_PATH}/logos/nikon.png"),
    "Olympus": Path(f"{RESOURCE_PATH}/logos/olympus_blue_gold.png"),
    "Panasonic": Path(f"{RESOURCE_PATH}/logos/panasonic.png"),
    "PENTAX": Path(f"{RESOURCE_PATH}/logos/pentax.png"),
    "RICOH": Path(f"{RESOURCE_PATH}/logos/RICOH.png"),
    "SONY": Path(f"{RESOURCE_PATH}/logos/sony.png"),
}

class LOGO_LAYOUT(Enum):
    LEFT = "LOGO居左"
    RIGHT = "LOGO居右"

    def get_enum(value):
        for member in LOGO_LAYOUT:
            if member.value == value:
                return member
        return LOGO_LAYOUT.LEFT
    
    def isLeft(self):
        return self == LOGO_LAYOUT.LEFT
    
    def all_values():
        values = [member.value for member in LOGO_LAYOUT]
        return values
    
class MARK_MODE(Enum):
    STANDARD = "标准模式"
    SIMPLE = "简易模式"

    def get_enum(value):
        for member in MARK_MODE:
            if member.value == value:
                return member
        return MARK_MODE.STANDARD

    def info(self):
        if self == MARK_MODE.SIMPLE:
            return "simple"
        else:
            return "standard"

    def key(value):
        if value == "simple":
            return MARK_MODE.SIMPLE
        else:
            return MARK_MODE.STANDARD
        
    def all_values():
        values = [member.value for member in MARK_MODE]
        return values
    
    def isSimple(self):
        return self == MARK_MODE.SIMPLE


class Config(QConfig):
    styleName = ConfigItem("Style", "StyleName", "default")

    baseQuality = ConfigItem("Base", "BaseQuality", 100)
    baseFontSize = ConfigItem("Base", "BaseFontSize", 1)
    boldFontSize = ConfigItem("Base", "BoldFontSize", 1)
    backgroundColor = ConfigItem("Base", "BackgroundColor", "#ffffff")

    markMode = ConfigItem("Mode", "MarkMode", "standard")

    useEquivalentFocal = ConfigItem("Global", "UseEquivalentFocal", True)
    useOriginRatioPadding = ConfigItem(
        "Global", "UseOriginRatioPadding", False)
    addShadow = ConfigItem("Global", "AddShadow", False)
    whiteMargin = ConfigItem("Global", "WhiteMargin", True)
    whiteMarginWidth = ConfigItem("Global", "WhiteMarginWidth", 3)

    logoEnable = ConfigItem("LOGO", "LogoEnable", True)
    isLogoLeft = ConfigItem("LOGO", "isLogoLeft", True)

    leftTopType = ConfigItem("Layout", "LeftTopType", "LensModel")
    leftTopBold = ConfigItem("Layout", "LeftTopBold", True)
    leftTopFontColor = ConfigItem("Layout", "LeftTopFontColor", "#212121")

    leftBottomType = ConfigItem("Layout", "LeftBottomType", "Model")
    leftBottomBold = ConfigItem("Layout", "LeftBottomBold", False)
    leftBottomFontColor = ConfigItem(
        "Layout", "LeftBottomFontColor", "#757575")

    rightTopType = ConfigItem("Layout", "RightTopType", "Datetime")
    rightTopBold = ConfigItem("Layout", "RightTopBold", True)
    rightTopFontColor = ConfigItem("Layout", "RightTopFontColor", "#212121")

    rightBottomType = ConfigItem("Layout", "RightBottomType", "Param")
    rightBottomBold = ConfigItem("Layout", "RightBottomBold", False)
    rightBottomFontColor = ConfigItem(
        "Layout", "RightBottomFontColor", "#757575")

    def get_font_padding_level(self):
        bold_font_size = self.boldFontSize.value if 1 <= self.boldFontSize.value <= 3 else 1
        font_size = self.baseFontSize.value if 1 <= self.baseFontSize.value <= 3 else 1
        return bold_font_size + font_size

    def to_dict(self):
        return self._cfg.toDict()


cfg = Config()
qconfig.load(SETTINGS_PATH, cfg)
