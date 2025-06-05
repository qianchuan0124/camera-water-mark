import sys
import platform
import logging
from pathlib import Path
from qfluentwidgets import (
    QConfig,
    qconfig,
    ConfigItem
)

LOG_LEVEL = logging.INFO

if getattr(sys, 'frozen', False):
    ROOT_PATH = Path(__file__).parent.parent
    if platform.system() == 'Windows':
        APPDATA_PATH = ROOT_PATH.parent / "AppData"
        RESOURCE_PATH = ROOT_PATH.parent / "resource"
        LOG_PATH = APPDATA_PATH / "logs"
        ASSETS_PATH = RESOURCE_PATH / "assets"
        CACHE_PATH = APPDATA_PATH / "cache"
        SETTINGS_PATH = APPDATA_PATH / "settings.json"
        STYLE_PATH = RESOURCE_PATH / "style"
        EXIFTOOL_PATH = APPDATA_PATH / "exiftool"
        OUTPUT_PATH = APPDATA_PATH / "output"
        FONT_PATH = RESOURCE_PATH / "fonts"
    else:
        APPDATA_PATH = f"{ROOT_PATH}/AppData"
        RESOURCE_PATH = f"{ROOT_PATH}/resource"
        LOG_PATH = f"{APPDATA_PATH}/logs"
        ASSETS_PATH = f"{RESOURCE_PATH}/assets"
        CACHE_PATH = f"{APPDATA_PATH}/cache"
        SETTINGS_PATH = f"{APPDATA_PATH}/settings.json"
        STYLE_PATH = f"{RESOURCE_PATH}/style"
        EXIFTOOL_PATH = f"{APPDATA_PATH}/exiftool"
        OUTPUT_PATH = f"{APPDATA_PATH}/output"
        FONT_PATH = f"{RESOURCE_PATH}/fonts"
else:
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
    FONT_PATH = RESOURCE_PATH / "fonts"


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
    styleName = ConfigItem("Style", "StyleName", "default")

    baseQuality = ConfigItem("Base", "BaseQuality", 100)
    baseFontName = ConfigItem("Base", "BaseFontName",
                              "AlibabaPuHuiTi-2-45-Light")
    boldFontName = ConfigItem("Base", "BoldFontName",
                              "AlibabaPuHuiTi-2-45-Bold")
    baseFontSize = ConfigItem("Base", "BaseFontSize", 1)
    boldFontSize = ConfigItem("Base", "BoldFontSize", 1)
    radiusInfo = ConfigItem("Base", "RadiusInfo", 20)
    backgroundColor = ConfigItem("Base", "BackgroundColor", "#ffffffff")
    targetPath = ConfigItem("Base", "TargetPath", str(OUTPUT_PATH))

    markMode = ConfigItem("Mode", "MarkMode", "standard")

    useEquivalentFocal = ConfigItem("Global", "UseEquivalentFocal", True)
    useOriginRatioPadding = ConfigItem(
        "Global", "UseOriginRatioPadding", False)
    addShadow = ConfigItem("Global", "AddShadow", False)
    backgroundBlur = ConfigItem("Global", "BackgroundBlur", False)
    blurExtent = ConfigItem("Global", "BlurExtent", 35)
    blurHorizontalPadding = ConfigItem("Global", "BlurHorizontalPadding", 0.09)
    blurTopPadding = ConfigItem("Global", "BlurTopPadding", 0.09)
    blurBottomPadding = ConfigItem("Global", "BlurBottomPadding", 0.09)

    whiteMargin = ConfigItem("Global", "WhiteMargin", True)
    whiteMarginWidth = ConfigItem("Global", "WhiteMarginWidth", 3)

    logoEnable = ConfigItem("LOGO", "LogoEnable", True)
    isLogoLeft = ConfigItem("LOGO", "isLogoLeft", True)
    simpleLogoSize = ConfigItem("LOGO", "SimpleLogoSize", 0.3)
    customLogoEnable = ConfigItem("LOGO", "CustomLogoEnable", False)
    customLogoPath = ConfigItem("LOGO", "CustomLogoPath", "")

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
    
    standardVerticalPadding = ConfigItem("Layout", "StandardTopPadding", 0.45)
    standardLeftPadding = ConfigItem("Layout", "StandardLeftPadding", 200)
    standardRightPadding = ConfigItem("Layout", "StandardRightPadding", 200)

    simpleFirstLineType = ConfigItem("Layout", "SimpleFirstLineType", "Model")
    simpleFirstLineBold = ConfigItem("Layout", "SimpleFirstLineBold", True)
    simpleFirstLineColor = ConfigItem("Layout", "SimpleFirstLineColor", "#212121")

    simpleSecondLineType = ConfigItem("Layout", "SimpleSecondLineType", "Param")
    simpleSecondLineBold = ConfigItem("Layout", "SimpleSecondLineBold", False)
    simpleSecondLineColor = ConfigItem("Layout", "SimpleSecondLineColor", "#757575")

    simpleThirdLineType = ConfigItem("Layout", "SimpleThirdLineType", "Datetime")
    simpleThirdLineBold = ConfigItem("Layout", "SimpleThirdLineBold", False)
    simpleThirdLineColor = ConfigItem("Layout", "SimpleThirdLineColor", "#757575")

    simpleScale = ConfigItem("Layout", "SimpleScale", 0.16)
    simplePaddingScale = ConfigItem("Layout", "SimplePaddingScale", 0.1)

    def get_font_padding_level(self):
        bold_font_size = self.boldFontSize.value if 1 <= self.boldFontSize.value <= 3 else 1
        font_size = self.baseFontSize.value if 1 <= self.baseFontSize.value <= 3 else 1
        return bold_font_size + font_size

    def to_dict(self):
        return self._cfg.toDict()


cfg = Config()
qconfig.load(SETTINGS_PATH, cfg)
