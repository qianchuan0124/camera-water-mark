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

# 左右排布，两行标准布局


class StandardLayout(SettingCardGroup):

    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "ClassicalLayout", "标准布局"), parent=parent)
        self.__init_values()
        self.__setup_sub_layout()
        self.__set_settings()
        self.__connect_signals()

    def __setup_sub_layout(self):
      # 左上角类型
        self.leftTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左上角类型"),
            self.tr("设置左上角展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions(),
        )

        # 左上角字体颜色
        self.leftTopColor = ColorSettingCard(
            self.leftTopFontColorValue,
            FIF.PALETTE,
            self.tr("左上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 左上角字体粗细
        self.leftTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
            self
        )

        # 左下角类型
        self.leftBottomType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左下角类型"),
            self.tr("设置左下角展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions(),
        )

        # 左下角字体颜色
        self.leftBottomColor = ColorSettingCard(
            self.leftBottomFontColorValue,
            FIF.PALETTE,
            self.tr("左下角字体颜色"),
            self.tr("设置左下角字体颜色"),
        )

        # 左下角字体粗细
        self.leftBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左下角字体是否加粗"),
            self.tr("设置左下角字体是否加粗"),
            None,
            self
        )

        # 右上角类型
        self.rightTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("右上角类型"),
            self.tr("设置右上角展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions(),
        )

        # 右上角字体颜色
        self.rightTopColor = ColorSettingCard(
            self.rightTopFontColorValue,
            FIF.PALETTE,
            self.tr("右上角字体颜色"),
            self.tr("设置右上角字体颜色"),
        )

        # 右上角字体粗细
        self.rightTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("右上角字体是否加粗"),
            self.tr("设置右上角字体是否加粗"),
            None,
            self
        )

        # 右下角类型
        self.rightBottomType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("右下角类型"),
            self.tr("设置右下角展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions(),
        )

        # 右下角字体颜色
        self.rightBottomColor = ColorSettingCard(
            self.rightBottomFontColorValue,
            FIF.PALETTE,
            self.tr("右下角字体颜色"),
            self.tr("设置右下角字体颜色"),
        )

        # 右下角字体粗细
        self.rightBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("右下角字体是否加粗"),
            self.tr("设置右下角字体是否加粗"),
            None,
            self
        )

        self.verticalPadding = SpinBoxSettingCard(
            FIF.UNIT,
            self.tr("纵向留白占比"),
            self.tr("纵向留白百分比, -1表示自适应留白"),
            minimum=-1,
            maximum=100
        )

        self.leftPadding = SpinBoxSettingCard(
            FIF.UNIT,
            self.tr("左侧间距"),
            self.tr("左侧留白距离"),
            minimum=-2000,
            maximum=2000
        )

        self.rightPadding = SpinBoxSettingCard(
            FIF.UNIT,
            self.tr("右侧间距"),
            self.tr("右侧留白距离"),
            minimum=-2000,
            maximum=2000
        )

        self.addSettingCard(self.leftTopType)
        self.addSettingCard(self.leftTopColor)
        self.addSettingCard(self.leftTopBold)
        self.addSettingCard(self.leftBottomType)
        self.addSettingCard(self.leftBottomColor)
        self.addSettingCard(self.leftBottomBold)
        self.addSettingCard(self.rightTopType)
        self.addSettingCard(self.rightTopColor)
        self.addSettingCard(self.rightTopBold)
        self.addSettingCard(self.rightBottomType)
        self.addSettingCard(self.rightBottomColor)
        self.addSettingCard(self.rightBottomBold)

        self.addSettingCard(self.verticalPadding)
        self.addSettingCard(self.leftPadding)
        self.addSettingCard(self.rightPadding)

        self._leftTopTypeChanged(self.leftTopTypeValue.description)
        self._leftBottomTypeChanged(self.leftBottomTypeValue.description)
        self._rightBottomTypeChanged(self.rightBottomTypeValue.description)
        self._rightTopTypeChanged(self.rightTopTypeValue.description)

    def __init_values(self):
        # 布局样式
        self.leftTopTypeValue = DISPLAY_TYPE.from_str(cfg.leftTopType.value)
        self.leftTopFontColorValue = QColor(cfg.leftTopFontColor.value)
        self.leftTopBoldValue = cfg.leftTopBold.value

        self.leftBottomTypeValue = DISPLAY_TYPE.from_str(
            cfg.leftBottomType.value)
        self.leftBottomFontColorValue = QColor(cfg.leftBottomFontColor.value)
        self.leftBottomBoldValue = cfg.leftBottomBold.value

        self.rightTopTypeValue = DISPLAY_TYPE.from_str(cfg.rightTopType.value)
        self.rightTopFontColorValue = QColor(cfg.rightTopFontColor.value)
        self.rightTopBoldValue = cfg.rightTopBold.value

        self.rightBottomTypeValue = DISPLAY_TYPE.from_str(
            cfg.rightBottomType.value)
        self.rightBottomFontColorValue = QColor(cfg.rightBottomFontColor.value)
        self.rightBottomBoldValue = cfg.rightBottomBold.value

        self.verticalPaddingValue = int(cfg.standardVerticalPadding.value * 100)
        self.leftPaddingValue = cfg.standardLeftPadding.value
        self.rightPaddingValue = cfg.standardRightPadding.value

    def __set_settings(self):
        # 布局样式
        self.leftTopType.comboBox.setCurrentText(
            self.leftTopTypeValue.description)
        self.leftTopColor.setColor(self.leftTopFontColorValue)
        self.leftTopBold.setValue(self.leftTopBoldValue)

        self.leftBottomType.comboBox.setCurrentText(
            self.leftBottomTypeValue.description)
        self.leftBottomColor.setColor(self.leftBottomFontColorValue)
        self.leftBottomBold.setValue(self.leftBottomBoldValue)

        self.rightTopType.comboBox.setCurrentText(
            self.rightTopTypeValue.description)
        self.rightTopColor.setColor(self.rightTopFontColorValue)
        self.rightTopBold.setValue(self.rightTopBoldValue)

        self.rightBottomType.comboBox.setCurrentText(
            self.rightBottomTypeValue.description)
        self.rightBottomColor.setColor(self.rightBottomFontColorValue)
        self.rightBottomBold.setValue(self.rightBottomBoldValue)

        self.verticalPadding.setValue(self.verticalPaddingValue)
        self.leftPadding.setValue(self.leftPaddingValue)
        self.rightPadding.setValue(self.rightPaddingValue)

    def __connect_signals(self):
        # 左上角
        self.leftTopType.currentTextChanged.connect(self._leftTopTypeChanged)
        self.leftTopColor.colorChanged.connect(
            lambda text: setattr(self, "leftTopFontColorValue", text))
        self.leftTopBold.checkedChanged.connect(
            lambda text: setattr(self, "leftTopBoldValue", text))

        # 左下角
        self.leftBottomType.currentTextChanged.connect(self._leftBottomTypeChanged)
        self.leftBottomColor.colorChanged.connect(
            lambda text: setattr(self, "leftBottomFontColorValue", text))
        self.leftBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "leftBottomBoldValue", text))

        # 右上角
        self.rightTopType.currentTextChanged.connect(self._rightTopTypeChanged)
        self.rightTopColor.colorChanged.connect(
            lambda text: setattr(self, "rightTopFontColorValue", text))
        self.rightTopBold.checkedChanged.connect(
            lambda text: setattr(self, "rightTopBoldValue", text))

        # 右下角
        self.rightBottomType.currentTextChanged.connect(self._rightBottomTypeChanged)
        self.rightBottomColor.colorChanged.connect(
            lambda text: setattr(self, "rightBottomFontColorValue", text))
        self.rightBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "rightBottomBoldValue", text))
        
        # 间距设置
        self.verticalPadding.valueChanged.connect(
            lambda text: setattr(self, "verticalPaddingValue", text))
        self.leftPadding.valueChanged.connect(
            lambda text: setattr(self, "leftPaddingValue", text))
        self.rightPadding.valueChanged.connect(
            lambda text: setattr(self, "rightPaddingValue", text))
        
    def _leftTopTypeChanged(self, text):
        self.leftTopTypeValue = DISPLAY_TYPE.from_desc(text)
        self.leftTopBold.setHidden(self.leftTopTypeValue is DISPLAY_TYPE.NONE)
        self.leftTopColor.setHidden(self.leftTopTypeValue is DISPLAY_TYPE.NONE)
    
    def _leftBottomTypeChanged(self, text):
        self.leftBottomTypeValue = DISPLAY_TYPE.from_desc(text)
        self.leftBottomBold.setHidden(self.leftBottomTypeValue is DISPLAY_TYPE.NONE)
        self.leftBottomColor.setHidden(self.leftBottomTypeValue is DISPLAY_TYPE.NONE)
    
    def _rightTopTypeChanged(self, text):
        self.rightTopTypeValue = DISPLAY_TYPE.from_desc(text)
        self.rightTopBold.setHidden(self.rightTopTypeValue is DISPLAY_TYPE.NONE)
        self.rightTopColor.setHidden(self.rightTopTypeValue is DISPLAY_TYPE.NONE)
    
    def _rightBottomTypeChanged(self, text):
        self.rightBottomTypeValue = DISPLAY_TYPE.from_desc(text)
        self.rightBottomBold.setHidden(self.rightBottomTypeValue is DISPLAY_TYPE.NONE)
        self.rightBottomColor.setHidden(self.rightBottomTypeValue is DISPLAY_TYPE.NONE)

    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def load_style(self, style_content):
        # 布局样式
        self.leftTopTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["LeftTopType"])
        self.leftTopFontColorValue = QColor(
            style_content["Layout"]["LeftTopFontColor"])
        self.leftTopColor.setColor(self.leftTopFontColorValue)
        self.leftTopBoldValue = style_content["Layout"]["LeftTopBold"]

        self.leftBottomTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["LeftBottomType"])
        self.leftBottomFontColorValue = QColor(
            style_content["Layout"]["LeftBottomFontColor"])
        self.leftBottomColor.setColor(self.leftBottomFontColorValue)
        self.leftBottomBoldValue = style_content["Layout"]["LeftBottomBold"]

        self.rightTopTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["RightTopType"])
        self.rightTopFontColorValue = QColor(
            style_content["Layout"]["RightTopFontColor"])
        self.rightTopColor.setColor(self.rightTopFontColorValue)
        self.rightTopBoldValue = style_content["Layout"]["RightTopBold"]

        self.rightBottomTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["RightBottomType"])
        self.rightBottomFontColorValue = QColor(
            style_content["Layout"]["RightBottomFontColor"])
        self.rightBottomColor.setColor(self.rightBottomFontColorValue)
        self.rightBottomBoldValue = style_content["Layout"]["RightBottomBold"]

        self.verticalPaddingValue = int(
            style_content["Layout"].get("StandardVerticalPadding", 0.50) * 100)
        self.leftPaddingValue = style_content["Layout"].get(
            "StandardLeftPadding", 200)
        self.rightPaddingValue = style_content["Layout"].get(
            "StandardRightPadding", 200)

    def save_style(self):
        # 布局样式
        cfg.set(cfg.leftTopType, self.leftTopTypeValue.value)
        cfg.set(cfg.leftTopFontColor, self.leftTopFontColorValue.name())
        cfg.set(cfg.leftTopBold, self.leftTopBoldValue)

        cfg.set(cfg.leftBottomType, self.leftBottomTypeValue.value)
        cfg.set(cfg.leftBottomFontColor, self.leftBottomFontColorValue.name())
        cfg.set(cfg.leftBottomBold, self.leftBottomBoldValue)

        cfg.set(cfg.rightTopType, self.rightTopTypeValue.value)
        cfg.set(cfg.rightTopFontColor, self.rightTopFontColorValue.name())
        cfg.set(cfg.rightTopBold, self.rightTopBoldValue)

        cfg.set(cfg.rightBottomType, self.rightBottomTypeValue.value)
        cfg.set(cfg.rightBottomFontColor,
                self.rightBottomFontColorValue.name())
        cfg.set(cfg.rightBottomBold, self.rightBottomBoldValue)

        cfg.set(cfg.standardVerticalPadding, self.verticalPaddingValue / 100)
        cfg.set(cfg.standardLeftPadding, self.leftPaddingValue)
        cfg.set(cfg.standardRightPadding, self.rightPaddingValue)
