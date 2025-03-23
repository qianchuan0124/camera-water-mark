from qfluentwidgets import LineEdit, ToolButton
from PyQt5.QtWidgets import QToolTip


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
