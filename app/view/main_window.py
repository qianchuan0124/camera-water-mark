from qfluentwidgets import (FluentWindow)
from qfluentwidgets import setTheme, Theme, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from app.view.home_interface import HomeInterface
from app.view.setting_interface import SettingInterface
from app.config import ASSETS_PATH, ROOT_PATH
from app.utils.logger import setup_logger
logger = setup_logger("main")

LOGO_PATH = f"{ASSETS_PATH}/logo.png"


class MainWindow(FluentWindow):
    def __init__(self):
        setTheme(Theme.DARK)

        super().__init__()
        self.initWindow()

        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)

        self.initNavigation()

    def initWindow(self):
        self.resize(1050, 600)
        self.setMinimumWidth(700)
        self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.setWindowTitle("水印助手")

        # 设置窗口位置, 居中
        desktop = QApplication.desktop().availableGeometry()  # type: ignore
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        logger.info(f"root path: {ROOT_PATH}")
        self.show()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')

        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.tr("设置"),
            NavigationItemPosition.BOTTOM,
        )

        self.switchTo(self.homeInterface)
