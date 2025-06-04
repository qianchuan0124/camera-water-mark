from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    ComboBoxSettingCard,
    ColorSettingCard,
    SwitchSettingCard
)
from app.entity.enums import DISPLAY_TYPE
from app.config import cfg

# 左右排布，两行经典布局


class ClassicalLayout(SettingCardGroup):

    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "ClassicalLayout", "经典布局"), parent=parent)
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
            self.tr("设置左上角字体颜色"),
        )

        # 左下角字体粗细
        self.leftBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左下角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
            self
        )

        # 右上角类型
        self.rightTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("右上角类型"),
            self.tr("设置左上角展示信息的类型"),
            texts=DISPLAY_TYPE.all_descriptions(),
        )

        # 右上角字体颜色
        self.rightTopColor = ColorSettingCard(
            self.rightTopFontColorValue,
            FIF.PALETTE,
            self.tr("右上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 右上角字体粗细
        self.rightTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
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

    def __connect_signals(self):
        # 左上角
        self.leftTopType.currentTextChanged.connect(
            lambda text: setattr(self, "leftTopTypeValue", DISPLAY_TYPE.from_desc(text)))
        self.leftTopColor.colorChanged.connect(
            lambda text: setattr(self, "leftTopFontColorValue", text))
        self.leftTopBold.checkedChanged.connect(
            lambda text: setattr(self, "leftTopBoldValue", text))

        # 左下角
        self.leftBottomType.currentTextChanged.connect(
            lambda text: setattr(self, "leftBottomTypeValue", DISPLAY_TYPE.from_desc(text)))
        self.leftBottomColor.colorChanged.connect(
            lambda text: setattr(self, "leftBottomFontColorValue", text))
        self.leftBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "leftBottomBoldValue", text))

        # 右上角
        self.rightTopType.currentTextChanged.connect(
            lambda text: setattr(self, "rightTopTypeValue", DISPLAY_TYPE.from_desc(text)))
        self.rightTopColor.colorChanged.connect(
            lambda text: setattr(self, "rightTopFontColorValue", text))
        self.rightTopBold.checkedChanged.connect(
            lambda text: setattr(self, "rightTopBoldValue", text))

        # 右下角
        self.rightBottomType.currentTextChanged.connect(
            lambda text: setattr(self, "rightBottomTypeValue", DISPLAY_TYPE.from_desc(text)))
        self.rightBottomColor.colorChanged.connect(
            lambda text: setattr(self, "rightBottomFontColorValue", text))
        self.rightBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "rightBottomBoldValue", text))

    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def load_style(self, style_content):
        # 布局样式
        self.leftTopTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["LeftTopType"])
        self.leftTopFontColorValue = QColor(
            style_content["Layout"]["LeftTopFontColor"])
        self.leftTopBoldValue = style_content["Layout"]["LeftTopBold"]

        self.leftBottomTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["LeftBottomType"])
        self.leftBottomFontColorValue = QColor(
            style_content["Layout"]["LeftBottomFontColor"])
        self.leftBottomBoldValue = style_content["Layout"]["LeftBottomBold"]

        self.rightTopTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["RightTopType"])
        self.rightTopFontColorValue = QColor(
            style_content["Layout"]["RightTopFontColor"])
        self.rightTopBoldValue = style_content["Layout"]["RightTopBold"]

        self.rightBottomTypeValue = DISPLAY_TYPE.from_str(
            style_content["Layout"]["RightBottomType"])
        self.rightBottomFontColorValue = QColor(
            style_content["Layout"]["RightBottomFontColor"])
        self.rightBottomBoldValue = style_content["Layout"]["RightBottomBold"]

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
