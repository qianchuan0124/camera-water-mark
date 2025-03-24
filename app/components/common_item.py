from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy
from qfluentwidgets import LineEdit, ToolButton, FluentIcon, FluentIconBase, Theme, isDarkTheme
from PyQt5.QtWidgets import QToolTip, QPushButton, QLabel
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import Qt
from app.config import ASSETS_PATH
from pathlib import Path

LOADING_GIF = f"{ASSETS_PATH}/loading.gif"


class LoadingButton(QPushButton):
    def __init__(self, icon: QIcon | FluentIcon, text: str, parent=None):
        super().__init__(parent)
        self.loading_path = str(Path(LOADING_GIF))
        if isinstance(icon, FluentIconBase) and self.isEnabled():
            theme = Theme.DARK if not isDarkTheme() else Theme.LIGHT
            self.custom_icon = QLabel()
            self.custom_icon.setPixmap(icon.icon(theme).pixmap(16, 16))
        self.text = text
        self.is_loading = False

        self.setup_ui()

    def setup_ui(self):
        self.setLayout(QHBoxLayout())
        layout = self.layout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        layout.addStretch()

        if hasattr(self, 'custom_icon'):
            self.custom_icon.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.custom_icon)

        self.text_label = QLabel(self.text)
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)
        self.text_label.setStyleSheet("""
            QLabel {
                color: black;                   /* 字体颜色 */
                font-weight: bold;              /* 字体粗细（bold/normal） */
                font-size: 14px;               /* 字体大小（可选） */
                padding: 0 4px;                /* 内边距（可选） */
            }
        """)

        self.gif_label = QLabel()
        self.gif_label.setFixedSize(16, 16)
        self.movie = QMovie(self.loading_path)
        if self.movie.isValid():
            self.gif_label.setMovie(self.movie)
            self.movie.setScaledSize(QSize(16, 16))
        self.gif_label.hide()
        layout.addWidget(self.gif_label)

        layout.addStretch()

        self.setStyleSheet("""
            QPushButton {
                background-color: #58f4ff;  /* 背景色 */
                color: black;              /* 文字颜色 */
                border-radius: 6px;       /* 圆角半径 */
                padding: 5px 15px;
                min-width: 80px;
                max-width: 160px;
            }
            QPushButton:hover {
                background-color: #25d9e6; /* 悬停颜色 */
            }
            QPushButton:pressed {
                background-color: #25c6d1; /* 按下颜色 */
            }
        """)

    def isLoading(self) -> bool:
        return self.is_loading

    def start_loading(self):
        if self.movie.isValid():
            self.setEnabled(False)
            self.is_loading = True
            self.gif_label.show()
            self.movie.start()

    def stop_loading(self):
        self.setEnabled(True)
        self.is_loading = False
        self.gif_label.hide()
        self.movie.stop()


class TapButton(ToolButton):
    def __init__(self, parent=None, tips=None):
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
        if tips:
            self.setToolTip(tips)

    def enterEvent(self, event):
        """鼠标进入按钮时显示提示"""
        QToolTip.showText(self.mapToGlobal(
            self.rect().bottomLeft()), self.toolTip())
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开按钮时隐藏提示"""
        QToolTip.hideText()
        super().leaveEvent(event)


class SearchInput(LineEdit):
    def __init__(self, parent=None):
        super(SearchInput, self).__init__(parent)
        self.setPlaceholderText(self.tr("请拖拽文件或输入URL"))
        self.setFixedHeight(40)
        self.setClearButtonEnabled(True)
        self.focusOutEvent = lambda e: super(
            LineEdit, self
        ).focusOutEvent(e)
        self.paintEvent = lambda e: super(
            LineEdit, self
        ).paintEvent(e)
        self.setStyleSheet(
            self.styleSheet()
            + """
            QLineEdit {
                border-radius: 18px;
                padding: 0 20px;
                background-color: transparent;
                border: 1px solid rgba(255,255, 255, 0.08);
            }
            QLineEdit:focus[transparent=true] {
                border: 1px solid rgba(47,141, 99, 0.48);
            }
            
        """
        )
