from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    ComboBoxSettingCard,
    ColorSettingCard,
    SpinBoxSettingCard
)
from app.config import cfg
from app.manager.font_manager import font_manager
from app.utils.image_handle import qcolor_to_hex, hex_to_qcolor


class BaseGroup(SettingCardGroup):
    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "BaseGroup", "基础"), parent=parent)
        self.__init_values()
        self.__setup_sub_layout()
        self.__set_settings()
        self.__connect_signals()

    def __init_values(self):
        # 基础样式
        self.baseBackgroundValue = hex_to_qcolor(
            cfg.backgroundColor.value)
        self.baseFontName = cfg.baseFontName.value
        self.boldFontName = cfg.boldFontName.value
        self.baseFontSizeValue = cfg.baseFontSize.value
        self.boldFontSizeValue = cfg.boldFontSize.value
        self.baseQualityValue = cfg.baseQuality.value
        self.radiusInfoValue = cfg.radiusInfo.value

    def __setup_sub_layout(self):
        # 基础样式

        # 背景颜色
        self.baseBackground = ColorSettingCard(
            self.baseBackgroundValue,
            FIF.PALETTE,
            self.tr("背景颜色"),
            self.tr("设置照片背景颜色"),
            enableAlpha=True
        )

        # 标准字体
        self.baseFont = ComboBoxSettingCard(
            FIF.FONT,
            self.tr("标准字体"),
            self.tr("选择标准字体"),
            texts=font_manager.font_families(),
        )
        self.baseFont.comboBox.setMaxVisibleItems(12)

        # 粗体字体
        self.boldFont = ComboBoxSettingCard(
            FIF.FONT,
            self.tr("粗体字体"),
            self.tr("选择粗体字体"),
            texts=font_manager.font_families(),
        )
        self.boldFont.comboBox.setMaxVisibleItems(12)

        # 标准字体大小
        self.baseFontSize = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("标准字号"),
            self.tr("设置标准字号"),
            minimum=1,
            maximum=3,
        )

        # 粗体字体大小
        self.boldFontSize = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("粗体字号"),
            self.tr("设置粗体字号"),
            minimum=1,
            maximum=3,
        )

        # 渲染质量
        self.baseQuality = SpinBoxSettingCard(
            FIF.ZOOM,
            self.tr("基础质量"),
            self.tr("设置基础质量"),
            minimum=1,
            maximum=100,
        )

        # 圆角设置
        self.radiusInfo = SpinBoxSettingCard(
            FIF.ALIGNMENT,
            self.tr("圆角大小"),
            self.tr("设置圆角大小"),
            minimum=0,
            maximum=100,
        )

        # 基础样式
        self.addSettingCard(self.baseBackground)
        self.addSettingCard(self.baseFont)
        self.addSettingCard(self.baseFontSize)
        self.addSettingCard(self.boldFont)
        self.addSettingCard(self.boldFontSize)
        self.addSettingCard(self.baseQuality)
        self.addSettingCard(self.radiusInfo)

    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def __set_settings(self):
        # 基础样式
        self.baseBackground.setColor(self.baseBackgroundValue)
        self.baseFont.comboBox.setCurrentText(self.baseFontName)
        self.boldFont.comboBox.setCurrentText(self.boldFontName)
        self.baseQuality.setValue(self.baseQualityValue)
        self.radiusInfo.setValue(self.radiusInfoValue)
        self.baseFontSize.setValue(self.baseFontSizeValue)
        self.boldFontSize.setValue(self.boldFontSizeValue)

    def __connect_signals(self):
        # 基础样式
        self.baseBackground.colorChanged.connect(
            lambda text: setattr(self, "baseBackgroundValue", text))
        self.baseFont.currentTextChanged.connect(
            lambda text: setattr(self, "baseFontName", text))
        self.boldFont.currentTextChanged.connect(
            lambda text: setattr(self, "boldFontName", text))
        self.baseFontSize.valueChanged.connect(
            lambda text: setattr(self, "baseFontSizeValue", text))
        self.boldFontSize.valueChanged.connect(
            lambda text: setattr(self, "boldFontSizeValue", text))
        self.baseQuality.valueChanged.connect(
            lambda text: setattr(self, "baseQualityValue", text))
        self.radiusInfo.valueChanged.connect(
            lambda text: setattr(self, "radiusInfoValue", text))

    def load_style(self, style_content):
        # 基础样式
        self.baseBackgroundValue = QColor(
            hex_to_qcolor(style_content["Base"]["BackgroundColor"]))
        self.baseFontName = style_content["Base"]["BaseFontName"]
        self.baseFontSizeValue = style_content["Base"]["BaseFontSize"]
        self.boldFontName = style_content["Base"]["BoldFontName"]
        self.boldFontSizeValue = style_content["Base"]["BoldFontSize"]
        self.baseQualityValue = int(style_content["Base"]["BaseQuality"])
        self.radiusInfoValue = int(style_content["Base"]["RadiusInfo"])

    def save_style(self):
        # 基础样式
        cfg.set(cfg.backgroundColor, qcolor_to_hex(
            self.baseBackgroundValue))
        cfg.set(cfg.baseFontName, self.baseFontName)
        cfg.set(cfg.boldFontName, self.boldFontName)
        cfg.set(cfg.baseFontSize, self.baseFontSizeValue)
        cfg.set(cfg.boldFontSize, self.boldFontSizeValue)
        cfg.set(cfg.baseQuality, self.baseQualityValue)
        cfg.set(cfg.radiusInfo, self.radiusInfoValue)

    
