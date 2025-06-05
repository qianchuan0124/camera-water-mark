from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    ComboBoxSettingCard,
    ColorSettingCard,
    SwitchSettingCard,
    SpinBoxSettingCard
)
from app.entity.enums import DISPLAY_TYPE
from app.config import cfg

# 居中排布, 简易布局

class SimpleLayout(SettingCardGroup):
    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "SimpleLayout", "简易布局"), parent=parent)
        self.__init_values()
        self.__setup_sub_layout()
        self.__set_settings()
        self.__connect_signals()

    def __init_values(self):
        self.firstLineTypeValue = DISPLAY_TYPE.from_str(cfg.simpleFirstLineType.value)
        self.firstLineColorValue = QColor(cfg.simpleFirstLineColor.value)
        self.firstLineBoldValue = cfg.simpleFirstLineBold.value

        self.secondLineTypeValue = DISPLAY_TYPE.from_str(cfg.simpleSecondLineType.value)
        self.secondLineColorValue = QColor(cfg.simpleSecondLineColor.value)
        self.secondLineBoldValue = cfg.simpleSecondLineBold.value

        self.thirdLineTypeValue = DISPLAY_TYPE.from_str(cfg.simpleThirdLineType.value)
        self.thirdLineColorValue = QColor(cfg.simpleThirdLineColor.value)
        self.thirdLineBoldValue = cfg.simpleThirdLineBold.value

        self.simpleScaleValue = int(cfg.simpleScale.value * 100)
        self.simplePaddingScaleValue = int(cfg.simplePaddingScale.value * 100)

    def __setup_sub_layout(self):
        # 第一行类型
        self.firstLineType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("第一行类型"),
            self.tr("设置第一行展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions()
        )

        # 第一行字体颜色
        self.firstLineColor = ColorSettingCard(
            self.firstLineColorValue,
            FIF.PALETTE,
            self.tr("第一行字体颜色"),
            self.tr("设置第一行字体颜色"),
        )

        # 第一行字体粗细
        self.firstLineBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("第一行字体粗细"),
            self.tr("设置第一行字体是否加粗"),
            None,
            self
        )

        # 第二行类型
        self.secondLineType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("第二行类型"),
            self.tr("设置第二行展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions()
        )

        # 第二行字体颜色
        self.secondLineColor = ColorSettingCard(
            self.secondLineColorValue,
            FIF.PALETTE,
            self.tr("第二行字体颜色"),
            self.tr("设置第二行字体颜色"),
        )

        # 第二行字体粗细
        self.secondLineBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("第二行字体粗细"),
            self.tr("设置第二行字体是否加粗"),
            None,
            self
        )

        # 第三行类型
        self.thirdLineType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("第三行类型"),
            self.tr("设置第三行展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions()
        )
        
        # 第三行字体颜色
        self.thirdLineColor = ColorSettingCard(
            self.thirdLineColorValue,
            FIF.PALETTE,
            self.tr("第三行字体颜色"),
            self.tr("设置第三行字体颜色"),
        )
        # 第三行字体粗细
        self.thirdLineBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("第三行字体粗细"),
            self.tr("设置第三行字体是否加粗"),
            None,
            self
        )

        self.simpleScale = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("整体缩放比例"),
            self.tr("设置水印占原图的比例"),
            minimum=1,
            maximum=100
        )

        self.simplePaddingScale = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("边距缩放比例"),
            self.tr("设置边距占水印的比例"),
            minimum=1,
            maximum=100
        )

        self.addSettingCard(self.firstLineType)
        self.addSettingCard(self.firstLineColor)
        self.addSettingCard(self.firstLineBold)
        self.addSettingCard(self.secondLineType)
        self.addSettingCard(self.secondLineColor)
        self.addSettingCard(self.secondLineBold)
        self.addSettingCard(self.thirdLineType)
        self.addSettingCard(self.thirdLineColor)
        self.addSettingCard(self.thirdLineBold)
        self.addSettingCard(self.simpleScale)
        self.addSettingCard(self.simplePaddingScale)

        self._firstLineTypeChanged(self.firstLineTypeValue.description)
        self._secondLineTypeChanged(self.secondLineTypeValue.description)
        self._thirdLineTypeChanged(self.thirdLineTypeValue.description)

    def __set_settings(self):
        self.firstLineType.comboBox.setCurrentText(self.firstLineTypeValue.description)
        self.firstLineColor.setColor(self.firstLineColorValue)
        self.firstLineBold.setValue(self.firstLineBoldValue)

        self.secondLineType.setCurrentText(self.secondLineTypeValue.description)
        self.secondLineColor.setColor(self.secondLineColorValue)
        self.secondLineBold.setValue(self.secondLineBoldValue)

        self.thirdLineType.setCurrentText(self.thirdLineTypeValue.description)
        self.thirdLineColor.setColor(self.thirdLineColorValue)
        self.thirdLineBold.setValue(self.thirdLineBoldValue)

        self.simpleScale.setValue(self.simpleScaleValue)
        self.simplePaddingScale.setValue(self.simplePaddingScaleValue)

    def __connect_signals(self):
        self.firstLineType.comboBox.currentTextChanged.connect(self._firstLineTypeChanged)
        self.firstLineColor.colorChanged.connect(
            lambda text: setattr(self, "firstLineColorValue", text))
        self.firstLineBold.checkedChanged.connect(
            lambda text: setattr(self, "firstLineBoldValue", text))

        self.secondLineType.comboBox.currentTextChanged.connect(self._secondLineTypeChanged)
        self.secondLineColor.colorChanged.connect(
            lambda text: setattr(self, "secondLineColorValue", text))
        self.secondLineBold.checkedChanged.connect(
            lambda text: setattr(self, "secondLineBoldValue", text))
        
        self.thirdLineType.comboBox.currentTextChanged.connect(self._thirdLineTypeChanged)
        self.thirdLineColor.colorChanged.connect(
            lambda text: setattr(self, "thirdLineColorValue", text))
        self.thirdLineBold.checkedChanged.connect(
            lambda text: setattr(self, "thirdLineBoldValue", text))
        
        self.simpleScale.valueChanged.connect(
            lambda text: setattr(self, "simpleScaleValue", text))
        self.simplePaddingScale.valueChanged.connect(
            lambda text: setattr(self, "simplePaddingScaleValue", text))
        
    def _firstLineTypeChanged(self, text):
        self.firstLineTypeValue = DISPLAY_TYPE.from_desc(text)
        self.firstLineColor.setHidden(self.firstLineTypeValue == DISPLAY_TYPE.NONE)
        self.firstLineBold.setHidden(self.firstLineTypeValue == DISPLAY_TYPE.NONE)

    def _secondLineTypeChanged(self, text):
        self.secondLineTypeValue = DISPLAY_TYPE.from_desc(text)
        self.secondLineColor.setHidden(self.secondLineTypeValue == DISPLAY_TYPE.NONE)
        self.secondLineBold.setHidden(self.secondLineTypeValue == DISPLAY_TYPE.NONE)

    def _thirdLineTypeChanged(self, text):
        self.thirdLineTypeValue = DISPLAY_TYPE.from_desc(text)
        self.thirdLineColor.setHidden(self.thirdLineTypeValue == DISPLAY_TYPE.NONE)
        self.thirdLineBold.setHidden(self.thirdLineTypeValue == DISPLAY_TYPE.NONE)
        
    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def load_style(self, style_content):
        """加载样式内容"""
        self.firstLineTypeValue = DISPLAY_TYPE.from_str(style_content["Layout"].get("SimpleFirstLineType", "Model"))
        self.firstLineColorValue = QColor(style_content["Layout"].get("SimpleFirstLineColor", "#212121"))
        self.firstLineBoldValue = style_content["Layout"].get("SimpleFirstLineBold", False)

        self.secondLineTypeValue = DISPLAY_TYPE.from_str(style_content["Layout"].get("SimpleSecondLineType", "Param"))
        self.secondLineColorValue = QColor(style_content["Layout"].get("SimpleSecondLineColor", "#757575"))
        self.secondLineBoldValue = style_content["Layout"].get("SimpleSecondLineBold", False)

        self.thirdLineTypeValue = DISPLAY_TYPE.from_str(style_content["Layout"].get("SimpleThirdLineType", "Datetime"))
        self.thirdLineColorValue = QColor(style_content["Layout"].get("SimpleThirdLineColor", "#757575"))
        self.thirdLineBoldValue = style_content["Layout"].get("SimpleThirdLineBold", False)

        self.simpleScaleValue = int(style_content["Layout"].get("SimpleScale", 0.16) * 100)
        self.simplePaddingScaleValue = int(style_content["Layout"].get("SimplePaddingScale", 0.1) * 100)

    def save_style(self):
        """保存样式内容"""
        cfg.set(cfg.simpleFirstLineType, self.firstLineTypeValue.value)
        cfg.set(cfg.simpleFirstLineColor, self.firstLineColorValue.name())
        cfg.set(cfg.simpleFirstLineBold, self.firstLineBoldValue)

        cfg.set(cfg.simpleSecondLineType, self.secondLineTypeValue.value)
        cfg.set(cfg.simpleSecondLineColor, self.secondLineColorValue.name())
        cfg.set(cfg.simpleSecondLineBold, self.secondLineBoldValue)

        cfg.set(cfg.simpleThirdLineType, self.thirdLineTypeValue.value)
        cfg.set(cfg.simpleThirdLineColor, self.thirdLineColorValue.name())
        cfg.set(cfg.simpleThirdLineBold, self.thirdLineBoldValue)

        cfg.set(cfg.simpleScale, self.simpleScaleValue / 100)
        cfg.set(cfg.simplePaddingScale, self.simplePaddingScaleValue / 100)