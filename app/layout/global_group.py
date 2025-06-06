from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    SwitchSettingCard,
    SpinBoxSettingCard,
    ColorSettingCard
)
from app.config import cfg
from app.utils.image_handle import qcolor_to_hex, hex_to_qcolor


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
        self.blurExtentValue = cfg.blurExtent.value
        self.blurHorizontalPaddingValue = int(cfg.blurHorizontalPadding.value * 100)
        self.blurTopPaddingValue = int(cfg.blurTopPadding.value * 100)
        self.blurBottomPaddingValue = int(cfg.blurBottomPadding.value * 100)

        self.addShadowValue = cfg.addShadow.value
        self.shadowBlurValue = cfg.shadowBlur.value
        self.shadowColorValue = hex_to_qcolor(cfg.shadowColor.value)

        self.whiteMarginValue = cfg.whiteMargin.value
        self.whiteMarginWidthValue = cfg.whiteMarginWidth.value
        self.whiteMarginColorValue = hex_to_qcolor(cfg.whiteMarginColor.value)

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

        # 背景模糊
        self.backgroundBlur = SwitchSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("背景模糊"),
            self.tr("是否设置背景模糊"),
            None,
            self
        )

        self.blurExtent = SpinBoxSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("模糊程度"),
            self.tr("高斯模糊参数, 数值越大模糊"),
            minimum=0,
            maximum=100
        )

        self.blurHorizontalPadding = SpinBoxSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("水平间距"),
            self.tr("前景图距离模糊背景的水平间距百分比"),
            minimum=0,
            maximum=100
        )

        self.blurTopPadding = SpinBoxSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("顶部间距"),
            self.tr("前景图距离模糊背景的顶部间距百分比"),
            minimum=0,
            maximum=100
        )

        self.blurBottomPadding = SpinBoxSettingCard(
            FIF.BACKGROUND_FILL,
            self.tr("底部间距"),
            self.tr("前景图距离模糊背景的底部间距百分比"),
            minimum=0,
            maximum=100
        )

        # 添加阴影
        self.addShadow = SwitchSettingCard(
            FIF.LEAF,
            self.tr("添加阴影"),
            self.tr("是否添加阴影"),
            None,
            self
        )

        self.shadowBlur = SpinBoxSettingCard(
            FIF.LEAF,
            self.tr("模糊程度"),
            self.tr("阴影模糊程度, 数值越大模糊"),
            minimum=0,
            maximum=100
        )

        self.shadowColor = ColorSettingCard(
            self.shadowColorValue,
            FIF.LEAF,
            self.tr("阴影颜色"),
            self.tr("设置照片阴影颜色"),
            enableAlpha=True
        )

        # 添加外部边框
        self.whiteMargin = SwitchSettingCard(
            FIF.COPY,
            self.tr("外部边框"),
            self.tr("是否添加外部边框"),
            None,
            self
        )

        # 外部边框宽度
        self.whiteMarginWidth = SpinBoxSettingCard(
            FIF.COPY,
            self.tr("边框宽度"),
            self.tr("设置外部边框宽度"),
            minimum=0,
            maximum=10,
        )

        self.whiteMarginColor = ColorSettingCard(
            self.whiteMarginColorValue,
            FIF.COPY,
            self.tr("边框颜色"),
            self.tr("设置外部边框颜色"),
            enableAlpha=True
        )

        # 全局样式
        self.addSettingCard(self.useEquivalentFocal)
        self.addSettingCard(self.useOriginRatioPadding)

        self.addSettingCard(self.backgroundBlur)
        self.addSettingCard(self.blurExtent)
        self.addSettingCard(self.blurHorizontalPadding)
        self.addSettingCard(self.blurTopPadding)
        self.addSettingCard(self.blurBottomPadding)

        self.addSettingCard(self.addShadow)
        self.addSettingCard(self.shadowBlur)
        self.addSettingCard(self.shadowColor)

        self.addSettingCard(self.whiteMargin)
        self.addSettingCard(self.whiteMarginWidth)
        self.addSettingCard(self.whiteMarginColor)

    def __set_settings(self):
        # 全局样式
        self.useEquivalentFocal.setValue(self.useEquivalentFocalValue)
        self.useOriginRatioPadding.setValue(self.useOriginRatioPaddingValue)

        self.backgroundBlur.setValue(self.backgroundBlurValue)
        self.blurExtent.setValue(self.blurExtentValue)
        self.blurHorizontalPadding.setValue(self.blurHorizontalPaddingValue)
        self.blurTopPadding.setValue(self.blurTopPaddingValue)
        self.blurBottomPadding.setValue(self.blurBottomPaddingValue)

        self.addShadow.setValue(self.addShadowValue)
        self.shadowColor.setColor(self.shadowColorValue)
        self.shadowBlur.setValue(self.shadowBlurValue)

        self.whiteMargin.setValue(self.whiteMarginValue)
        self.whiteMarginWidth.setValue(self.whiteMarginWidthValue)
        self.whiteMarginColor.setColor(self.whiteMarginColorValue)

    def __connect_signals(self):
        # 全局样式
        self.useEquivalentFocal.checkedChanged.connect(
            lambda text: setattr(self, "useEquivalentFocalValue", text))
        self.useOriginRatioPadding.checkedChanged.connect(
            lambda text: setattr(self, "useOriginRatioPaddingValue", text))
        
        self.backgroundBlur.checkedChanged.connect(self.__on_backgound_blur_changed)
        self.blurExtent.valueChanged.connect(
            lambda text: setattr(self, "blurExtentValue", text))
        self.blurHorizontalPadding.valueChanged.connect(
            lambda text: setattr(self, "blurHorizontalPaddingValue", text))
        self.blurTopPadding.valueChanged.connect(
            lambda text: setattr(self, "blurTopPaddingValue", text))
        self.blurBottomPadding.valueChanged.connect(
            lambda text: setattr(self, "blurBottomPaddingValue", text)) 

        self.addShadow.checkedChanged.connect(self.__on_add_shadow_changed)
        self.shadowColor.colorChanged.connect(
            lambda text: setattr(self, "shadowColorValue", text))
        self.shadowBlur.valueChanged.connect(
            lambda text: setattr(self, "shadowBlurValue", text))

        
        self.whiteMargin.checkedChanged.connect(self.__on_white_margin_changed)
        self.whiteMarginWidth.valueChanged.connect(lambda text: setattr(self, "whiteMarginWidthValue", text))
        self.whiteMarginColor.colorChanged.connect(
            lambda text: setattr(self, "whiteMarginColorValue", text))

    def __on_backgound_blur_changed(self, value):
        """处理背景模糊开关变化的逻辑"""
        self.backgroundBlurValue = value
        self.blurExtent.setHidden(not value)
        self.blurHorizontalPadding.setHidden(not value)
        self.blurTopPadding.setHidden(not value)
        self.blurBottomPadding.setHidden(not value)

    def __on_add_shadow_changed(self, value):
        """处理添加阴影开关变化的逻辑"""
        self.addShadowValue = value
        self.shadowBlur.setHidden(not value)
        self.shadowColor.setHidden(not value)

    def __on_white_margin_changed(self, value):
        """处理添加外部边框开关变化的逻辑"""
        self.whiteMarginValue = value
        self.whiteMarginWidth.setHidden(not value)
        self.whiteMarginColor.setHidden(not value)

    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def load_style(self, style_content):
        # 全局样式
        self.useEquivalentFocalValue = style_content["Global"]["UseEquivalentFocal"]
        self.useOriginRatioPaddingValue = style_content["Global"]["UseOriginRatioPadding"]

        self.backgroundBlurValue = style_content["Global"].get("BackgroundBlur", False)
        self.blurExtentValue = int(style_content["Global"].get("BlurExtent", 35))
        self.blurHorizontalPaddingValue = int(style_content["Global"].get("BlurHorizontalPadding", 0.09) * 100)
        self.blurTopPaddingValue = int(style_content["Global"].get("BlurTopPadding", 0.09) * 100)
        self.blurBottomPaddingValue = int(style_content["Global"].get("BlurBottomPadding", 0.09) * 100)
        self.backgroundBlur.setChecked(self.backgroundBlurValue)
        self.__on_backgound_blur_changed(self.backgroundBlurValue)

        self.addShadowValue = style_content["Global"].get("AddShadow", False)
        self.shadowColorValue = hex_to_qcolor(
            style_content["Global"].get("ShadowColor", "#00000000"))
        self.shadowBlurValue = int(style_content["Global"].get("ShadowBlur", 20))
        print(f"get shadow color: {self.shadowColorValue}")
        self.addShadow.setChecked(self.addShadowValue)
        self.__on_add_shadow_changed(self.addShadowValue)

        self.whiteMarginValue = style_content["Global"]["WhiteMargin"]
        self.whiteMarginWidthValue = int(
            style_content["Global"]["WhiteMarginWidth"])
        self.whiteMarginColorValue = hex_to_qcolor(
            style_content["Global"].get("WhiteMarginColor", "#ffffff"))
        self.whiteMargin.setChecked(self.whiteMarginValue)
        self.__on_white_margin_changed(self.whiteMarginValue)

    def save_style(self):
        # 全局样式
        cfg.set(cfg.useEquivalentFocal, self.useEquivalentFocalValue)
        cfg.set(cfg.useOriginRatioPadding, self.useOriginRatioPaddingValue)

        cfg.set(cfg.backgroundBlur, self.backgroundBlurValue)
        cfg.set(cfg.blurExtent, self.blurExtentValue)
        cfg.set(cfg.blurHorizontalPadding, float(self.blurHorizontalPaddingValue / 100))
        cfg.set(cfg.blurTopPadding, float(self.blurTopPaddingValue / 100))
        cfg.set(cfg.blurBottomPadding, float(self.blurBottomPaddingValue / 100))

        cfg.set(cfg.addShadow, self.addShadowValue)
        cfg.set(cfg.shadowColor, qcolor_to_hex(self.shadowColorValue))
        cfg.set(cfg.shadowBlur, self.shadowBlurValue)

        cfg.set(cfg.whiteMargin, self.whiteMarginValue)
        cfg.set(cfg.whiteMarginWidth, self.whiteMarginWidthValue)
        cfg.set(cfg.whiteMarginColor, qcolor_to_hex(self.whiteMarginColorValue))
