from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    SwitchSettingCard,
    SpinBoxSettingCard
)
from app.config import cfg


class GlobalGroup(SettingCardGroup):
    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "GlobalGroup", "全局"), parent=parent)
        self.__init_values()
        self.__setup_sub_layout()
        self.__set_settings()
        self.__connect_signals()

    def __init_values(self):
        # 全局样式
        self.useEquivalentFocalValue = cfg.useEquivalentFocal.value
        self.useOriginRatioPaddingValue = cfg.useOriginRatioPadding.value
        self.backgroundBlurValue = cfg.backgroundBlur.value
        self.addShadowValue = cfg.addShadow.value
        self.whiteMarginValue = cfg.whiteMargin.value
        self.whiteMarginWidthValue = cfg.whiteMarginWidth.value

    def __setup_sub_layout(self):
        # 使用等效聚焦
        self.useEquivalentFocal = SwitchSettingCard(
            FIF.PIN,
            self.tr("使用等效焦距"),
            self.tr("是否使用等效焦距"),
            None,
            self
        )

        # 使用原始比例填充
        self.useOriginRatioPadding = SwitchSettingCard(
            FIF.ALBUM,
            self.tr("使用原始比例填充"),
            self.tr("是否使用原始比例填充"),
            None,
            self
        )

        self.backgroundBlur = SwitchSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("背景模糊"),
            self.tr("是否设置背景模糊"),
            None,
            self
        )

        # 添加阴影
        self.addShadow = SwitchSettingCard(
            FIF.LEAF,
            self.tr("添加阴影"),
            self.tr("是否添加阴影"),
            None,
            self
        )

        # 添加白色间距
        self.whiteMargin = SwitchSettingCard(
            FIF.COPY,
            self.tr("白色间距"),
            self.tr("是否添加白色间距"),
            None,
            self
        )

        # 白色间距宽度
        self.whiteMarginWidth = SpinBoxSettingCard(
            FIF.COPY,
            self.tr("白色间距宽度"),
            self.tr("设置白色间距宽度"),
            minimum=0,
            maximum=10,
        )

        # 全局样式
        self.addSettingCard(self.useEquivalentFocal)
        self.addSettingCard(self.useOriginRatioPadding)
        self.addSettingCard(self.backgroundBlur)
        self.addSettingCard(self.addShadow)
        self.addSettingCard(self.whiteMargin)
        self.addSettingCard(self.whiteMarginWidth)

    def __set_settings(self):
        # 全局样式
        self.useEquivalentFocal.setValue(self.useEquivalentFocalValue)
        self.useOriginRatioPadding.setValue(self.useOriginRatioPaddingValue)
        self.backgroundBlur.setValue(self.backgroundBlurValue)
        self.addShadow.setValue(self.addShadowValue)
        self.whiteMargin.setValue(self.whiteMarginValue)
        self.whiteMarginWidth.setValue(self.whiteMarginWidthValue)

    def __connect_signals(self):
        # 全局样式
        self.whiteMarginWidth.valueChanged.connect(
            lambda text: setattr(self, "whiteMarginWidthValue", text))
        self.useEquivalentFocal.checkedChanged.connect(
            lambda text: setattr(self, "useEquivalentFocalValue", text))
        self.useOriginRatioPadding.checkedChanged.connect(
            lambda text: setattr(self, "useOriginRatioPaddingValue", text))
        self.backgroundBlur.checkedChanged.connect(
            lambda text: setattr(self, "backgroundBlurValue", text))
        self.addShadow.checkedChanged.connect(
            lambda text: setattr(self, "addShadowValue", text))
        self.whiteMargin.checkedChanged.connect(
            lambda text: setattr(self, "whiteMarginValue", text))

    def reset_style(self):
        self.__initValues()
        self.__setSettings()

    def load_style(self, style_content):
        # 全局样式
        self.useEquivalentFocalValue = style_content["Global"]["UseEquivalentFocal"]
        self.useOriginRatioPaddingValue = style_content["Global"]["UseOriginRatioPadding"]
        self.backgroundBlurValue = style_content["Global"]["BackgroundBlur"]
        self.addShadowValue = style_content["Global"]["AddShadow"]
        self.whiteMarginValue = style_content["Global"]["WhiteMargin"]
        self.whiteMarginWidthValue = int(
            style_content["Global"]["WhiteMarginWidth"])

    def save_style(self):
        # 全局样式
        cfg.set(cfg.useEquivalentFocal, self.useEquivalentFocalValue)
        cfg.set(cfg.useOriginRatioPadding, self.useOriginRatioPaddingValue)
        cfg.set(cfg.backgroundBlur, self.backgroundBlurValue)
        cfg.set(cfg.addShadow, self.addShadowValue)
        cfg.set(cfg.whiteMargin, self.whiteMarginValue)
        cfg.set(cfg.whiteMarginWidth, self.whiteMarginWidthValue)
