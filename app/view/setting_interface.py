import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFontDatabase
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    ImageLabel,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    MessageBoxBase,
    PushSettingCard,
    ScrollArea,
    SettingCardGroup,
)

from app.config import cfg, SUBTITLE_STYLE_PATH
from app.components.common_card import (
    ComboBoxSettingCard,
    DoubleSpinBoxSettingCard,
    SpinBoxSettingCard,
    ColorSettingCard,
    SwitchSettingCard
)
from app.config import ASSETS_PATH, CACHE_PATH
from app.utils.mater_mark_preview import generate_preview
from app.entity.constants import DISPLAY_TYPE, display_type_key, display_type_value
from app.thread.image_handle_thread import ImageHandleTask, ImageHandleThread

DEFAULT_BG = {
    "path": ASSETS_PATH / "default_bg.jpg",
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

    def _initSettingsArea(self):
        """初始化左侧设置区域"""
        self.settingsScrollArea = ScrollArea()
        self.settingsScrollArea.setFixedWidth(350)
        self.settingsWidget = QWidget()
        self.settingsLayout = QVBoxLayout(self.settingsWidget)
        self.settingsScrollArea.setWidget(self.settingsWidget)
        self.settingsScrollArea.setWidgetResizable(True)

        # 创建设置组
        self.baseGroup = SettingCardGroup(self.tr("基础"), self.settingsWidget)
        self.globalGroup = SettingCardGroup(self.tr("全局"), self.settingsWidget)
        self.layoutGroup = SettingCardGroup(self.tr("布局"), self.settingsWidget)

    def _initPreviewArea(self):
        """初始化右侧预览区域"""
        self.previewCard = CardWidget()
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

        self.openStyleFolderButton = PushSettingCard(
            self.tr("打开样式文件夹"),
            FIF.FOLDER,
            self.tr("打开样式文件夹"),
            self.tr("在文件管理器中打开样式文件夹"),
        )

        self.previewBottomLayout.addWidget(self.styleNameComboBox)
        self.previewBottomLayout.addWidget(self.newStyleButton)
        self.previewBottomLayout.addWidget(self.openStyleFolderButton)

        self.previewLayout.addWidget(self.previewTopWidget)
        self.previewLayout.addWidget(self.previewBottomWidget)
        self.previewLayout.addStretch(1)

    def _initSettingCards(self):
        """初始化所有设置卡片"""
        # 左上角类型
        self.leftTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左上角类型"),
            self.tr("设置左上角展示信息的类型"),
            texts=DISPLAY_TYPE.keys(),
        )

        # 左上角字体颜色
        self.leftTopColor = ColorSettingCard(
            QColor(33, 33, 33),
            FIF.PALETTE,
            self.tr("左上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 左上角字体粗细
        self.leftTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            cfg.leftTopBold,
            self.layoutGroup
        )

        # 左下角类型
        self.leftBottomType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左下角类型"),
            self.tr("设置左下角展示信息的类型"),
            texts=DISPLAY_TYPE.keys(),
        )

        # 左下角字体颜色
        self.leftBottomColor = ColorSettingCard(
            QColor(117, 117, 117),
            FIF.PALETTE,
            self.tr("左下角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 左下角字体粗细
        self.leftBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左下角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            cfg.leftBottomBold,
            self.layoutGroup
        )

        # 右上角类型
        self.rightTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("右上角类型"),
            self.tr("设置左上角展示信息的类型"),
            texts=DISPLAY_TYPE.keys(),
        )

        # 右上角字体颜色
        self.rightTopColor = ColorSettingCard(
            QColor(33, 33, 33),
            FIF.PALETTE,
            self.tr("右上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 右上角字体粗细
        self.rightTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            cfg.rightTopBold,
            self.layoutGroup
        )

        # 右下角类型
        self.rightBottomType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左下角类型"),
            self.tr("设置左下角展示信息的类型"),
            texts=DISPLAY_TYPE.keys(),
        )

        # 右下角字体颜色
        self.rightBottomColor = ColorSettingCard(
            QColor(117, 117, 117),
            FIF.PALETTE,
            self.tr("左上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 右下角字体粗细
        self.rightBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            cfg.rightBottomBold,
            self.layoutGroup
        )
        
        # 字体大小
        self.baseFontSize = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("基础字号"),
            self.tr("设置基础字号"),
            minimum=1,
            maximum=20,
        )

        # 渲染质量
        self.baseQuality = SpinBoxSettingCard(
            FIF.ZOOM,
            self.tr("基础质量"),
            self.tr("设置基础质量"),
            minimum=1,
            maximum=100,
        )

        # 使用等效聚焦
        self.useEquivalentFocal = SwitchSettingCard(
            FIF.PIN,
            self.tr("使用等效焦距"),
            self.tr("是否使用等效焦距"),
            cfg.useEquivalentFocal,
            self.globalGroup
        )

        # 使用原始比例填充
        self.useOriginRatioPadding = SwitchSettingCard(
            FIF.ALBUM,
            self.tr("使用原始比例填充"),
            self.tr("是否使用原始比例填充"),
            cfg.useOriginRatioPadding,
            self.globalGroup
        )

        # 添加阴影
        self.addShadow = SwitchSettingCard(
            FIF.LEAF,
            self.tr("添加阴影"),
            self.tr("是否添加阴影"),
            cfg.addShadow,
            self.globalGroup
        )

        # 添加白色边框
        self.whiteMargin = SwitchSettingCard(
            FIF.COPY,
            self.tr("白色边框"),
            self.tr("是否添加白色边框"),
            cfg.whiteMargin,
            self.globalGroup
        )

        # 白色边框宽度
        self.whiteMarginWidth = SpinBoxSettingCard(
            FIF.COPY,
            self.tr("白色边框宽度"),
            self.tr("设置白色边框宽度"),
            minimum=1,
            maximum=100,
        )

    def _initLayout(self):
        """初始化布局"""
        # 添加卡片到组
        self.layoutGroup.addSettingCard(self.leftTopType)
        self.layoutGroup.addSettingCard(self.leftTopColor)
        self.layoutGroup.addSettingCard(self.leftTopBold)
        self.layoutGroup.addSettingCard(self.leftBottomType)
        self.layoutGroup.addSettingCard(self.leftBottomColor)
        self.layoutGroup.addSettingCard(self.leftBottomBold)
        self.layoutGroup.addSettingCard(self.rightTopType)
        self.layoutGroup.addSettingCard(self.rightTopColor)
        self.layoutGroup.addSettingCard(self.rightTopBold)
        self.layoutGroup.addSettingCard(self.rightBottomType)
        self.layoutGroup.addSettingCard(self.rightBottomColor)
        self.layoutGroup.addSettingCard(self.rightBottomBold)

        self.baseGroup.addSettingCard(self.baseFontSize)
        self.baseGroup.addSettingCard(self.baseQuality)

        self.globalGroup.addSettingCard(self.useEquivalentFocal)
        self.globalGroup.addSettingCard(self.useOriginRatioPadding)
        self.globalGroup.addSettingCard(self.addShadow)
        self.globalGroup.addSettingCard(self.whiteMargin)
        self.globalGroup.addSettingCard(self.whiteMarginWidth)

        # 添加组到布局
        self.settingsLayout.addWidget(self.baseGroup)
        self.settingsLayout.addWidget(self.globalGroup)
        self.settingsLayout.addWidget(self.layoutGroup)
        self.settingsLayout.addStretch(1)

        # 添加左右两侧到主布局
        self.hBoxLayout.addWidget(self.settingsScrollArea)
        self.hBoxLayout.addWidget(self.previewCard)

    def _initStyle(self):
        """初始化样式"""
        self.settingsWidget.setObjectName("settingsWidget")
        self.setStyleSheet(
            """        
            SubtitleStyleInterface, #settingsWidget {
                background-color: transparent;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        )

    def __setValues(self):
        """设置初始值"""
        # 设置布局内容
        self.leftTopType.comboBox.setCurrentText(display_type_key(cfg.get(cfg.leftTopType)))
        self.leftBottomType.comboBox.setCurrentText(display_type_key(cfg.get(cfg.leftBottomType)))
        self.rightTopType.comboBox.setCurrentText(display_type_key(cfg.get(cfg.rightTopType)))
        self.rightBottomType.comboBox.setCurrentText(display_type_key(cfg.get(cfg.rightBottomType)))

        self.baseQuality.setValue(cfg.get(cfg.baseQuality))
        self.baseFontSize.setValue(cfg.get(cfg.baseFontSize))
        self.whiteMarginWidth.setValue(cfg.get(cfg.whiteMarginWidth))

        # 设置字幕样式
        self.styleNameComboBox.comboBox.setCurrentText(cfg.get(cfg.subtitle_style_name))

        self.loadStyle("")

        # 获取系统字体,设置comboBox的选项
        # fontDatabase = QFontDatabase()
        # fontFamilies = fontDatabase.families()
        # self.subFontCard.addItems(fontFamilies)

        # 设置字体选项框最大显示数量
        # self.subFontCard.comboBox.setMaxVisibleItems(12)

        # 获取样式目录下的所有txt文件名
        # style_files = [f.stem for f in SUBTITLE_STYLE_PATH.glob("*.txt")]
        # if "default" in style_files:
        #     style_files.insert(0, style_files.pop(style_files.index("default")))
        # else:
        #     style_files.insert(0, "default")
        #     self.saveStyle("default")
        # self.styleNameComboBox.comboBox.addItems(style_files)

        # # 加载默认样式
        # subtitle_style_name = cfg.get(cfg.subtitle_style_name)
        # if subtitle_style_name in style_files:
        #     self.loadStyle(subtitle_style_name)
        #     self.styleNameComboBox.comboBox.setCurrentText(subtitle_style_name)
        # else:
        #     self.loadStyle(style_files[0])
        #     self.styleNameComboBox.comboBox.setCurrentText(style_files[0])

    def connectSignals(self):
        """连接所有设置变更的信号到预览更新函数"""
        # 左上角
        self.leftTopType.currentTextChanged.connect(self.onSettingChanged)
        print(f"设置 ----> {display_type_value(self.leftTopType.comboBox.currentText())}")
        self.leftTopType.currentTextChanged.connect(
            lambda: cfg.set(cfg.leftTopType, display_type_value(self.leftTopType.comboBox.currentText()))
        )
        self.leftTopColor.colorChanged.connect(self.onSettingChanged)

        # 左下角
        self.leftBottomType.currentTextChanged.connect(self.onSettingChanged)
        self.leftBottomType.currentTextChanged.connect(
            lambda: cfg.set(cfg.leftBottomType, display_type_value(self.leftBottomType.comboBox.currentText()))
        )
        self.leftBottomColor.colorChanged.connect(self.onSettingChanged)

        # 右上角
        self.rightTopType.currentTextChanged.connect(self.onSettingChanged)
        self.rightTopType.currentTextChanged.connect(
            lambda: cfg.set(cfg.rightTopType, display_type_value(self.rightTopType.comboBox.currentText()))
        )
        self.rightTopColor.colorChanged.connect(self.onSettingChanged)

        # 右下角
        self.rightBottomType.currentTextChanged.connect(self.onSettingChanged)
        self.rightBottomType.currentTextChanged.connect(
            lambda: cfg.set(cfg.rightBottomType, display_type_value(self.rightBottomType.comboBox.currentText()))
        )
        self.rightBottomColor.colorChanged.connect(self.onSettingChanged)

        self.baseFontSize.valueChanged.connect(self.onSettingChanged)
        self.baseQuality.valueChanged.connect(self.onSettingChanged)
        self.whiteMarginWidth.valueChanged.connect(self.onSettingChanged)


        # 连接样式切换信号
        self.styleNameComboBox.currentTextChanged.connect(self.loadStyle)
        self.newStyleButton.clicked.connect(self.createNewStyle)
        self.openStyleFolderButton.clicked.connect(self.on_open_style_folder_clicked)

    def on_open_style_folder_clicked(self):
        """打开样式文件夹"""
        if sys.platform == "win32":
            os.startfile(SUBTITLE_STYLE_PATH)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", SUBTITLE_STYLE_PATH])
        else:  # Linux
            subprocess.run(["xdg-open", SUBTITLE_STYLE_PATH])

    def onOrientationChanged(self):
        """当预览方向改变时调用"""
        orientation = self.orientationCard.comboBox.currentText()
        # preview_image = (
        #     DEFAULT_BG_LANDSCAPE if orientation == "横屏" else DEFAULT_BG_PORTRAIT
        # )
        # cfg.set(cfg.subtitle_preview_image, str(Path(preview_image["path"])))
        self.updatePreview()

    def onSettingChanged(self):
        """当任何设置改变时调用"""
        # 如果正在加载样式，不触发更新
        if self._loading_style:
            return

        self.updatePreview()
        # 获取当前选择的样式名称
        current_style = self.styleNameComboBox.comboBox.currentText()
        if current_style:
            self.saveStyle(current_style)  # 自动保存为当前选择的样式
        else:
            self.saveStyle("default")  # 如果没有选择样式,保存为默认样式

    def selectPreviewImage(self):
        """选择预览背景图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("选择背景图片"),
            "",
            self.tr("图片文件") + " (*.png *.jpg *.jpeg)",
        )
        if file_path:
            cfg.set(cfg.subtitle_preview_image, file_path)
            self.updatePreview()

    def updatePreview(self):
        # 创建预览线程
        print("创建预览线程....")
        cache_preview = Path(CACHE_PATH) / "preview.png"
        self.preview_task = ImageHandleTask(Path(DEFAULT_BG["path"]), cache_preview)
        self.preview_thread = ImageHandleThread(self.preview_task)
        self.preview_thread.finished.connect(self.onPreviewReady)
        self.preview_thread.start()

    def onPreviewReady(self, preview_path):
        """预览图片生成完成的回调"""
        self.previewImage.setImage(preview_path)
        self.updatePreviewImage()

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
        # style_path = SUBTITLE_STYLE_PATH / f"{style_name}.txt"

        # if not style_path.exists():
        #     return

        # # 设置标志位，防止触发onSettingChanged
        # self._loading_style = True

        # with open(style_path, "r", encoding="utf-8") as f:
        #     style_content = f.read()

        # # 解析样式内容
        # for line in style_content.split("\n"):
        #     if line.startswith("Style: Default"):
        #         # 解析主字幕样式
        #         parts = line.split(",")
        #         self.mainSizeCard.spinBox.setValue(int(parts[2]))

        #         vertical_spacing = int(parts[17])
        #         // 需要修改
        #         self.leftTopColor.setColor(QColor(parts[3]))

        #         self.mainSpacingCard.spinBox.setValue(float(parts[13]))
        #         self.mainOutlineSizeCard.spinBox.setValue(float(parts[16]))
        #     elif line.startswith("Style: Secondary"):
        #         # 解析副字幕样式
        #         parts = line.split(",")
        #         self.subFontCard.setCurrentText(parts[1])
        #         self.subSizeCard.spinBox.setValue(int(parts[2]))

        #         self.subSpacingCard.spinBox.setValue(float(parts[13]))
        #         self.subOutlineSizeCard.spinBox.setValue(float(parts[16]))

        # cfg.set(cfg.subtitle_style_name, style_name)

        # # 重置标志位
        # self._loading_style = False

        # # 手动更新一次预览
        self.updatePreview()

        # # 显示加载成功提示
        # InfoBar.success(
        #     title=self.tr("成功"),
        #     content=self.tr("已加载样式 ") + style_name,
        #     orient=Qt.Horizontal,
        #     isClosable=True,
        #     position=InfoBarPosition.TOP,
        #     duration=1500,
        #     parent=self,
        # )

    def createNewStyle(self):
        """创建新样式"""
        dialog = StyleNameDialog(self)
        if dialog.exec():
            style_name = dialog.nameLineEdit.text().strip()
            if not style_name:
                return

            # 检查是否已存在同名样式
            if (SUBTITLE_STYLE_PATH / f"{style_name}.txt").exists():
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
        Args:
            style_name (str): 样式名称
        """
        # 确保样式目录存在
        # SUBTITLE_STYLE_PATH.mkdir(parents=True, exist_ok=True)

        # # 生成样式内容并保存
        # style_content = self.generateAssStyles()
        # style_path = SUBTITLE_STYLE_PATH / f"{style_name}.txt"

        # with open(style_path, "w", encoding="utf-8") as f:
        #     f.write(style_content)


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
