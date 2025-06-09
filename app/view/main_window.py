import sys
import webbrowser
from pathlib import Path
from qfluentwidgets import (FluentWindow)
from qfluentwidgets import setTheme, Theme, NavigationItemPosition, MessageBox
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from app.config import ASSETS_PATH, ROOT_PATH
from app.entity.constants import NO_PERMISSION_URL

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
            w.yesButton.setText(QCoreApplication.translate("MainWindow", "尝试修复"))
            w.cancelButton.setText(QCoreApplication.translate("MainWindow", "退出"))
            if w.exec():
                webbrowser.open(NO_PERMISSION_URL)
                sys.exit()
            else:
                sys.exit()
        

    def initWindow(self):
        # 获取精确的屏幕尺寸和窗口尺寸
        desktop = QApplication.desktop().availableGeometry()
        screen_center = desktop.center()

        self.resize(max(min(1050, desktop.width() - 400), 800), max(min(850, desktop.height() - 100), 600))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.setWindowTitle("水印助手")
        
        window_size = self.size()
        
        # 精确计算左上角坐标（中心点对齐）
        x = screen_center.x() - window_size.width() // 2
        y = screen_center.y() - window_size.height() // 2
        self.move(x, y)

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
