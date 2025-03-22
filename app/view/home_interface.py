from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt
from qfluentwidgets import LineEdit, ToolButton
from qfluentwidgets import FluentIcon
from app.thread.image_handle_thread import ImageHandleThread, ImageHandleTask
from qfluentwidgets import ProgressBar, BodyLabel, InfoBar, InfoBarPosition
from pathlib import Path
from app.config import OUTPUT_PATH

# 打开文件夹，选中多张图片，形成表格

class TapButton(ToolButton):
    def __init__(self, parent=None):
        super(TapButton, self).__init__(parent)
        self.setFixedSize(40, 40)
        self.setStyleSheet(
            self.styleSheet()
            + """
            QToolButton {
                border-radius: 20px;
                background-color: #2F8D63;
            }
            QToolButton:hover {
                background-color: #2E805C;
            }
            QToolButton:pressed {
                background-color: #2E905C;
            }
        """
        )

class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HomeInterface')
        self.setStyleSheet('HomeInterface {background-color: #f0f0f0;}')

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setup_ui()
        self.setup_signals()


    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setSpacing(36)

        self.start_button = TapButton(self)
        self.start_button.setIcon(FluentIcon.PLAY)

        self.main_layout.addWidget(self.start_button)

        self.main_layout.addStretch(1)

    def setup_signals(self):
        self.start_button.clicked.connect(self.on_start_button_clicked)

    def on_start_button_clicked(self):
        image_path = Path("E:/Workspace/camera-water/semi-utils/input/DSC_0060.jpg")
        target_path = Path(OUTPUT_PATH) / "DSC_0060.jpg"
        self.task = ImageHandleTask(image_path, target_path)
        self.image_handle_thread = ImageHandleThread(self.task)
        self.image_handle_thread.finished.connect(self.on_image_handle_finished)
        self.image_handle_thread.error.connect(self.on_image_handle_error)
        self.image_handle_thread.start()

    def on_image_handle_finished(self):
        InfoBar.success(
            self.tr("成功"),
            self.tr("照片处理已完成"),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def on_image_handle_error(self, error):
        InfoBar.error(
            self.tr("错误"),
            str(error),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self,
        )