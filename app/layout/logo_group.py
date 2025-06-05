from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import SettingCardGroup, FluentIcon as FIF
from app.components.common_card import (
    ComboBoxSettingCard,
    SwitchSettingCard,
    SpinBoxSettingCard
)
from app.config import cfg
from app.entity.enums import LOGO_LAYOUT
from app.components.custom_logo_path_card import CustomLogoPathCard


class LogoGroup(SettingCardGroup):
    def __init__(self, parent=None):
        super().__init__(title=QCoreApplication.translate(
            "LogoGroup", "LOGO"), parent=parent)
        self.__init_values()
        self.__setup_sub_layout()
        self.__set_settings()
        self.__connect_signals()

    def __init_values(self):
        # LOGO样式
        self.logoEnableValue = cfg.logoEnable.value
        self.logoLayoutValue = LOGO_LAYOUT.LEFT if cfg.isLogoLeft else LOGO_LAYOUT.RIGHT
        self.logoSizeValue = int(cfg.simpleLogoSize.value * 100)
        self.customLogoEnableValue = cfg.customLogoEnable.value
        self.customLogoPathValue = cfg.customLogoPath.value

    def __setup_sub_layout(self):
        # LOGO样式
        self.logoEnable = SwitchSettingCard(
            FIF.LAYOUT,
            self.tr("展示LOGO"),
            self.tr("是否展示LOGO"),
            None,
            self
        )

        self.logoLayout = ComboBoxSettingCard(
            FIF.LAYOUT,
            self.tr("LOGO布局"),
            self.tr("设置LOGO布局样式"),
            texts=LOGO_LAYOUT.all_values(),
        )

        self.logoSize = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("LOGO大小"),
            self.tr("设置LOGO的大小比例"),
            minimum=1,
            maximum=100
        )

        self.customLogo = CustomLogoPathCard(self)

        # LOGO样式
        self.addSettingCard(self.logoEnable)
        self.addSettingCard(self.logoSize)
        self.addSettingCard(self.logoLayout)
        self.addSettingCard(self.customLogo)

    def __set_settings(self):
        # LOGO样式
        self.logoEnable.setValue(self.logoEnableValue)
        self.logoLayout.comboBox.setCurrentText(self.logoLayoutValue.value)
        self.logoSize.setValue(self.logoSizeValue)
        self.customLogo.setChecked(self.customLogoEnableValue)
        self.customLogo.setPath(self.customLogoPathValue)

    def __connect_signals(self):
        # LOGO样式

        self.logoEnable.checkedChanged.connect(self.on_logo_enable_changed)
        self.logoLayout.currentTextChanged.connect(lambda text: setattr(
            self, "logoLayoutValue", LOGO_LAYOUT.get_enum(text)))
        self.logoSize.valueChanged.connect(lambda text: setattr(self, "logoSizeValue", text))
        self.customLogo.checkedChanged.connect(lambda text: setattr(
            self, "customLogoEnableValue", text))
        self.customLogo.pathChanged.connect(
            lambda text: setattr(self, "customLogoPathValue", text))

    def on_logo_enable_changed(self, logoEnable):
        self.logoEnableValue = logoEnable
        self.logoLayout.setHidden(not self.logoEnableValue)
        self.customLogo.setHidden(not self.logoEnableValue)

    def set_sub_hiddens(self, isSimple):
        self.logoSize.setHidden(not isSimple)
        self.logoLayout.setHidden(isSimple)

    def reset_style(self):
        self.__init_values()
        self.__set_settings()

    def load_style(self, style_content):
        # LOGO布局
        self.logoEnableValue = style_content["LOGO"]["LogoEnable"]
        self.logoLayoutValue = LOGO_LAYOUT.LEFT if style_content[
            "LOGO"]["isLogoLeft"] else LOGO_LAYOUT.RIGHT
        self.logoSizeValue = int(style_content["LOGO"].get("SimpleLogoSize", 0.5) * 100)
        self.customLogoEnableValue = style_content["LOGO"]["CustomLogoEnable"]
        self.customLogoPathValue = style_content["LOGO"]["CustomLogoPath"]

    def save_style(self):
        # LOGO布局
        cfg.set(cfg.logoEnable, self.logoEnableValue)
        cfg.set(cfg.isLogoLeft, self.logoLayoutValue.isLeft())
        cfg.set(cfg.simpleLogoSize, self.logoSizeValue / 100)
        cfg.set(cfg.customLogoEnable, self.customLogoEnableValue)
        cfg.set(cfg.customLogoPath, self.customLogoPathValue)
