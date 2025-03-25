import os
import re
from app.utils.logger import setup_logger
from app.entity.enums import ExifId, DISPLAY_TYPE
from datetime import datetime
from dateutil import parser
from app.config import cfg
from app.entity.custom_error import CustomError
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

    # 相机厂商
    def make(self) -> str:
        return extract_attribute(self.exif, ExifId.CAMERA_MAKE.value)

    # 相机型号
    def model(self) -> str:
        return extract_attribute(self.exif, ExifId.CAMERA_MODEL.value)

    # 镜头型号
    def lens_model(self) -> str:
        return extract_attribute(self.exif, *ExifId.LENS_MODEL.value)

    # 镜头厂商
    def lens_make(self) -> str:
        return extract_attribute(self.exif, ExifId.LENS_MAKE.value)

    def parse_exif_info(self, type: str) -> str:
        display: DISPLAY_TYPE = DISPLAY_TYPE.from_str(type)
        if display == DISPLAY_TYPE.MODEL:
            return self.model()
        elif display == DISPLAY_TYPE.LENS_MODEL:
            return self.lens_model()
        elif display == DISPLAY_TYPE.DATE_TIME:
            return self.get_datetime()
        elif display == DISPLAY_TYPE.PARAM:
            return self.get_param_str()
        elif display == DISPLAY_TYPE.LOCATION:
            return self.get_location_str()
        elif display == DISPLAY_TYPE.MAKE:
            return self.make()
        elif display == DISPLAY_TYPE.LENS_MAKE_LENS_MODEL:
            return ' '.join(
                [self.lens_make(), self.lens_model()])
        elif display == DISPLAY_TYPE.CAMERA_MAKE_CAMERA_MODEL:
            return ' '.join(
                [self.make(), self.model()])
        elif display == DISPLAY_TYPE.CAMERA_MODEL_LENS_MODEL:
            return ' '.join(
                [self.model(), self.lens_model()])
        return DEFAULT_VALUE

    def get_focal_length(self):
        focal_length = DEFAULT_VALUE
        focal_length_in_35mm_film = DEFAULT_VALUE

        try:
            focal_lengths = PATTERN.findall(
                extract_attribute(self.exif, ExifId.FOCAL_LENGTH.value))
            if not focal_lengths:
                logger.exception(f"{self.name}: 焦距无法获取")
                return focal_length, focal_length_in_35mm_film
            try:
                focal_length = focal_lengths[0] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.exception(
                    f'{self.name}: ValueError: 不存在焦距：{focal_lengths} : {e}')
            try:
                focal_length_in_35mm_film: str = focal_lengths[1] if focal_length else DEFAULT_VALUE
            except IndexError as e:
                logger.exception(
                    f'{self.name}: ValueError: 不存在 35mm 焦距：{focal_lengths} : {e}')
        except Exception as e:
            logger.exception(
                f'{self.name}: KeyError: 焦距转换错误：{extract_attribute(self.exif, ExifId.FOCAL_LENGTH.value)} : {e}')
            raise CustomError("焦距信息获取失败", 405)

        return focal_length, focal_length_in_35mm_film

    def get_datetime(self) -> str:
        dt = datetime.now()
        try:
            dt = parser.parse(extract_attribute(self.exif, ExifId.DATETIME.value,
                                                default_value=str(datetime.now())))
        except ValueError as e:
            logger.exception(
                f'{self.name}: Error: 时间格式错误：{extract_attribute(self.exif, ExifId.DATETIME.value)}')
            raise CustomError("时间格式获取失败", 406)
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

    def get_location_str(self) -> str:
        # GPS 信息
        if 'GPSPosition' in self.exif:
            return str.join(' ', self.extract_gps_info(self.exif.get('GPSPosition')))
        elif 'GPSLatitude' in self.exif and 'GPSLongitude' in self.exif:
            return str.join(' ', self.extract_gps_lat_and_long((self.exif.get('GPSLatitude'),
                                                                self.exif.get('GPSLongitude'))))
        else:
            return '无'

    def extract_gps_lat_and_long(self, lat: str, long: str) -> str:
        # 提取出纬度和经度主要部分
        lat_deg, _, lat_min = re.findall(r"(\d+ deg \d+)", lat)[0].split()
        long_deg, _, long_min = re.findall(r"(\d+ deg \d+)", long)[0].split()

        # 提取出方向（北 / 南 / 东 / 西）
        lat_dir = re.findall(r"([NS])", lat)[0]
        long_dir = re.findall(r"([EW])", long)[0]

        latitude = f"{lat_deg}°{lat_min}'{lat_dir}"
        longitude = f"{long_deg}°{long_min}'{long_dir}"

        return latitude, longitude

    def extract_gps_info(self, gps_info: str) -> str:
        lat, long = gps_info.split(", ")
        return self.extract_gps_lat_and_long(lat, long)
