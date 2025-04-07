from qfluentwidgets import MessageBoxBase, TableWidget, setTheme, Theme, InfoBar, TransparentToolButton, FluentIcon, MessageBox
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QApplication, QFileDialog, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path
from app.utils.image_handle import get_exif, update_custom_tags
from app.entity.enums import ExifId
from typing import List
import os
import shutil
from dataclasses import dataclass
from app.entity.custom_error import CustomError


@dataclass
class ExifItem:
    name: str
    desc: str
    value: str
    tip: str


class ExifEditMessageBox(MessageBoxBase):
    path_changed = pyqtSignal((int, Path))

    def __init__(self, parent=None, path: Path = None, index: int = None):
        setTheme(Theme.DARK)
        super().__init__(parent)
        self.setWindowTitle(self.tr("元信息编辑"))
        self.path = path  # 保存传入的文件路径
        self.exif = get_exif(path)
        self.index = index
        self.exif_data: List[ExifItem] = []
        # 初始化UI
        self._init_ui()

        # 重写按钮行为
        self.yesButton.setText(self.tr("更新"))
        self.cancelButton.setText(self.tr("取消"))
        self.cancelButton.clicked.connect(self.close)
        self.yesButton.clicked.disconnect()  # 断开所有之前的连接
        self.yesButton.clicked.connect(self.__onYesButtonClicked)

    def _init_ui(self):
        """初始化界面组件"""
        self.table = TableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            [self.tr("属性"), self.tr("值"), self.tr("备注")])

        # 表格样式设置
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(
            TableWidget.DoubleClicked | TableWidget.EditKeyPressed)

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 60)

        # 添加数据
        self._init_table_data()
        self.viewLayout.addWidget(self.table)
        self.widget.setMinimumWidth(500)
        self.widget.setMinimumHeight(600)

    def _init_table_data(self):
        """初始化表格数据"""

        allExifs: List[ExifId] = ExifId.display_values()

        for exif in allExifs:
            if exif.value in self.exif:
                info: str = self.exif[exif.value]
            else:
                info: str = ""
            item = ExifItem(exif.update_value(), exif.ex_description(),
                            info, exif.default_value())
            self.exif_data.append(item)

        self.table.setRowCount(len(self.exif_data))
        for row, data in enumerate(self.exif_data):
            # 左侧标签列
            label_item = QTableWidgetItem(data.desc)
            label_item.setFlags(label_item.flags() & ~Qt.ItemIsEditable)
            label_item.setToolTip(data.desc)
            self.table.setItem(row, 0, label_item)

            # 右侧值列（带 placeholder 效果）
            value_item = QTableWidgetItem(data.value)
            if not data.value.strip():  # 如果值为空，设置 placeholder
                value_item.setData(Qt.DisplayRole, "")
                value_item.setData(Qt.UserRole, data.value)  # 保存原始值
            self.table.setItem(row, 1, value_item)

            reamrk_item_container = QWidget()
            reamrk_layout = QHBoxLayout(reamrk_item_container)
            reamrk_layout.setContentsMargins(0, 0, 0, 0)

            remark_button = TransparentToolButton(FluentIcon.INFO)
            remark_button.clicked.connect(
                lambda checked, r=row: self._remark_model(r))
            reamrk_layout.addStretch()
            reamrk_layout.addWidget(remark_button)
            reamrk_layout.addStretch()
            self.table.setCellWidget(row, 2, reamrk_item_container)

        # 连接信号，当编辑时恢复默认样式
        self.table.cellChanged.connect(self._on_cell_changed)

    def _remark_model(self, row):
        """显示备注信息"""
        item = self.exif_data[row]
        if item:
            w = MessageBox(self.tr("提示信息"), item.tip, self.window())
            w.cancelButton.hide()
            w.yesButton.setText(self.tr("我知道了"))
            w.exec()

    def _on_cell_changed(self, row, col):
        """当单元格内容变化时处理 placeholder 样式"""
        if col == 1:  # 只处理值列
            item = self.table.item(row, col)
            self.exif_data[row].value = item.data(Qt.DisplayRole)

    def __onYesButtonClicked(self):
        """点击确定按钮时的处理"""
        # 1. 获取所有修改后的数据
        modified_data = {}
        for data in self.exif_data:
            modified_data[data.name] = data.value

        file_name = os.path.basename(self.path)
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("选择保存位置"),
            file_name,
            self.tr("图片文件 (*.jpg *.jpeg *.png)")
        )

        if new_path:
            if self.path != new_path:
                # 复制原文件到新位置
                shutil.copy2(self.path, new_path)
                self.path = new_path
                self.path_changed.emit(self.index, Path(new_path))
            # 保存EXIF到新文件
            try:
                update_custom_tags(self.path, modified_data)
                InfoBar.success(
                    self.tr("成功"),
                    self.tr("更新元信息成功"),
                    duration=3000,
                    parent=self,
                )
            except CustomError as e:
                InfoBar.error(
                    self.tr("更新失败"),
                    self.tr("更新元信息失败"),
                    duration=3000,
                    parent=self,
                )


# 使用示例
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    box = ExifEditMessageBox(path=Path("test.jpg"))
    if box.exec_():
        print("用户点击了确定")
    else:
        print("用户点击了取消")
