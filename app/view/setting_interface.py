import os
import subprocess
import sys
from pathlib import Path
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, PrimaryPushButton
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

from app.config import cfg, STYLE_PATH
from app.components.common_card import (
    ComboBoxSettingCard,
    SpinBoxSettingCard,
    ColorSettingCard,
    SwitchSettingCard
)
from app.config import ASSETS_PATH, CACHE_PATH, LOGO_LAYOUT, MARK_MODE
from app.utils.mater_mark_preview import generate_preview
from app.entity.constants import DISPLAY_TYPE, display_type_key, display_type_value
from app.thread.image_handle_thread import ImageHandleTask, ImageHandleThread, HandleProgress, ImageHandleStatus
from app.components.common_item import LoadingButton

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

        # 基础样式
        self.baseBackgroundValue = QColor(cfg.backgroundColor.value)
        self.baseFontSizeValue = cfg.baseFontSize.value
        self.baseQualityValue = cfg.baseQuality.value

        # 模式选择
        self.modeValue = MARK_MODE.key(cfg.markMode.value)

        # 全局样式
        self.useEquivalentFocalValue = cfg.useEquivalentFocal.value
        self.useOriginRatioPaddingValue = cfg.useOriginRatioPadding.value
        self.addShadowValue = cfg.addShadow.value
        self.whiteMarginValue = cfg.whiteMargin.value
        self.whiteMarginWidthValue = cfg.whiteMarginWidth.value

        # LOGO样式
        self.logoEnableValue = cfg.logoEnable.value
        self.logoLayoutValue = LOGO_LAYOUT.LEFT if cfg.isLogoLeft else LOGO_LAYOUT.RIGHT

        # 布局样式
        self.leftTopTypeValue = display_type_key(cfg.leftTopType.value)
        self.leftTopFontColorValue = QColor(cfg.leftTopFontColor.value)
        self.leftTopBoldValue = cfg.leftTopBold.value

        self.leftBottomTypeValue = display_type_key(cfg.leftBottomType.value)
        self.leftBottomFontColorValue = QColor(cfg.leftBottomFontColor.value)
        self.leftBottomBoldValue = cfg.leftBottomBold.value

        self.rightTopTypeValue = display_type_key(cfg.rightTopType.value)
        self.rightTopFontColorValue = QColor(cfg.rightTopFontColor.value)
        self.rightTopBoldValue = cfg.rightTopBold.value

        self.rightBottomTypeValue = display_type_key(cfg.rightBottomType.value)
        self.rightBottomFontColorValue = QColor(cfg.rightBottomFontColor.value)
        self.rightBottomBoldValue = cfg.rightBottomBold.value

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
        self.modeGroup = SettingCardGroup(self.tr("模式"), self.settingsWidget)
        self.globalGroup = SettingCardGroup(self.tr("全局"), self.settingsWidget)
        self.logoGroup = SettingCardGroup(self.tr("LOGO"), self.settingsWidget)
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
        # 基础样式

        # 背景颜色
        self.baseBackground = ColorSettingCard(
            self.baseBackgroundValue,
            FIF.PALETTE,
            self.tr("背景颜色"),
            self.tr("设置照片背景颜色"),
        )

        # 字体大小
        self.baseFontSize = SpinBoxSettingCard(
            FIF.FONT_SIZE,
            self.tr("基础字号"),
            self.tr("设置基础字号"),
            minimum=1,
            maximum=3,
        )

        # 模式
        self.markMode = ComboBoxSettingCard(
            FIF.MORE,
            self.tr("布局模式"),
            self.tr("设置布局模式"),
            texts=MARK_MODE.all_values(),
        )

        # 全局样式

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
            None,
            self.globalGroup
        )

        # 使用原始比例填充
        self.useOriginRatioPadding = SwitchSettingCard(
            FIF.ALBUM,
            self.tr("使用原始比例填充"),
            self.tr("是否使用原始比例填充"),
            None,
            self.globalGroup
        )

        # 添加阴影
        self.addShadow = SwitchSettingCard(
            FIF.LEAF,
            self.tr("添加阴影"),
            self.tr("是否添加阴影"),
            None,
            self.globalGroup
        )

        # 添加白色边框
        self.whiteMargin = SwitchSettingCard(
            FIF.COPY,
            self.tr("白色边框"),
            self.tr("是否添加白色边框"),
            None,
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

        # LOGO样式
        self.logoEnable = SwitchSettingCard(
            FIF.LAYOUT,
            self.tr("展示LOGO"),
            self.tr("是否展示LOGO"),
            None,
            self.logoGroup
        )

        self.logoLayout = ComboBoxSettingCard(
            FIF.LAYOUT,
            self.tr("LOGO布局"),
            self.tr("设置LOGO布局样式"),
            texts=LOGO_LAYOUT.all_values(),
        )

        # 布局样式

        # 左上角类型
        self.leftTopType = ComboBoxSettingCard(
            FIF.VIEW,
            self.tr("左上角类型"),
            self.tr("设置左上角展示信息的类型"),
            texts=DISPLAY_TYPE.keys(),
        )

        # 左上角字体颜色
        self.leftTopColor = ColorSettingCard(
            self.leftTopFontColorValue,
            FIF.PALETTE,
            self.tr("左上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 左上角字体粗细
        self.leftTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
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
            self.leftBottomFontColorValue,
            FIF.PALETTE,
            self.tr("左下角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 左下角字体粗细
        self.leftBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左下角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
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
            self.rightTopFontColorValue,
            FIF.PALETTE,
            self.tr("右上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 右上角字体粗细
        self.rightTopBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
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
            self.rightBottomFontColorValue,
            FIF.PALETTE,
            self.tr("左上角字体颜色"),
            self.tr("设置左上角字体颜色"),
        )

        # 右下角字体粗细
        self.rightBottomBold = SwitchSettingCard(
            FIF.FONT_SIZE,
            self.tr("左上角字体是否加粗"),
            self.tr("设置左上角字体是否加粗"),
            None,
            self.layoutGroup
        )

    def _initLayout(self):
        """初始化布局"""
        # 添加卡片到组

        # 基础样式
        self.baseGroup.addSettingCard(self.baseBackground)
        self.baseGroup.addSettingCard(self.baseFontSize)
        self.baseGroup.addSettingCard(self.baseQuality)

        # 模式
        self.modeGroup.addSettingCard(self.markMode)

        # LOGO样式
        self.logoGroup.addSettingCard(self.logoEnable)
        self.logoGroup.addSettingCard(self.logoLayout)

        # 全局样式
        self.globalGroup.addSettingCard(self.useEquivalentFocal)
        self.globalGroup.addSettingCard(self.useOriginRatioPadding)
        self.globalGroup.addSettingCard(self.addShadow)
        self.globalGroup.addSettingCard(self.whiteMargin)
        self.globalGroup.addSettingCard(self.whiteMarginWidth)

        # 布局样式
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

        # 添加组到布局
        self.settingsLayout.addWidget(self.baseGroup)
        self.settingsLayout.addWidget(self.modeGroup)
        self.settingsLayout.addWidget(self.globalGroup)
        self.settingsLayout.addWidget(self.logoGroup)
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

    def __setSettings(self):
        # 设置样式到UI上

        # 基础样式
        self.baseBackground.setColor(self.baseBackgroundValue)
        self.baseQuality.setValue(self.baseQualityValue)
        self.baseFontSize.setValue(self.baseFontSizeValue)

        # 模式
        self.markMode.comboBox.setCurrentText(self.modeValue.value)

        # 全局样式
        self.useEquivalentFocal.setValue(self.useEquivalentFocalValue)
        self.useOriginRatioPadding.setValue(self.useOriginRatioPaddingValue)
        self.addShadow.setValue(self.addShadowValue)
        self.whiteMargin.setValue(self.whiteMarginValue)
        self.whiteMarginWidth.setValue(self.whiteMarginWidthValue)

        # LOGO样式
        self.logoEnable.setValue(self.logoEnableValue)
        self.logoLayout.comboBox.setCurrentText(self.logoLayoutValue.value)

        # 布局样式
        self.leftTopType.comboBox.setCurrentText(
            self.leftTopTypeValue)
        self.leftTopColor.setColor(self.leftTopFontColorValue)
        self.leftTopBold.setValue(self.leftTopBoldValue)

        self.leftBottomType.comboBox.setCurrentText(
            self.leftBottomTypeValue)
        self.leftBottomColor.setColor(self.leftBottomFontColorValue)
        self.leftBottomBold.setValue(self.leftBottomBoldValue)

        self.rightTopType.comboBox.setCurrentText(
            self.rightTopTypeValue)
        self.rightTopColor.setColor(self.rightTopFontColorValue)
        self.rightTopBold.setValue(self.rightTopBoldValue)

        self.rightBottomType.comboBox.setCurrentText(
            self.rightBottomTypeValue)
        self.rightBottomColor.setColor(self.rightBottomFontColorValue)
        self.rightBottomBold.setValue(self.rightBottomBoldValue)

        self.__setInitHiddens()

    def __setInitHiddens(self):
        self.logoEnable.setHidden(self.modeValue.isSimple())
        self.logoLayout.setHidden(True if self.modeValue.isSimple() else not self.logoEnable)

        self.logoGroup.setHidden(self.modeValue.isSimple())
        self.layoutGroup.setHidden(self.modeValue.isSimple())

        # self.leftTopType.setHidden(self.modeValue.isSimple())
        # self.leftTopColor.setHidden(self.modeValue.isSimple())
        # self.leftTopBold.setHidden(self.modeValue.isSimple())

        # self.leftBottomType.setHidden(self.modeValue.isSimple())
        # self.leftBottomColor.setHidden(self.modeValue.isSimple())
        # self.leftBottomBold.setHidden(self.modeValue.isSimple()) 

        # self.rightTopType.setHidden(self.modeValue.isSimple())
        # self.rightTopColor.setHidden(self.modeValue.isSimple())
        # self.rightTopBold.setHidden(self.modeValue.isSimple())

        # self.rightBottomType.setHidden(self.modeValue.isSimple())
        # self.rightBottomColor.setHidden(self.modeValue.isSimple())
        # self.rightBottomBold.setHidden(self.modeValue.isSimple())
            

    def __setValues(self):
        """设置初始值"""
        # 设置布局内容
        self.__setSettings()

        # 设置字幕样式
        self.styleNameComboBox.comboBox.setCurrentText(
            cfg.get(cfg.styleName))

        # 获取系统字体,设置comboBox的选项
        # fontDatabase = QFontDatabase()
        # fontFamilies = fontDatabase.families()
        # self.subFontCard.addItems(fontFamilies)

        # 设置字体选项框最大显示数量
        # self.subFontCard.comboBox.setMaxVisibleItems(12)

        # 获取样式目录下的所有json文件名
        style_files = [f.stem for f in STYLE_PATH.glob("*.json")]
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

        # 基础样式
        self.baseBackground.colorChanged.connect(
            lambda text: setattr(self, "baseBackgroundValue", text))
        self.baseFontSize.valueChanged.connect(
            lambda text: setattr(self, "baseFontSizeValue", text))
        self.baseQuality.valueChanged.connect(
            lambda text: setattr(self, "baseQualityValue", text))
        
        # 模式
        self.markMode.currentTextChanged.connect(self.on_mark_mode_change)

        # 全局样式
        self.whiteMarginWidth.valueChanged.connect(
            lambda text: setattr(self, "whiteMarginWidthValue", text))
        self.useEquivalentFocal.checkedChanged.connect(
            lambda text: setattr(self, "useEquivalentFocalValue", text))
        self.useOriginRatioPadding.checkedChanged.connect(
            lambda text: setattr(self, "useOriginRatioPaddingValue", text))
        self.addShadow.checkedChanged.connect(
            lambda text: setattr(self, "addShadowValue", text))
        self.whiteMargin.checkedChanged.connect(
            lambda text: setattr(self, "whiteMarginValue", text))
        
        # LOGO样式

        self.logoEnable.checkedChanged.connect(self.onLogoEnableChanged)
        self.logoLayout.currentTextChanged.connect(lambda text: setattr(self, "logoLayoutValue", LOGO_LAYOUT.get_enum(text)))

        # 布局样式

        # 左上角
        self.leftTopType.currentTextChanged.connect(
            lambda text: setattr(self, "leftTopTypeValue", text))
        self.leftTopColor.colorChanged.connect(
            lambda text: setattr(self, "leftTopFontColorValue", text))
        self.leftTopBold.checkedChanged.connect(
            lambda text: setattr(self, "leftTopBoldValue", text))

        # 左下角
        self.leftBottomType.currentTextChanged.connect(
            lambda text: setattr(self, "leftBottomTypeValue", text))
        self.leftBottomColor.colorChanged.connect(
            lambda text: setattr(self, "leftBottomFontColorValue", text))
        self.leftBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "leftBottomBoldValue", text))

        # 右上角
        self.rightTopType.currentTextChanged.connect(
            lambda text: setattr(self, "rightTopTypeValue", text))
        self.rightTopColor.colorChanged.connect(
            lambda text: setattr(self, "rightTopFontColorValue", text))
        self.rightTopBold.checkedChanged.connect(
            lambda text: setattr(self, "rightTopBoldValue", text))

        # 右下角
        self.rightBottomType.currentTextChanged.connect(
            lambda text: setattr(self, "rightBottomTypeValue", text))
        self.rightBottomColor.colorChanged.connect(
            lambda text: setattr(self, "rightBottomFontColorValue", text))
        self.rightBottomBold.checkedChanged.connect(
            lambda text: setattr(self, "rightBottomBoldValue", text))

        # 连接样式切换信号
        self.styleNameComboBox.currentTextChanged.connect(self.loadStyle)
        self.newStyleButton.clicked.connect(self.createNewStyle)
        self.openStyleFolderButton.clicked.connect(
            self.on_open_style_folder_clicked)
        
    def on_mark_mode_change(self):
        self.modeValue = MARK_MODE.get_enum(self.markMode.comboBox.text())
        self.__setInitHiddens()
        
    def onLogoEnableChanged(self, logoEnable):
        self.logoEnableValue = logoEnable
        self.logoLayout.setHidden(not self.logoEnableValue)

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

    def updatePreview(self):
        # 创建预览线程
        self.renderButton.start_loading()
        cache_preview = Path(CACHE_PATH) / "preview.png"
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        self.preview_task = ImageHandleTask(
            Path(DEFAULT_BG["path"]), cache_preview)
        self.preview_thread = ImageHandleThread([self.preview_task])
        self.preview_thread.finished.connect(self.onPreviewReady)
        self.preview_thread.start()

    def onPreviewReady(self, progress: HandleProgress):
        """预览图片生成完成的回调"""
        task = progress.tasks[0]
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
            InfoBar.error(
                self.tr("处理错误"),
                self.tr("图片渲染错误"),
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
        style_path = STYLE_PATH / f"{style_name}.json"

        if not style_path.exists():
            return

        # # 设置标志位，防止触发onSettingChanged
        self._loading_style = True

        with open(style_path, "r", encoding="utf-8") as f:
            style_content = json.load(f)

        # 解析样式内容

        # 基础样式
        self.baseFontSizeValue = style_content["Base"]["BaseFontSize"]
        self.baseQualityValue = int(style_content["Base"]["BaseQuality"])
        self.baseBackgroundValue = QColor(
            style_content["Base"]["BackgroundColor"])
        
        # 模式
        self.modeValue = MARK_MODE.key(style_content["Mode"]["MarkMode"])

        # 全局样式
        self.useEquivalentFocalValue = style_content["Global"]["UseEquivalentFocal"]
        self.useOriginRatioPaddingValue = style_content["Global"]["UseOriginRatioPadding"]
        self.addShadowValue = style_content["Global"]["AddShadow"]
        self.whiteMarginValue = style_content["Global"]["WhiteMargin"]
        self.whiteMarginWidthValue = int(
            style_content["Global"]["WhiteMarginWidth"])
        
        # LOGO布局
        self.logoEnableValue = style_content["LOGO"]["LogoEnable"]
        self.logoLayoutValue = LOGO_LAYOUT.LEFT if style_content["LOGO"]["isLogoLeft"] else LOGO_LAYOUT.RIGHT

        # 布局样式
        self.leftTopTypeValue = display_type_key(
            style_content["Layout"]["LeftTopType"])
        self.leftTopFontColorValue = QColor(
            style_content["Layout"]["LeftTopFontColor"])
        self.leftTopBoldValue = style_content["Layout"]["LeftTopBold"]

        self.leftBottomTypeValue = display_type_key(
            style_content["Layout"]["LeftBottomType"])
        self.leftBottomFontColorValue = QColor(
            style_content["Layout"]["LeftBottomFontColor"])
        self.leftBottomBoldValue = style_content["Layout"]["LeftBottomBold"]

        self.rightTopTypeValue = display_type_key(
            style_content["Layout"]["RightTopType"])
        self.rightTopFontColorValue = QColor(
            style_content["Layout"]["RightTopFontColor"])
        self.rightTopBoldValue = style_content["Layout"]["RightTopBold"]

        self.rightBottomTypeValue = display_type_key(
            style_content["Layout"]["RightBottomType"])
        self.rightBottomFontColorValue = QColor(
            style_content["Layout"]["RightBottomFontColor"])
        self.rightBottomBoldValue = style_content["Layout"]["RightBottomBold"]

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
            if (STYLE_PATH / f"{style_name}.json").exists():
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
        STYLE_PATH.mkdir(parents=True, exist_ok=True)

        # 基础样式
        cfg.set(cfg.backgroundColor, self.baseBackgroundValue.name())
        cfg.set(cfg.baseFontSize, self.baseFontSizeValue)
        cfg.set(cfg.baseQuality, self.baseQualityValue)

        # 模式
        cfg.set(cfg.markMode, self.modeValue.info())

        # 全局样式
        cfg.set(cfg.useEquivalentFocal, self.useEquivalentFocalValue)
        cfg.set(cfg.useOriginRatioPadding, self.useOriginRatioPaddingValue)
        cfg.set(cfg.addShadow, self.addShadowValue)
        cfg.set(cfg.whiteMarginWidth, self.whiteMarginWidthValue)

        # LOGO布局
        cfg.set(cfg.logoEnable, self.logoEnableValue)
        cfg.set(cfg.isLogoLeft, self.logoLayoutValue.isLeft())

        # 布局样式
        cfg.set(cfg.leftTopType, display_type_value(self.leftTopTypeValue))
        cfg.set(cfg.leftTopFontColor, self.leftTopFontColorValue.name())
        cfg.set(cfg.leftTopBold, self.leftTopBoldValue)

        cfg.set(cfg.leftBottomType, display_type_value(
            self.leftBottomTypeValue))
        cfg.set(cfg.leftBottomFontColor, self.leftBottomFontColorValue.name())
        cfg.set(cfg.leftBottomBold, self.leftBottomBoldValue)

        cfg.set(cfg.rightTopType, display_type_value(self.rightTopTypeValue))
        cfg.set(cfg.rightTopFontColor, self.rightTopFontColorValue.name())
        cfg.set(cfg.rightTopBold, self.rightTopBoldValue)

        cfg.set(cfg.rightBottomType, display_type_value(
            self.rightBottomTypeValue))
        cfg.set(cfg.rightBottomFontColor,
                self.rightBottomFontColorValue.name())
        cfg.set(cfg.rightBottomBold, self.rightBottomBoldValue)

        # # 生成样式内容并保存
        config_dict = cfg.to_dict()
        style_path = STYLE_PATH / f"{style_name}.json"

        with open(style_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4)

    def resetStyle(self):
        self._initValues()
        self.__setSettings()

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
