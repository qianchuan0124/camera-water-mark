import os
from pathlib import Path
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QStandardPaths, pyqtSignal
from qfluentwidgets import (
    ExpandGroupSettingCard,
    PushButton,
    SwitchButton,
    BodyLabel,
    FluentIcon,
    IndicatorPosition
)


class CustomLogoPathCard(ExpandGroupSettingCard):

    checkedChanged = pyqtSignal(bool)
    pathChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(
            icon=FluentIcon.TAG,
            title="自定义LOGO",
            content="建议宽高比例 1:1",
            parent=parent
        )
        self.origin_path = ""

        # 第一组
        self.switch_label = BodyLabel(self.tr("启用"))
        self.switch_content = BodyLabel(self.tr("是否使用自定义LOGO"))
        self.switch_button = SwitchButton(
            self.tr("否"), self, IndicatorPosition.RIGHT)
        self.switch_button.setOnText(self.tr("是"))

        # 第二组
        self.path_button = PushButton(self.tr("选择路径"))
        self.path_content = BodyLabel(self.tr("选择LOGO图片路径"))
        self.path_label = BodyLabel(self.tr("路径"))

        # 调整内部布局
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # 添加各组到设置卡中
        self.add(self.switch_label, self.switch_content, self.switch_button)
        self.add(self.path_label, self.path_content, self.path_button)

        self.setup_signals()

    def add(self, title, content, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 12, 12)

        left_layout = QVBoxLayout()
        left_layout.addWidget(title, 0, Qt.AlignLeft)
        left_layout.addWidget(content, 0, Qt.AlignLeft)
        content.setObjectName('contentLabel')

        layout.addLayout(left_layout)
        layout.addStretch(1)
        layout.addWidget(widget)

        # 添加组件到设置卡
        self.addGroupWidget(w)

    def setup_signals(self):
        """设置信号"""
        self.switch_button.checkedChanged.connect(self._on_switch_clicked)
        self.path_button.clicked.connect(self._on_path_clicked)

    def _on_switch_clicked(self, checked: bool):
        """开关按钮点击事件"""
        self.setChecked(checked)
        self.checkedChanged.emit(checked)

    def _on_path_clicked(self):
        # 获取桌面路径作为初始目录
        current_path = Path(self.origin_path)
        if os.path.exists(current_path):
            desktop_path = os.path.dirname(current_path)
        else:
            desktop_path = QStandardPaths.writableLocation(
                QStandardPaths.DesktopLocation
            )

        # 创建文件对话框并设置过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption=self.tr("选择LOGO图片"),
            directory=desktop_path,
            filter=self.tr("PNG图片 (*.png);;所有文件 (*)")
        )

        # 如果用户选择了文件（未点击取消）
        if file_path:
            self.setPath(file_path)
            self.pathChanged.emit(file_path)

    def setChecked(self, checked: bool):
        """设置开关状态"""
        self.switch_button.setChecked(checked)
        self.switch_button.setText(self.tr("是") if checked else self.tr("否"))

    def setPath(self, path: str):
        """设置路径"""
        if not path:
            self.path_content.setText(self.tr("选择LOGO图片路径"))
            return
        self.origin_path = path
        if len(path) > 25:
            path = f"{path[:10]}...{path[-15:]}"
        self.path_content.setText(path)
