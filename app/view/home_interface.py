import os
import platform
import subprocess
from typing import List
from pathlib import Path
from PyQt5.QtCore import Qt, QStandardPaths
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QTableWidgetItem, QWidget, QHBoxLayout, QFileDialog
from qfluentwidgets import TableWidget, TableItemDelegate, HyperlinkButton
from qfluentwidgets import FluentIcon
from app.thread.image_handle_thread import ImageHandleThread, ImageHandleTask, ImageHandleStatus, HandleProgress
from qfluentwidgets import ProgressBar, BodyLabel, InfoBar, InfoBarPosition
from app.config import OUTPUT_PATH, SupportedImageFormats
from app.models.picutre_model import PictureItem
from app.components.common_item import TapButton, SearchInput
from app.view.log_window import LogWindow
from app.utils.logger import setup_logger
logger = setup_logger("home")

# 打开文件夹，选中多张图片，形成表格


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('HomeInterface')
        self.setStyleSheet('HomeInterface {background-color: #f0f0f0;}')
        self.setAcceptDrops(True)
        self.log_window = None
        self.target_path = OUTPUT_PATH

        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setSpacing(36)

        self.setup_header_view()

        self.picture_table = self._create_picture_table()
        self.picture_models: List[PictureItem] = []
        self.main_layout.addWidget(self.picture_table)

        self.setup_status_layout()
        self.setup_info_label()

        self.main_layout.addStretch(1)

    def setup_header_view(self):
        self.header_layout = QHBoxLayout()
        self.header_layout.setObjectName("header_layout")
        self.header_layout.setSpacing(12)
        self.header_layout.setContentsMargins(16, 16, 16, 0)

        title_label = BodyLabel(self.tr("目标路径:"))
        self.header_layout.addWidget(title_label)

        self.search_input = SearchInput(self)
        self.search_input.setText(str(OUTPUT_PATH))
        self.header_layout.addWidget(self.search_input)

        self.target_button = TapButton(self, self.tr("更新目标路径"))
        self.target_button.setIcon(FIF.FOLDER)
        self.header_layout.addWidget(self.target_button)

        self.add_button = TapButton(self, self.tr("添加图片"))
        self.add_button.setIcon(FIF.ADD)
        self.header_layout.addWidget(self.add_button)

        self.clean_button = TapButton(self, self.tr("清空图片"))
        self.clean_button.setIcon(FIF.DELETE)
        self.header_layout.addWidget(self.clean_button)

        self.start_button = TapButton(self, self.tr("开始处理"))
        self.start_button.setIcon(FluentIcon.PLAY)
        self.header_layout.addWidget(self.start_button)

        self.main_layout.addLayout(self.header_layout)

    def setup_status_layout(self):
        bottom_layout = QHBoxLayout()
        self.progress_bar = ProgressBar(self)
        self.status_label = BodyLabel(self.tr("就绪"), self)
        self.status_label.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        bottom_layout.setContentsMargins(80, 0, 80, 0)
        bottom_layout.addWidget(self.progress_bar, 1)  # 进度条使用剩余空间
        bottom_layout.addWidget(self.status_label)  # 状态标签使用固定宽度

        self.main_layout.addStretch(1)
        self.main_layout.addLayout(bottom_layout)

    def setup_info_label(self):
        # 创建底部容器
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # 创建日志按钮
        self.log_button = HyperlinkButton(
            url="", text=self.tr("查看日志"), parent=self)
        self.log_button.setStyleSheet(
            self.log_button.styleSheet()
            + """
            QPushButton {
                font-size: 12px;
                color: #2F8D63;
                text-decoration: underline;
            }
        """
        )

        # 将组件添加到底部布局
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.log_button)
        bottom_layout.addStretch()

        self.main_layout.addStretch()
        self.main_layout.addWidget(bottom_container)

    def setup_signals(self):
        self.target_button.clicked.connect(self.on_target_button_clicked)
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.clean_button.clicked.connect(self.on_clean_button_clicked)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.log_button.clicked.connect(self.show_log_window)
        self.search_input.textChanged.connect(self.on_search_input_changed)

    def on_search_input_changed(self):
        self.target_path = self.search_input.text()

    def show_log_window(self):
        """显示日志窗口"""
        if self.log_window is None:
            self.log_window = LogWindow()
        if self.log_window.isHidden():
            self.log_window.show()
        else:
            self.log_window.activateWindow()

    def on_target_button_clicked(self):
        desktop_path = QStandardPaths.writableLocation(
            QStandardPaths.DesktopLocation
        )

        # 使用 getExistingDirectory 选择文件夹
        folder_path = QFileDialog.getExistingDirectory(
            self, self.tr("选择文件夹"), desktop_path
        )

        if folder_path:
            self.search_input.setText(folder_path)

    def on_add_button_clicked(self):
        desktop_path = QStandardPaths.writableLocation(
            QStandardPaths.DesktopLocation
        )
        file_dialog = QFileDialog()

        # 构建文件过滤器
        picture_formats = " ".join(
            f"*.{fmt.value}" for fmt in SupportedImageFormats)
        filter_str = f"{self.tr('图片文件')} ({picture_formats})"

        # 使用 getOpenFileNames 选择多个文件
        file_paths, _ = file_dialog.getOpenFileNames(
            self, self.tr("选择媒体文件"), desktop_path, filter_str
        )

        # 处理选中的文件路径
        if file_paths:
            has_added = False
            for file_path in file_paths:
                is_exist = any(
                    model.original_path == file_path for model in self.picture_models)
                if is_exist:
                    continue
                else:
                    has_added = True
                    self.picture_models.append(PictureItem(
                        name=os.path.basename(file_path),
                        original_path=file_path,
                        target_path=OUTPUT_PATH,
                        status=ImageHandleStatus.WAITING
                    ))
            if has_added:
                self._populate_model_table()
                InfoBar.success(
                    self.tr("导入成功"),
                    self.tr("导入图片文件成功"),
                    duration=1500,
                    parent=self,
                )

    def on_clean_button_clicked(self):
        self.picture_models.clear()
        self._populate_model_table()

    def on_start_button_clicked(self):
        if not os.path.exists(self.target_path):
            InfoBar.error(
                self.tr("处理错误"),
                self.tr("目标路径不存在"),
                duration=3000,
                parent=self,
            )
            return
        tasks: List[ImageHandleTask] = []
        for model in self.picture_models:
            target_path = Path(f"{self.target_path}/{model.name}")
            task = ImageHandleTask(model.original_path, target_path)
            tasks.append(task)
        self.image_handle_thread = ImageHandleThread(tasks)
        self.image_handle_thread.finished.connect(
            self.on_image_handle_finished)
        self.image_handle_thread.loading.connect(self.on_image_handle_loading)
        self.image_handle_thread.error.connect(self.on_image_handle_error)
        self.image_handle_thread.start()

    def _create_picture_table(self):
        """创建图片表格"""
        table = TableWidget(self)
        table.setEditTriggers(TableWidget.NoEditTriggers)
        table.setSelectionMode(TableWidget.NoSelection)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [self.tr("名称"), self.tr("位置"), self.tr("操作"), self.tr("状态")]
        )

        # 设置表格样式
        table.setBorderVisible(True)
        table.setBorderRadius(8)
        table.setItemDelegate(TableItemDelegate(table))

        # 设置列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        table.setColumnWidth(1, 120)
        table.setColumnWidth(2, 120)
        table.setColumnWidth(3, 120)

        # 设置行高
        row_height = 45
        table.verticalHeader().setDefaultSectionSize(row_height)

        # 设置表格高度
        header_height = 20
        max_visible_rows = 12
        table_height = row_height * max_visible_rows + header_height + 15
        table.setFixedHeight(table_height)

        return table

    def _populate_model_table(self):
        """填充照片表格数据"""
        self.picture_table.setRowCount(len(self.picture_models))
        for i, model in enumerate(self.picture_models):
            self._add_model_row(i, model)

    def _add_model_row(self, row, model: PictureItem):
        """添加照片表格行"""
        # 名称
        name_item = QTableWidgetItem(model.name)
        name_item.setTextAlignment(Qt.AlignCenter)
        self.picture_table.setItem(row, 0, name_item)

        # 原始路径
        original_path_container = QWidget()
        original_path_layout = QHBoxLayout(original_path_container)
        original_path_layout.setContentsMargins(4, 4, 4, 4)

        original_path_btn = HyperlinkButton(
            "",
            self.tr("当前路径"),
            parent=self,
        )
        original_path_btn.setIcon(FIF.FOLDER)
        original_path_btn.clicked.connect(
            lambda checked, p=model.original_path: self._open_origin_path(p))
        original_path_layout.addStretch()
        original_path_layout.addWidget(original_path_btn)
        original_path_layout.addStretch()
        self.picture_table.setCellWidget(row, 1, original_path_container)

        # 删除
        delete_container = QWidget()
        delete_layout = QHBoxLayout(delete_container)
        delete_layout.setContentsMargins(4, 4, 4, 4)

        delete_btn = HyperlinkButton(
            "",
            self.tr("删除"),
            parent=self,
        )
        delete_btn.setIcon(FIF.DELETE)
        delete_btn.clicked.connect(
            lambda checked, r=row: self._delete_model(r))
        delete_layout.addStretch()
        delete_layout.addWidget(delete_btn)
        delete_layout.addStretch()
        self.picture_table.setCellWidget(row, 2, delete_container)

        # 状态
        status_item = QTableWidgetItem(
            self.tr(f"{model.status.value}"))
        if model.status == ImageHandleStatus.FINISHED:
            status_item.setForeground(Qt.green)
        status_item.setTextAlignment(Qt.AlignCenter)
        self.picture_table.setItem(row, 3, status_item)

    def _open_origin_path(self, path):
        """打开原始路径对应的文件夹"""
        self.open_folder(os.path.dirname(path))

    def open_folder(self, folder_path):
        system_platform = platform.system()
        try:
            if system_platform == "Windows":
                subprocess.run(["explorer", folder_path], check=True)
            elif system_platform == "Darwin":  # macOS
                subprocess.run(["open", folder_path], check=True)
            elif system_platform == "Linux":
                subprocess.run(["xdg-open", folder_path], check=True)
            else:
                logger.error(f"不支持的操作系统: {system_platform}")
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")

    def _delete_model(self, row):
        """删除模型"""
        self.picture_models.pop(row)
        self._populate_model_table()

    def dragEnterEvent(self, event):
        event.accept() if event.mimeData().hasUrls() else event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file_path in files:
            if not os.path.isfile(file_path):
                continue

            file_ext = os.path.splitext(file_path)[1][1:].lower()

            # 检查文件格式是否支持
            supported_formats = {fmt.value for fmt in SupportedImageFormats}

            is_supported = file_ext in supported_formats
            has_failed = False

            if is_supported:
                is_exist = any(
                    model.original_path == file_path for model in self.picture_models)
                if is_exist:
                    continue
                else:
                    self.picture_models.append(PictureItem(
                        name=os.path.basename(file_path),
                        original_path=file_path,
                        target_path=OUTPUT_PATH,
                        status=ImageHandleStatus.WAITING
                    ))
                    self._populate_model_table()
            else:
                has_failed = True
                InfoBar.error(
                    self.tr(f"格式错误") + file_ext,
                    self.tr("不支持该文件格式"),
                    duration=3000,
                    parent=self,
                )

        if not has_failed:
            InfoBar.success(
                self.tr("导入成功"),
                self.tr("导入图片文件成功"),
                duration=1500,
                parent=self,
            )

    def on_image_handle_finished(self, progress: HandleProgress):
        for task in progress.tasks:
            for model in self.picture_models:
                if model.original_path == task.image_path:
                    model.status = task.status
                    break
        self.progress_bar.setValue(progress.progress)
        self.status_label.setText("处理完成")
        self._populate_model_table()
        self.open_folder(self.target_path)
        InfoBar.success(
            self.tr("成功"),
            self.tr("照片处理已完成"),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def on_image_handle_loading(self, progress: HandleProgress):
        # 将task的状态赋值到model上去
        for task in progress.tasks:
            for model in self.picture_models:
                if model.original_path == task.image_path:
                    model.status = task.status
                    break
        self.progress_bar.setValue(progress.progress)
        self.status_label.setText("处理中")
        self._populate_model_table()

    def on_image_handle_error(self, error):
        InfoBar.error(
            self.tr("错误"),
            str(error),
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self,
        )
