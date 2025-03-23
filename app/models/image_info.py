import os
import re
from PyQt5.QtCore import QObject
from app.utils.logger import setup_logger
from app.entity.exif_id import ExifId
from datetime import datetime
from dateutil import parser
from app.config import cfg
from app.utils.image_handle import get_exif, extract_attribute
logger = setup_logger("image_info")

DEFAULT_VALUE = '--'
PATTERN = re.compile(r"(\d+)\.")  # 匹配小数


class ImageInfo(object):
    name: str
    path: str
    exif: dict

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.exif = get_exif(path)

    def logo(self) -> str:
        return extract_attribute(
            self.exif, ExifId.CAMERA_MAKE.value)

    def parse_exif_info(self, type: str) -> str:
        if type == "Model":
            return extract_attribute(self.exif, ExifId.CAMERA_MODEL.value)
        elif type == "LensModel":
            return extract_attribute(self.exif, *ExifId.LENS_MODEL.value)
        elif type == "Datetime":
            return self.get_datetime()
        elif type == "Param":
            return self.get_param_str()

    def get_focal_length(self):
        focal_length = DEFAULT_VALUE
        focal_length_in_35mm_film = DEFAULT_VALUE

        try:
            focal_lengths = PATTERN.findall(
                extract_attribute(self.exif, ExifId.FOCAL_LENGTH.value))
            if not focal_lengths:
                logger.error(f"{self.name}: 焦距无法获取")
                return focal_length, focal_length_in_35mm_film
            try:
                focal_length = focal_lengths[0] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.error(
                    f'{self.name}: ValueError: 不存在焦距：{focal_lengths} : {e}')
            try:
                focal_length_in_35mm_film: str = focal_lengths[1] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.error(
                    f'{self.name}: ValueError: 不存在 35mm 焦距：{focal_lengths} : {e}')
        except Exception as e:
            logger.error(
                f'{self.name}: KeyError: 焦距转换错误：{extract_attribute(self.exif, ExifId.FOCAL_LENGTH.value)} : {e}')

        return focal_length, focal_length_in_35mm_film

    def get_datetime(self) -> str:
        dt = datetime.now()
        try:
            dt = parser.parse(extract_attribute(self.exif, ExifId.DATETIME.value,
                                                default_value=str(datetime.now())))
        except ValueError as e:
            logger.error(
                f'{self.name}: Error: 时间格式错误：{extract_attribute(self.exif, ExifId.DATETIME.value)}')
        return datetime.strftime(dt, '%Y-%m-%d %H:%M')

    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        self.focal_length, self.focal_length_in_35mm_film = self.get_focal_length()
        focal_length = self.focal_length_in_35mm_film if cfg.useEquivalentFocal.value else self.focal_length
        f_number: str = extract_attribute(
            self.exif, ExifId.F_NUMBER.value, default_value=DEFAULT_VALUE)
        exposure_time: str = extract_attribute(self.exif, ExifId.EXPOSURE_TIME.value, default_value=DEFAULT_VALUE,
                                               suffix='s')
        iso: str = extract_attribute(
            self.exif, ExifId.ISO.value, default_value=DEFAULT_VALUE)
        return '  '.join([str(focal_length) + 'mm', 'f/' + f_number, exposure_time,
                          'ISO' + str(iso)])
