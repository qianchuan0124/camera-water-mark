import logging
from pathlib import Path
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
SUBTITLE_STYLE_PATH = RESOURCE_PATH / "subtitle_style"
EXIFTOOL_PATH = APPDATA_PATH / "exiftool"
OUTPUT_PATH = APPDATA_PATH / "output"
ENCODING = 'gbk'

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

class Config(QConfig):
    save_path = APPDATA_PATH / "config.json"
    subtitle_style_name = ConfigItem("SubtitleStyle", "StyleName", "default")
    subtitle_preview_image = ConfigItem("SubtitleStyle", "PreviewImage", "")
    leftTopType = ConfigItem("Layout", "LeftTopType", "LensModel")
    leftTopBold = ConfigItem("Layout", "LeftTopBold", True)
    leftTopFontColor = ConfigItem("Layout", "LeftTopFontColor", "#212121")

    leftBottomType = ConfigItem("Layout", "LeftTopType", "Model")
    leftBottomBold = ConfigItem("Layout", "LeftTopBold", False)
    leftBottomFontColor = ConfigItem("Layout", "LeftTopFontColor", "#212121")

    rightTopType = ConfigItem("Layout", "LeftTopType", "Datetime")
    rightTopBold = ConfigItem("Layout", "LeftTopBold", True)
    rightTopFontColor = ConfigItem("Layout", "LeftTopFontColor", "#212121")

    rightBottomType = ConfigItem("Layout", "LeftTopType", "Param")
    rightBottomBold = ConfigItem("Layout", "LeftTopBold", False)
    rightBottomFontColor = ConfigItem("Layout", "LeftTopFontColor", "#212121")

    baseQuality = ConfigItem("Layout", "BaseQuality", 100)
    baseFontSize = ConfigItem("Layout", "BaseFontSize", 1)
    boldFontSize = ConfigItem("Layout", "BoldFontSize", 1)

    useEquivalentFocal = ConfigItem("Layout", "UseEquivalentFocal", True)
    useOriginRatioPadding = ConfigItem("Layout", "UseOriginRatioPadding", False)
    addShadow = ConfigItem("Layout", "AddShadow", False)
    whiteMargin = ConfigItem("Layout", "WhiteMargin", True)
    whiteMarginWidth = ConfigItem("Layout", "WhiteMarginWidth", 3)
    layoutType = ConfigItem("Layout", "LayoutType", "watermark_left_logo")

    backgroundColor = ConfigItem("Layout", "BackgroundColor", "#ffffff")
    logoEnable = ConfigItem("Layout", "LogoEnable", True)
    isLogoLeft = ConfigItem("Layout", "isLogoLeft", True)

    def get_font_padding_level(self):
        bold_font_size = self.boldFontSize.value if 1 <= self.boldFontSize.value <= 3 else 1
        font_size = self.baseFontSize.value if 1 <= self.baseFontSize.value <= 3 else 1
        return bold_font_size + font_size

cfg = Config()
qconfig.load(SETTINGS_PATH, cfg)