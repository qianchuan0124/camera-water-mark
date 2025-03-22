from PyQt5.QtCore import QThread, pyqtSignal
from dataclasses import dataclass
from pathlib import Path
from app.config import cfg, RESOURCE_PATH, LOGO_PATH

from PIL import Image, ImageOps, ImageFont
from PIL.Image import Transpose
from dateutil import parser
from datetime import datetime
import re
from app.entity.exif_id import ExifId
from app.utils.image_handle import get_exif, text_to_image, concatenate_image, padding_image, append_image_by_side, resize_image_with_width, extract_attribute

from app.utils.logger import setup_logger
logger = setup_logger("image_handle_thread")


NORMAL_HEIGHT = 1000
FONT = Path(f"{RESOURCE_PATH}/fonts/AlibabaPuHuiTi-2-45-Light.otf")
BOLD_FONT = Path(f"{RESOURCE_PATH}/fonts/AlibabaPuHuiTi-2-85-Bold.otf")
TRANSPARENT = (0, 0, 0, 0)
GRAY = '#CBCBC9'
LINE_TRANSPARENT = Image.new('RGBA', (20, 1000), color=TRANSPARENT)
LINE_GRAY = Image.new('RGBA', (20, 1000), color=GRAY)
DEFAULT_VALUE = '--'
PATTERN = re.compile(r"(\d+)\.")  # 匹配小数

@dataclass
class ImageHandleTask:
    image_path: Path
    target_path: Path

class ImageHandleThread(QThread):
    finished = pyqtSignal(str)
    loading = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, task: ImageHandleTask):
        super().__init__()
        self.task = task
        self.image: Image.Image = Image.open(self.task.image_path)
        self.exif: dict = get_exif(self.task.image_path)
        self.watermark_img = None
        self.fix_orientation()
        self._logos = {}

    def get_ratio(self):
        return self.image.width / self.image.height
    
    def get_font(self):
        return ImageFont.truetype(FONT, self.get_font_size())
    
    def get_font_size(self):
        font_size = cfg.baseFontSize.value
        if font_size == 1:
            return 240
        elif font_size == 2:
            return 250
        elif font_size == 3:
            return 300
        else:
            return 240
    
    def get_bold_font(self):
        return ImageFont.truetype(BOLD_FONT, self.get_bold_font_size())
    
    def get_bold_font_size(self):
        font_size = cfg.boldFontSize.value
        if font_size == 1:
            return 260
        elif font_size == 2:
            return 290
        elif font_size == 3:
            return 320
        else:
            return 260
    
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

    def load_logo(self, make:str) -> Image.Image:
        """
        根据厂商获取 logo
        :param make: 厂商
        :return: logo
        """
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
    
    def parse_exif_info(self, type: str) -> str:
        if type == "Model":
            return extract_attribute(self.exif, ExifId.CAMERA_MODEL.value)
        elif type == "LensModel":
            return extract_attribute(self.exif, *ExifId.LENS_MODEL.value)
        elif type == "Datetime":
            return self.get_datetime(self.exif)
        elif type == "Param":
            return self.get_param_str()
        
    def get_datetime(self, exif) -> str:
        dt = datetime.now()
        try:
            dt = parser.parse(extract_attribute(exif, ExifId.DATETIME.value,
                                                default_value=str(datetime.now())))
        except ValueError as e:
            logger.info(f'Error: 时间格式错误：{extract_attribute(exif, ExifId.DATETIME.value)}')
        return datetime.strftime(dt, '%Y-%m-%d %H:%M')
    
    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        self.focal_length, self.focal_length_in_35mm_film = self.get_focal_length(self.exif)
        focal_length = self.focal_length_in_35mm_film if cfg.useEquivalentFocal.value else self.focal_length
        f_number: str = extract_attribute(self.exif, ExifId.F_NUMBER.value, default_value=DEFAULT_VALUE)
        exposure_time: str = extract_attribute(self.exif, ExifId.EXPOSURE_TIME.value, default_value=DEFAULT_VALUE,
                                                    suffix='s')
        iso: str = extract_attribute(self.exif, ExifId.ISO.value, default_value=DEFAULT_VALUE)
        return '  '.join([str(focal_length) + 'mm', 'f/' + f_number, exposure_time,
                          'ISO' + str(iso)])
    
    def get_focal_length(self, exif):
        focal_length = DEFAULT_VALUE
        focal_length_in_35mm_film = DEFAULT_VALUE

        try:
            focal_lengths = PATTERN.findall(extract_attribute(exif, ExifId.FOCAL_LENGTH.value))
            try:
                focal_length = focal_lengths[0] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.info(
                    f'ValueError: 不存在焦距：{focal_lengths} : {e}')
            try:
                focal_length_in_35mm_film: str = focal_lengths[1] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.info(f'ValueError: 不存在 35mm 焦距：{focal_lengths} : {e}')
        except Exception as e:
            logger.info(f'KeyError: 焦距转换错误：{extract_attribute(exif, ExifId.FOCAL_LENGTH.value)} : {e}')

        return focal_length, focal_length_in_35mm_film


    def run(self):
        self.bg_color = cfg.backgroundColor.value

        # 下方水印的占比
        ratio = (.04 if self.get_ratio() >= 1 else .09) + 0.02 * cfg.get_font_padding_level()
        # 水印中上下边缘空白部分的占比
        padding_ratio = (.52 if self.get_ratio() >= 1 else .7) - 0.04 * cfg.get_font_padding_level()

        # 创建一个空白的水印图片
        watermark = Image.new('RGBA', (int(NORMAL_HEIGHT / ratio), NORMAL_HEIGHT), color=self.bg_color)

        with Image.new('RGBA', (10, 100), color=self.bg_color) as empty_padding:
            # 填充左边的文字内容
            left_top = text_to_image(self.parse_exif_info(cfg.leftTopType.value),
                                     self.get_font(),
                                     self.get_bold_font(),
                                     is_bold=cfg.leftTopBold.value,
                                     fill=cfg.leftTopFontColor.value)
            left_bottom = text_to_image(self.parse_exif_info(cfg.leftBottomType.value),
                                        self.get_font(),
                                        self.get_bold_font(),
                                        is_bold=cfg.leftBottomBold.value,
                                        fill=cfg.leftBottomFontColor.value)
            left = concatenate_image([left_top, empty_padding, left_bottom])
            # 填充右边的文字内容
            right_top = text_to_image(self.parse_exif_info(cfg.rightTopType.value),
                                      self.get_font(),
                                      self.get_bold_font(),
                                      is_bold=cfg.rightTopBold.value,
                                      fill=cfg.rightTopFontColor.value)
            right_bottom = text_to_image(self.parse_exif_info(cfg.rightBottomType.value),
                                         self.get_font(),
                                         self.get_bold_font(),
                                         is_bold=cfg.rightBottomBold.value,
                                         fill=cfg.rightBottomFontColor.value)
            right = concatenate_image([right_top, empty_padding, right_bottom])

        # 将左右两边的文字内容等比例缩放到相同的高度
        max_height = max(left.height, right.height)
        left = padding_image(left, int(max_height * padding_ratio), 'tb')
        right = padding_image(right, int(max_height * padding_ratio), 't')
        right = padding_image(right, left.height - right.height, 'b')

        logo = self.load_logo(extract_attribute(self.exif, ExifId.CAMERA_MAKE.value))
        if cfg.logoEnable.value:
            if cfg.isLogoLeft.value:
                # 如果 logo 在左边
                line = LINE_TRANSPARENT.copy()
                logo = padding_image(logo, int(padding_ratio * logo.height))
                append_image_by_side(watermark, [line, logo, left], is_start=logo is None)
                append_image_by_side(watermark, [right], side='right')
            else:
                # 如果 logo 在右边
                if logo is not None:
                    # 如果 logo 不为空，等比例缩小 logo
                    logo = padding_image(logo, int(padding_ratio * logo.height))
                    # 插入一根线条用于分割 logo 和文字
                    line = padding_image(LINE_GRAY, int(padding_ratio * LINE_GRAY.height * .8))
                else:
                    line = LINE_TRANSPARENT.copy()
                append_image_by_side(watermark, [left], is_start=True)
                append_image_by_side(watermark, [logo, line, right], side='right')
                line.close()
        else:
            append_image_by_side(watermark, [left], is_start=True)
            append_image_by_side(watermark, [right], side='right')
        left.close()
        right.close()

        # 缩放水印的大小
        watermark = resize_image_with_width(watermark, self.get_width())
        # 将水印图片放置在原始图片的下方
        bg = ImageOps.expand(self.get_watermark_img().convert('RGBA'),
                             border=(0, 0, 0, watermark.height),
                             fill=self.bg_color)
        fg = ImageOps.expand(watermark, border=(0, self.get_height(), 0, 0), fill=TRANSPARENT)
        result = Image.alpha_composite(bg, fg)
        watermark.close()
        # 更新图片对象
        result = ImageOps.exif_transpose(result).convert('RGB')
        self.update_watermark_img(result)

        self.save(self.task.target_path, quality=cfg.baseQuality.value)
        self.close()
        self.finished.emit(str(self.task.target_path))


    def fix_orientation(self):
        self.orientation = self.exif[ExifId.ORIENTATION.value] if ExifId.ORIENTATION.value in self.exif else 1
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
        self.image.close()
        self.watermark_img.close()

    def save(self, target_path, quality=100):
        if self.orientation == "Rotate 0":
            pass
        elif self.orientation == "Rotate 90 CW":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_90)
        elif self.orientation == "Rotate 180":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_180)
        elif self.orientation == "Rotate 270 CW":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_270)
        else:
            pass

        if self.watermark_img.mode != 'RGB':
            self.watermark_img = self.watermark_img.convert('RGB')

        if 'exif' in self.image.info:
            self.watermark_img.save(target_path, quality=quality, encoding='utf-8',
                                    exif=self.image.info['exif'] if 'exif' in self.image.info else '')
        else:
            self.watermark_img.save(target_path, quality=quality, encoding='utf-8')


