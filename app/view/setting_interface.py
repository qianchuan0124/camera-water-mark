import os
import subprocess
import sys
from pathlib import Path
import json

from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFileDialog
from qfluentwidgets import (
    ImageLabel,
    InfoBar,
    BodyLabel,
    CardWidget,
    PrimaryPushButton,
    InfoBarPosition,
    LineEdit,
    MessageBoxBase,
    PushSettingCard,
    ScrollArea,
    SettingCardGroup,
    FluentIcon as FIF
)

from app.config import cfg, STYLE_PATH
from app.components.common_card import ComboBoxSettingCard
from app.config import ASSETS_PATH, CACHE_PATH
from app.thread.image_handle_thread import ImageHandleTask, ImageHandleThread, HandleProgress, ImageHandleStatus
from app.components.common_item import LoadingButton
from app.entity.enums import MARK_MODE
from app.layout.standard_layout import StandardLayout
from app.layout.simple_layout import SimpleLayout
from app.layout.base_group import BaseGroup
from app.layout.global_group import GlobalGroup
from app.layout.logo_group import LogoGroup

DEFAULT_BG = {
    "path": Path(f"{ASSETS_PATH}/default_bg.jpg"),
    "width": 1280,
    "height": 720,
}

# 设置水印样式


class SettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('SettingInterface')
        self.setStyleSheet('SettingInterface {background-color: #f0f0f0;}')

        # 创建主布局
        self.hBoxLayout = QHBoxLayout(self)

        # 初始化界面组件
        self._initValues()
        self._initSettingsArea()
        self._initPreviewArea()
        self._initSettingCards()
        self._initLayout()
        self._initStyle()

        # 添加一个标志位来控制是否触发onSettingChanged
        self._loading_style = False

        # 设置初始值,加载样式
        self.__setValues()

        # 连接信号
        self.connectSignals()

    def _initValues(self):
        # 读取样式信息

        # 模式选择
        self.modeValue = MARK_MODE.key(cfg.markMode.value)

    def _initSettingsArea(self):
        """初始化左侧设置区域"""
        self.settingsScrollArea = ScrollArea()
        self.settingsScrollArea.setFixedWidth(350)
        self.settingsWidget = QWidget()
        self.settingsLayout = QVBoxLayout(self.settingsWidget)
        self.settingsScrollArea.setWidget(self.settingsWidget)
        self.settingsScrollArea.setWidgetResizable(True)

        # 创建设置组
        self.baseGroup = BaseGroup(self.settingsWidget)
        self.modeGroup = SettingCardGroup(self.tr("模式"), self.settingsWidget)
        self.globalGroup = GlobalGroup(self.settingsWidget)
        self.logoGroup = LogoGroup(self.settingsWidget)
        self.standardLayout = StandardLayout(self.settingsWidget)
        self.simpleLayout = SimpleLayout(self.settingsWidget)

    def _initPreviewArea(self):
        """初始化右侧预览区域"""
        self.previewScrollArea = ScrollArea()
        self.previewScrollArea.setWidgetResizable(True)
        self.previewScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.previewScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.previewCard = CardWidget()
        self.previewScrollArea.setWidget(self.previewCard)

        self.previewLayout = QVBoxLayout(self.previewCard)
        self.previewLayout.setSpacing(16)

        # 顶部预览区域
        self.previewTopWidget = QWidget()
        self.previewTopWidget.setFixedHeight(430)
        self.previewTopLayout = QVBoxLayout(self.previewTopWidget)

        self.previewLabel = BodyLabel(self.tr("预览效果"))
        self.previewImage = ImageLabel()
        self.previewImage.setAlignment(Qt.AlignCenter)
        self.previewTopLayout.addWidget(self.previewImage, 0, Qt.AlignCenter)
        self.previewTopLayout.setAlignment(Qt.AlignVCenter)

        # 底部控件区域
        self.previewBottomWidget = QWidget()
        self.previewBottomLayout = QVBoxLayout(self.previewBottomWidget)

        self.styleNameComboBox = ComboBoxSettingCard(
            FIF.VIEW, self.tr("选择样式"), self.tr("选择已保存的字幕样式"), texts=[]
        )

        self.newStyleButton = PushSettingCard(
            self.tr("新建样式"),
            FIF.ADD,
            self.tr("新建样式"),
            self.tr("基于当前样式新建预设"),
        )

        self.previewPath = PushSettingCard(
            self.tr("更新预览图"),
            FIF.ALBUM,
            self.tr("预览图路径"),
            cfg.get(cfg.previewPath),
        )

        self.openStyleFolderButton = PushSettingCard(
            self.tr("打开样式文件夹"),
            FIF.FOLDER,
            self.tr("打开样式文件夹"),
            self.tr("在文件管理器中打开样式文件夹"),
        )

        self.previewBottomLayout.addWidget(self.styleNameComboBox)
        self.previewBottomLayout.addWidget(self.newStyleButton)
        self.previewBottomLayout.addWidget(self.previewPath)
        self.previewBottomLayout.addWidget(self.openStyleFolderButton)

        self.previewSettingWidget = QWidget()
        self.previewSettingLayout = QHBoxLayout(self.previewSettingWidget)

        self.saveButton = PrimaryPushButton(self.tr("保存"), self, icon=FIF.SAVE)
        self.saveButton.clicked.connect(self.on_save_button_tapped)
        self.saveButton.setFixedHeight(34)

        self.resetButton = PrimaryPushButton(
            self.tr("重置"), self, icon=FIF.BRUSH)
        self.resetButton.clicked.connect(
            lambda: self.resetStyle()
        )
        self.resetButton.setFixedHeight(34)

        self.renderButton = LoadingButton(icon=FIF.CAMERA, text=self.tr("渲染"))
        self.renderButton.clicked.connect(
            lambda: self.renderStyle()
        )
        self.renderButton.setFixedHeight(34)

        self.previewSettingLayout.addWidget(self.saveButton)
        self.previewSettingLayout.addWidget(self.resetButton)
        self.previewSettingLayout.addWidget(self.renderButton)

        self.previewLayout.addWidget(self.previewTopWidget)
        self.previewLayout.addWidget(self.previewBottomWidget)
        self.previewLayout.addWidget(self.previewSettingWidget)
        self.previewLayout.addStretch(1)

    def _initSettingCards(self):
        """初始化所有设置卡片"""

        # 模式
        self.markMode = ComboBoxSettingCard(
            FIF.MORE,
            self.tr("布局模式"),
            self.tr("设置布局模式"),
            texts=MARK_MODE.all_values(),
        )

    def _initLayout(self):
        """初始化布局"""
        # 添加卡片到组

        # 模式
        self.modeGroup.addSettingCard(self.markMode)

        # 添加组到布局
        self.settingsLayout.addWidget(self.baseGroup)
        self.settingsLayout.addWidget(self.modeGroup)
        self.settingsLayout.addWidget(self.globalGroup)
        self.settingsLayout.addWidget(self.logoGroup)
        self.settingsLayout.addWidget(self.standardLayout)
        self.settingsLayout.addWidget(self.simpleLayout)
        self.settingsLayout.addStretch(1)

        # 添加左右两侧到主布局
        self.hBoxLayout.addWidget(self.settingsScrollArea)
        self.hBoxLayout.addWidget(self.previewScrollArea)

    def _initStyle(self):
        """初始化样式"""
        self.settingsWidget.setObjectName("settingsWidget")
        self.previewTopWidget.setObjectName("previewTopWidget")
        self.previewCard.setObjectName("previewCard")
        self.setStyleSheet(
            """
            #settingsWidget, #previewTopWidget, #previewCard {
                background-color: transparent;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        )

    def __setSettings(self):
        # 设置样式到UI上

        # 模式
        self.markMode.comboBox.setCurrentText(self.modeValue.value)

        self.__setInitHiddens()

    def __setInitHiddens(self):
        self.logoGroup.set_sub_hiddens(self.modeValue.isSimple())

        self.standardLayout.setHidden(self.modeValue.isSimple())

        self.simpleLayout.setHidden(not self.modeValue.isSimple())

    def __setValues(self):
        """设置初始值"""
        # 设置布局内容
        self.__setSettings()

        # 设置字幕样式
        self.styleNameComboBox.comboBox.setCurrentText(
            cfg.get(cfg.styleName))

        # 获取样式目录下的所有json文件名
        style_files = [f.stem for f in Path(f"{STYLE_PATH}").glob("*.json")]
        if "default" in style_files:
            style_files.insert(0, style_files.pop(
                style_files.index("default")))
        else:
            style_files.insert(0, "default")
            self.saveStyle("default")
        self.styleNameComboBox.comboBox.addItems(style_files)

        # 加载默认样式
        style_name = cfg.get(cfg.styleName)
        if style_name in style_files:
            self.loadStyle(style_name)
            self.styleNameComboBox.comboBox.setCurrentText(style_name)
        else:
            self.loadStyle(style_files[0])
            self.styleNameComboBox.comboBox.setCurrentText(style_files[0])

    def connectSignals(self):
        """连接所有设置变更的信号到预览更新函数"""
        # 监听UI上的改变，绑定到样式数据上
        self.previewPath.clicked.connect(self.__on_preview_path_clicked)

        # 模式
        self.markMode.currentTextChanged.connect(self.on_mark_mode_change)

        # 连接样式切换信号
        self.styleNameComboBox.currentTextChanged.connect(self.loadStyle)
        self.newStyleButton.clicked.connect(self.createNewStyle)
        self.openStyleFolderButton.clicked.connect(
            self.on_open_style_folder_clicked)

    def on_mark_mode_change(self):
        self.modeValue = MARK_MODE.get_enum(self.markMode.comboBox.text())
        self.__setInitHiddens()

    def on_save_button_tapped(self):
        self.saveStyle(cfg.styleName.value)
        InfoBar.success(
            title=self.tr("成功"),
            content=self.tr("保存成功 ") + cfg.styleName.value,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

    def on_open_style_folder_clicked(self):
        """打开样式文件夹"""
        if sys.platform == "win32":
            os.startfile(STYLE_PATH)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", STYLE_PATH])
        else:  # Linux
            subprocess.run(["xdg-open", STYLE_PATH])

    def __on_preview_path_clicked(self):
        current_path = Path(cfg.previewPath.value)
        if os.path.exists(current_path):
            desktop_path = os.path.dirname(current_path)
        else:
            desktop_path = QStandardPaths.writableLocation(
                QStandardPaths.DesktopLocation
            )

        # 创建文件对话框并设置过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption=self.tr("选择预览原图"),
            directory=desktop_path,
            filter=self.tr("图片 (*.jpg *.png *.jpeg);;所有文件 (*)")
        )

        # 如果用户选择了文件（未点击取消）
        if file_path:
            cfg.set(cfg.previewPath, file_path)
            self.previewPath.setContent(file_path)
            self.updatePreview()
            

    def updatePreview(self):
        # 创建预览线程
        self.renderButton.start_loading()
        cache_preview = Path(f"{CACHE_PATH}/preview.png")
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        preview_path = Path(cfg.previewPath.value)
        if not preview_path or not os.path.exists(preview_path):
            preview_path = Path(DEFAULT_BG["path"])
            cfg.set(cfg.previewPath, str(preview_path))
            self.previewPath.setContent(str(preview_path))

        self.preview_task = ImageHandleTask(
            preview_path, cache_preview)
        self.preview_thread = ImageHandleThread([self.preview_task])
        self.preview_thread.finished.connect(self.onPreviewReady)
        self.refreshButtons(False)
        self.preview_thread.start()

    def refreshButtons(self, isEnable):
        self.saveButton.setEnabled(isEnable)
        self.resetButton.setEnabled(isEnable)
        self.renderButton.setEnabled(isEnable)

    def onPreviewReady(self, progress: HandleProgress):
        """预览图片生成完成的回调"""
        task = progress.tasks[0]
        self.refreshButtons(True)
        if task and task.status == ImageHandleStatus.FINISHED:
            self.renderButton.stop_loading()
            self.previewImage.setImage(str(task.target_path))
            self.updatePreviewImage()
            InfoBar.success(
                self.tr("渲染成功"),
                self.tr("图片渲染成功"),
                duration=3000,
                parent=self,
            )
        else:
            info = task.errorInfo if len(
                task.errorInfo) > 0 else self.tr("位置错误")
            self.renderButton.stop_loading()
            InfoBar.error(
                self.tr("渲染错误"),
                info,
                duration=3000,
                parent=self,
            )

    def updatePreviewImage(self):
        """更新预览图片"""
        height = int(self.previewTopWidget.height() * 0.98)
        width = int(self.previewTopWidget.width() * 0.98)
        self.previewImage.scaledToWidth(width)
        if self.previewImage.height() > height:
            self.previewImage.scaledToHeight(height)
        self.previewImage.setBorderRadius(8, 8, 8, 8)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updatePreviewImage()

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.updatePreviewImage()

    def loadStyle(self, style_name):
        """加载指定样式"""
        style_path = Path(f"{STYLE_PATH}/{style_name}.json")

        if not style_path.exists():
            return

        # # 设置标志位，防止触发onSettingChanged
        self._loading_style = True

        with open(style_path, "r", encoding="utf-8") as f:
            style_content = json.load(f)

        # 解析样式内容
        self.baseGroup.load_style(style_content)

        # 模式
        self.modeValue = MARK_MODE.key(style_content["Mode"]["MarkMode"])

        self.globalGroup.load_style(style_content)

        self.logoGroup.load_style(style_content)

        self.standardLayout.load_style(style_content)

        self.simpleLayout.load_style(style_content)

        self.__setSettings()

        cfg.set(cfg.styleName, style_name)

        # 重置标志位
        self._loading_style = False

        # # 手动更新一次预览
        self.saveStyle(style_name)
        self.updatePreview()

        # # 显示加载成功提示
        InfoBar.success(
            title=self.tr("成功"),
            content=self.tr("已加载样式 ") + style_name,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self,
        )

    def createNewStyle(self):
        """创建新样式"""
        dialog = StyleNameDialog(self)
        if dialog.exec():
            style_name = dialog.nameLineEdit.text().strip()
            if not style_name:
                return

            # 检查是否已存在同名样式
            if Path(f"{STYLE_PATH}/{style_name}.json").exists():
                InfoBar.warning(
                    title=self.tr("警告"),
                    content=self.tr("样式 ") + style_name + self.tr(" 已存在"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self,
                )
                return

            # 保存新样式
            self.saveStyle(style_name)

            # 更新样式列表并选中新样式
            self.styleNameComboBox.addItem(style_name)
            self.styleNameComboBox.comboBox.setCurrentText(style_name)

            # 显示创建成功提示
            InfoBar.success(
                title=self.tr("成功"),
                content=self.tr("已创建新样式 ") + style_name,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self,
            )

    def saveStyle(self, style_name):
        """保存样式
        """
        # 确保样式目录存在
        Path(STYLE_PATH).mkdir(parents=True, exist_ok=True)

        self.baseGroup.save_style()

        # 模式
        cfg.set(cfg.markMode, self.modeValue.info())

        self.globalGroup.save_style()

        self.logoGroup.save_style()

        self.standardLayout.save_style()

        self.simpleLayout.save_style()

        # # 生成样式内容并保存
        config_dict = cfg.to_dict()
        style_path = Path(f"{STYLE_PATH}/{style_name}.json")

        with open(style_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4)

    def resetStyle(self):
        self._initValues()
        self.__setSettings()
        self.standardLayout.reset_style()
        self.simpleLayout.reset_style()
        self.logoGroup.reset_style()
        self.baseGroup.reset_style()
        self.globalGroup.reset_style()

    def renderStyle(self):
        if not self.renderButton.is_loading:
            self.renderButton.start_loading()
            self.updatePreview()


class StyleNameDialog(MessageBoxBase):
    """样式名称输入对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = BodyLabel(self.tr("新建样式"), self)
        self.nameLineEdit = LineEdit(self)

        self.nameLineEdit.setPlaceholderText(self.tr("输入样式名称"))
        self.nameLineEdit.setClearButtonEnabled(True)

        # 添加控件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameLineEdit)

        # 设置按钮文本
        self.yesButton.setText(self.tr("确定"))
        self.cancelButton.setText(self.tr("取消"))

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)
        self.nameLineEdit.textChanged.connect(self._validateInput)

    def _validateInput(self, text):
        self.yesButton.setEnabled(bool(text.strip()))
