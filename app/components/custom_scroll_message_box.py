from qfluentwidgets import MessageBoxBase, TextEdit, setTheme, Theme

class CustomScrollableMessageBox(MessageBoxBase):
    """ Custom message box with scrollable SubtitleLabel """

    def __init__(self, parent=None, title="输入长文本"):
        setTheme(Theme.DARK)
        super().__init__(parent)
        
        # 设置窗口标题
        self.setWindowTitle("自定义消息框")
        
        self.textInfo = TextEdit(self)
        self.textInfo.setReadOnly(True)
        self.textInfo.setPlainText(title)

        self.textInfo.verticalScrollBar().valueChanged.connect(self.on_scroll_changed)
        
        # 创建一个布局来容纳所有内容
        self.viewLayout.addWidget(self.textInfo)


        # 设置对话框的最小宽度和高度
        self.widget.setMinimumWidth(500)
        self.widget.setMinimumHeight(600)

    def on_scroll_changed(self, value):
        """监听滚动条变化"""
        scrollbar = self.textInfo.verticalScrollBar()
        max_value = scrollbar.maximum()
        self.auto_scroll = value <= max_value and value >= max_value * 0.85
