import os
from enum import Enum
from typing import List
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
from dataclasses import dataclass
from app.config import cfg, LOGO_PATH
from app.entity.enums import MARK_MODE, ExifId
from app.entity.custom_error import CustomError
from PIL import Image, ImageOps
from PIL.Image import Transpose
from app.entity.image_info import ImageInfo
from app.utils.image_handle import (
    text_to_image,
    concatenate_image,
    padding_image,
    append_image_by_side,
    resize_image_with_width,
    merge_images,
    resize_image_with_height
)
from app.manager.font_manager import font_manager
from app.utils.image_render import (
    add_shadow,
    add_rounded_corners,
    add_white_margin,
    add_background_blur
)
from app.entity.enums import ExifId, DISPLAY_TYPE
from app.utils.logger import setup_logger
logger = setup_logger("image_handle_thread")


NORMAL_HEIGHT = 1000
TRANSPARENT = (0, 0, 0, 0)
GRAY = '#CBCBC9'
LINE_TRANSPARENT = Image.new('RGBA', (20, 1000), color=TRANSPARENT)
LINE_GRAY = Image.new('RGBA', (20, 1000), color=GRAY)
SMALL_VERTICAL_GAP = Image.new('RGBA', (20, 50), color=TRANSPARENT)
MIDDLE_VERTICAL_GAP = Image.new('RGBA', (20, 100), color=TRANSPARENT)
MIDDLE_HORIZONTAL_GAP = Image.new('RGBA', (100, 20), color=TRANSPARENT)
LARGE_HORIZONTAL_GAP = Image.new('RGBA', (200, 20), color=TRANSPARENT)


class ImageHandleStatus(Enum):
    WAITING = "等待中"
    PROCESSING = "处理中"
    FINISHED = "已完成"
    ERROR = "出错"


@dataclass
class ImageHandleTask:
    image_path: Path
    target_path: Path
    status: ImageHandleStatus = ImageHandleStatus.WAITING
    errorInfo: str = ""


@dataclass
class HandleProgress:
    tasks: List[ImageHandleTask]
    progress: int


class ImageHandleThread(QThread):
    finished = pyqtSignal(HandleProgress)
    loading = pyqtSignal(HandleProgress)
    error = pyqtSignal(str)

    def __init__(self, tasks: List[ImageHandleStatus]):
        super().__init__()
        self.tasks = tasks
        self.image: Image.Image = None
        self.watermark_img = None
        self._logos = {}

    def get_ratio(self):
        return self.image.width / self.image.height

    def get_watermark_img(self) -> Image.Image:
        if self.watermark_img is None:
            self.watermark_img = self.image.copy()
        return self.watermark_img

    def get_width(self):
        return self.get_watermark_img().width

    def get_height(self):
        return self.get_watermark_img().height

    def update_watermark_img(self, watermark_img) -> None:
        if self.watermark_img == watermark_img:
            return
        original_watermark_img = self.watermark_img
        self.watermark_img = watermark_img
        if original_watermark_img is not None:
            original_watermark_img.close()

    def load_logo(self, make: str) -> Image.Image:
        """
        根据厂商获取 logo
        :param make: 厂商
        :return: logo
        """
        if cfg.customLogoEnable.value:
            if self._logos.get("custom") is None:
                if not os.path.exists(cfg.customLogoPath.value):
                    raise CustomError("自定义Logo不存在")
                custom_logo_path = Path(cfg.customLogoPath.value)
                self._logos["custom"] = Image.open(custom_logo_path)
            return self._logos["custom"]

        # 已经读到内存中的 logo
        if make in self._logos:
            return self._logos[make]
        # 未读取到内存中的 logo
        for (key, value) in LOGO_PATH.items():
            if key == '':
                pass
            if key.lower() in make.lower():
                logo = Image.open(value)
                self._logos[make] = logo
                return logo
        logo_path = LOGO_PATH['default']
        logo = Image.open(logo_path)
        self._logos[make] = logo
        return logo

    def run(self):
        progress = 0
        for index, task in enumerate(self.tasks):
            try:
                self.image = Image.open(task.image_path)
                self.image = add_rounded_corners(self.image)
                self.watermark_img = self.image.copy()
                image_info = ImageInfo(task.image_path)
                self.fix_orientation(image_info)
                self.tasks[index].status = ImageHandleStatus.PROCESSING
                self.loading.emit(HandleProgress(self.tasks, progress))
                self.hanle_task(image_info)
                self.save(task.target_path, quality=cfg.baseQuality.value)

                self.tasks[index].status = ImageHandleStatus.FINISHED
                progress = int(index / len(self.tasks) * 100)
                self.loading.emit(HandleProgress(self.tasks, progress))
            except CustomError as e:
                self.tasks[index].status = ImageHandleStatus.ERROR
                self.tasks[index].errorInfo = e.message
                self.loading.emit(HandleProgress(self.tasks, progress))
            except Exception as e:
                logger.exception(f"渲染出错，Error: {str(e)}")
                self.tasks[index].status = ImageHandleStatus.ERROR
                self.tasks[index].errorInfo = "未知错误"
                self.loading.emit(HandleProgress(self.tasks, progress))
        self.close()
        self.finished.emit(HandleProgress(self.tasks, 100))

    def hanle_task(self, image_info: ImageInfo):
        mode: MARK_MODE = MARK_MODE.key(cfg.markMode.value)
        if (cfg.addShadow.value):
            image = add_shadow(self.get_watermark_img())
            self.update_watermark_img(image)

        if (cfg.backgroundBlur.value):
            image = add_background_blur(
                self.get_watermark_img(), bottom_padding=self.cal_watermark_height(image_info, mode))
            self.update_watermark_img(image)

        if (cfg.whiteMargin.value):
            image = add_white_margin(self.get_watermark_img())
            self.update_watermark_img(image)

        if mode == MARK_MODE.SIMPLE:
            self.simple_mode(image_info)
        else:
            self.standard_mode(image_info)

    def simple_mode(self, image_info: ImageInfo):
        watermark = self.generate_simple_watermark(image_info)

        if cfg.backgroundBlur.value:
            # 将水印图片底部对齐作为前景叠加到原图
            bg = self.get_watermark_img().convert('RGBA')
            fg = Image.new('RGBA', bg.size, TRANSPARENT)
            fg.paste(watermark, (0, bg.height - watermark.height), watermark)
            result = Image.alpha_composite(bg, fg)

            self.update_watermark_img(result)
        else:
             # 将水印图片作为底部扩展叠加到原图
            bg = Image.new('RGBA', watermark.size, color='white')
            bg = Image.alpha_composite(bg, watermark)

            watermark_img = merge_images([self.get_watermark_img(), bg], 1, 1)
            self.update_watermark_img(watermark_img) 

    def generate_simple_watermark(self, image_info: ImageInfo):
        ratio = cfg.simpleScale.value
        padding_ratio = cfg.simplePaddingScale.value
        logo_ratio = cfg.simpleLogoSize.value

        self.bg_color = cfg.backgroundColor.value

        images = []
        if cfg.logoEnable.value:
            logo = self.load_logo(image_info.logo())
            logo = resize_image_with_height(logo, int(logo.height * logo_ratio), auto_close=False)
            images.append(logo)
            images.append(LARGE_HORIZONTAL_GAP)

        first_display_type: DISPLAY_TYPE = DISPLAY_TYPE.from_str(cfg.simpleFirstLineType.value)
        if first_display_type != DISPLAY_TYPE.NONE:
            first_text = text_to_image(image_info.parse_exif_info(cfg.simpleFirstLineType.value),
                                       font_manager.get_font(),
                                       font_manager.get_bold_font(),
                                       is_bold=cfg.simpleFirstLineBold.value,
                                       fill=cfg.simpleFirstLineColor.value,
                                       color=self.bg_color)
            images.append(first_text)
            images.append(MIDDLE_VERTICAL_GAP)

        second_display_type: DISPLAY_TYPE = DISPLAY_TYPE.from_str(cfg.simpleSecondLineType.value)
        if second_display_type != DISPLAY_TYPE.NONE:
            second_text = text_to_image(image_info.parse_exif_info(cfg.simpleSecondLineType.value),
                                        font_manager.get_font(),
                                        font_manager.get_bold_font(),
                                        is_bold=cfg.simpleSecondLineBold.value,
                                        fill=cfg.simpleSecondLineColor.value,
                                        color=self.bg_color)
            images.append(second_text)
            images.append(MIDDLE_VERTICAL_GAP)
        
        third_display_type: DISPLAY_TYPE = DISPLAY_TYPE.from_str(cfg.simpleThirdLineType.value)
        if third_display_type != DISPLAY_TYPE.NONE:
            third_text = text_to_image(image_info.parse_exif_info(cfg.simpleThirdLineType.value),
                                       font_manager.get_font(),
                                       font_manager.get_bold_font(),
                                       is_bold=cfg.simpleThirdLineBold.value,
                                       fill=cfg.simpleThirdLineColor.value,
                                       color=self.bg_color)
            images.append(third_text)

        image = merge_images(images, 1, 0)

        content_height = self.get_height() * ratio
        
        height = content_height * (1 - padding_ratio)
        image = resize_image_with_height(image, int(height))
        horizontal_padding = int((self.get_width() - image.width) / 2)
        vertical_padding = int((content_height - image.height) / 2)

        return ImageOps.expand(
            image, (horizontal_padding, vertical_padding, horizontal_padding, vertical_padding), fill=TRANSPARENT)

    def standard_mode(self, image_info: ImageInfo):
        watermark = self.generate_standard_watermark(image_info)

        if cfg.backgroundBlur.value:
            # 将水印图片底部对齐作为前景叠加到原图
            bg = self.get_watermark_img().convert('RGBA')
            fg = Image.new('RGBA', bg.size, TRANSPARENT)
            fg.paste(watermark, (0, bg.height - watermark.height), watermark)
            result = Image.alpha_composite(bg, fg)
        else:  
          # 将水印图片放置在原始图片的下方
          bg = ImageOps.expand(self.get_watermark_img().convert('RGBA'),
                              border=(0, 0, 0, watermark.height),
                              fill=TRANSPARENT)
          fg = ImageOps.expand(watermark, border=(
              0, self.get_height(), 0, 0), fill=TRANSPARENT)
          result = Image.alpha_composite(bg, fg)
        
        watermark.close()
        # 更新图片对象
        result = ImageOps.exif_transpose(result).convert('RGBA')
        self.update_watermark_img(result)

    def generate_standard_watermark(self, image_info: ImageInfo):
        self.bg_color = cfg.backgroundColor.value

        # 下方水印的占比
        ratio = (.04 if self.get_ratio() >= 1 else .09) + \
            0.02 * cfg.get_font_padding_level()
        # 水印中上下边缘空白部分的占比
        padding_ratio = (.52 if self.get_ratio() >= 1 else .7) - \
            0.04 * cfg.get_font_padding_level()
        final_padding_ratio = padding_ratio if cfg.standardVerticalPadding.value < 0 else cfg.standardVerticalPadding.value

        # 创建一个空白的水印图片
        watermark = Image.new(
            'RGBA', (int(NORMAL_HEIGHT / ratio), NORMAL_HEIGHT), color=self.bg_color)

        with Image.new('RGBA', (10, 100), color=self.bg_color) as empty_padding:
            # 填充左边的文字内容
            left_top = text_to_image(image_info.parse_exif_info(cfg.leftTopType.value),
                                     font_manager.get_font(),
                                     font_manager.get_bold_font(),
                                     is_bold=cfg.leftTopBold.value,
                                     fill=cfg.leftTopFontColor.value,
                                     color=self.bg_color)
            left_bottom = text_to_image(image_info.parse_exif_info(cfg.leftBottomType.value),
                                        font_manager.get_font(),
                                        font_manager.get_bold_font(),
                                        is_bold=cfg.leftBottomBold.value,
                                        fill=cfg.leftBottomFontColor.value,
                                        color=self.bg_color)
            left = concatenate_image(
                [left_top, empty_padding, left_bottom], color=self.bg_color)
            # 填充右边的文字内容
            right_top = text_to_image(image_info.parse_exif_info(cfg.rightTopType.value),
                                      font_manager.get_font(),
                                      font_manager.get_bold_font(),
                                      is_bold=cfg.rightTopBold.value,
                                      fill=cfg.rightTopFontColor.value,
                                      color=self.bg_color)
            right_bottom = text_to_image(image_info.parse_exif_info(cfg.rightBottomType.value),
                                         font_manager.get_font(),
                                         font_manager.get_bold_font(),
                                         is_bold=cfg.rightBottomBold.value,
                                         fill=cfg.rightBottomFontColor.value,
                                         color=self.bg_color)
            right = concatenate_image(
                [right_top, empty_padding, right_bottom], color=self.bg_color)

        # 将左右两边的文字内容等比例缩放到相同的高度
        max_height = max(left.height, right.height)
        left = padding_image(
            left, int(max_height * final_padding_ratio), 'tb', color=self.bg_color)
        right = padding_image(right, int(
            max_height * final_padding_ratio), 't', color=self.bg_color)
        right = padding_image(right, left.height -
                              right.height, 'b',  color=self.bg_color)

        logo = self.load_logo(image_info.logo())
        if cfg.logoEnable.value:
            if cfg.isLogoLeft.value:
                # 如果 logo 在左边
                line = LINE_TRANSPARENT.copy()
                logo = padding_image(
                    logo, int(final_padding_ratio * logo.height), color=self.bg_color)
                append_image_by_side(
                    watermark, 
                    [line, logo, left], 
                    padding=cfg.standardLeftPadding.value, 
                    is_start=logo is None
                )
                append_image_by_side(watermark, [right], padding=cfg.standardRightPadding.value, side='right')
            else:
                # 如果 logo 在右边
                if logo is not None:
                    # 如果 logo 不为空，等比例缩小 logo
                    logo = padding_image(
                        logo, int(padding_ratio * logo.height))
                    # 插入一根线条用于分割 logo 和文字
                    line = padding_image(LINE_GRAY, int(
                        padding_ratio * LINE_GRAY.height * .8))
                else:
                    line = LINE_TRANSPARENT.copy()
                append_image_by_side(watermark, [left], padding=cfg.standardLeftPadding.value, is_start=True)
                append_image_by_side(
                    watermark, [logo, line, right], padding=cfg.standardRightPadding.value, side='right')
                line.close()
        else:
            append_image_by_side(watermark, [left], padding=cfg.standardLeftPadding.value, is_start=True)
            append_image_by_side(watermark, [right], padding=cfg.standardRightPadding.value, side='right')
        left.close()
        right.close()

        # 缩放水印的大小
        watermark = resize_image_with_width(watermark, self.get_width())
        return watermark

    def cal_watermark_height(self, image_info: ImageInfo, mode: MARK_MODE):
        """
        计算水印高度
        :param image_info: 图片信息
        :param mode: 水印模式
        :return: 水印的高度
        """
        if mode == MARK_MODE.SIMPLE:
            return self.generate_simple_watermark(image_info).height
        else:
            return self.generate_standard_watermark(image_info).height

    def fix_orientation(self, image_info: ImageInfo):
        self.orientation = image_info.exif[ExifId.ORIENTATION.value] if ExifId.ORIENTATION.value in image_info.exif else 1
        if self.orientation == "Rotate 0":
            pass
        elif self.orientation == "Rotate 90 CW":
            self.image = self.image.transpose(Transpose.ROTATE_270)
        elif self.orientation == "Rotate 180":
            self.image = self.image.transpose(Transpose.ROTATE_180)
        elif self.orientation == "Rotate 270 CW":
            self.image = self.image.transpose(Transpose.ROTATE_90)
        else:
            pass

    def close(self):
        if self.image:
            self.image.close()
        if self.watermark_img:
            self.watermark_img.close()

    def save(self, target_path, quality=100):
        if self.orientation == "Rotate 0":
            pass
        elif self.orientation == "Rotate 90 CW":
            self.watermark_img = self.watermark_img.transpose(
                Transpose.ROTATE_90)
        elif self.orientation == "Rotate 180":
            self.watermark_img = self.watermark_img.transpose(
                Transpose.ROTATE_180)
        elif self.orientation == "Rotate 270 CW":
            self.watermark_img = self.watermark_img.transpose(
                Transpose.ROTATE_270)
        else:
            pass

        # if self.watermark_img.mode != 'RGB':
        #     self.watermark_img = self.watermark_img.convert('RGB')

        if 'exif' in self.image.info:
            self.watermark_img.save(target_path, quality=quality, encoding='utf-8',
                                    exif=self.image.info['exif'] if 'exif' in self.image.info else '')
        else:
            self.watermark_img.save(
                target_path, quality=quality, encoding='utf-8')
