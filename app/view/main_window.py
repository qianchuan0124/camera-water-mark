import sys
from pathlib import Path
from qfluentwidgets import (FluentWindow)
from qfluentwidgets import setTheme, Theme, NavigationItemPosition, MessageBox
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from app.config import ASSETS_PATH, ROOT_PATH

LOGO_PATH = f"{ASSETS_PATH}/logo.png"


class MainWindow(FluentWindow):
    def __init__(self):
        setTheme(Theme.DARK)

        super().__init__()

        self.initWindow()

        self.check_permissions(ROOT_PATH)

        from app.view.home_interface import HomeInterface
        from app.view.setting_interface import SettingInterface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)

        self.initNavigation()

    def check_permissions(self, path: str):
    # 检查是否有读写权限
        try:
            test_path = Path(path) / "test_permission"
            test_path.mkdir(parents=True, exist_ok=True)
            test_path.rmdir()  # 删除测试文件夹
        except PermissionError:
            w = MessageBox(
                QCoreApplication.translate("MainWindow", "没有读写权限"), 
                QCoreApplication.translate("MainWindow", "请检查文件夹权限或以管理员身份运行程序。"), 
                self.window()
            )
            w.yesButton.setText(QCoreApplication.translate("MainWindow", "确认"))
            w.cancelButton.setHidden(True)
            if w.exec():
                sys.exit()
        

    def initWindow(self):
        self.resize(1050, 600)
        self.setMinimumWidth(700)
        self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.setWindowTitle("水印助手")

        # 设置窗口位置, 居中
        desktop = QApplication.desktop().availableGeometry()  # type: ignore
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.show()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')

        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.tr("设置"),
            NavigationItemPosition.BOTTOM,
        )

        from app.utils.logger import setup_logger
        logger = setup_logger("main")
        logger.info(f"root path: {ROOT_PATH}")

        self.switchTo(self.homeInterface)
