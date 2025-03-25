from typing import List, Dict, TypeVar, Type
from enum import Enum
from typing import List, TypeVar, Type, Dict

# 支持处理的图片类型格式


class SupportedImageFormats(Enum):
    """支持的图片格式"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"

# LOGO布局样式


class LOGO_LAYOUT(Enum):
    LEFT = "LOGO居左"
    RIGHT = "LOGO居右"

    def get_enum(value):
        for member in LOGO_LAYOUT:
            if member.value == value:
                return member
        return LOGO_LAYOUT.LEFT

    def isLeft(self):
        return self == LOGO_LAYOUT.LEFT

    def all_values():
        values = [member.value for member in LOGO_LAYOUT]
        return values

# 水印展示样式


class MARK_MODE(Enum):
    STANDARD = "标准模式"
    SIMPLE = "简易模式"

    def get_enum(value):
        for member in MARK_MODE:
            if member.value == value:
                return member
        return MARK_MODE.STANDARD

    def info(self):
        if self == MARK_MODE.SIMPLE:
            return "simple"
        else:
            return "standard"

    def key(value):
        if value == "simple":
            return MARK_MODE.SIMPLE
        else:
            return MARK_MODE.STANDARD

    def all_values():
        values = [member.value for member in MARK_MODE]
        return values

    def isSimple(self):
        return self == MARK_MODE.SIMPLE


class ExifId(Enum):
    CAMERA_MODEL = 'CameraModelName'
    CAMERA_MAKE = 'Make'
    LENS_MODEL = ['LensModel', 'Lens', 'LensID']
    LENS_MAKE = 'LensMake'
    DATETIME = 'DateTimeOriginal'
    FOCAL_LENGTH = 'FocalLength'
    FOCAL_LENGTH_IN_35MM_FILM = 'FocalLengthIn35mmFormat'
    F_NUMBER = 'FNumber'
    ISO = 'ISO'
    EXPOSURE_TIME = 'ExposureTime'
    SHUTTER_SPEED_VALUE = 'ShutterSpeedValue'
    ORIENTATION = 'Orientation'

# 水印展示类型


T = TypeVar('T', bound='DISPLAY_TYPE')


class DISPLAY_TYPE(Enum):
    MODEL = "Model"
    MAKE = "Make"
    LENS_MODEL = "LensModel"
    DATE_TIME = "Datetime"
    PARAM = "Param"
    LOCATION = "Location"
    LENS_MAKE_LENS_MODEL = "LensMake_LensModel"
    CAMERA_MODEL_LENS_MODEL = "CameraModel_LensModel"
    CAMERA_MAKE_CAMERA_MODEL = "CameraMake_CameraModel"

    # 描述映射（类方法实现）
    @classmethod
    def _get_desc_map(cls) -> Dict[str, str]:
        return {
            cls.MODEL.value: "相机型号",
            cls.MAKE.value: "相机厂商",
            cls.LENS_MODEL.value: "镜头型号",
            cls.DATE_TIME.value: "拍摄时间",
            cls.PARAM.value: "拍摄参数",
            cls.LOCATION.value: "地理位置",
            cls.LENS_MAKE_LENS_MODEL.value: "镜头厂商 + 镜头型号",
            cls.CAMERA_MAKE_CAMERA_MODEL.value: "相机厂商 + 相机型号",
            cls.CAMERA_MODEL_LENS_MODEL.value: "相机型号 + 镜头型号"
        }

    @classmethod
    def _get_reverse_desc_map(cls) -> Dict[str, 'DISPLAY_TYPE']:
        return {
            "相机型号": cls.MODEL,
            "相机厂商": cls.MAKE,
            "镜头型号": cls.LENS_MODEL,
            "拍摄时间": cls.DATE_TIME,
            "拍摄参数": cls.PARAM,
            "地理位置": cls.LOCATION,
            "镜头厂商 + 镜头型号": cls.LENS_MAKE_LENS_MODEL,
            "相机厂商 + 相机型号": cls.CAMERA_MAKE_CAMERA_MODEL,
            "相机型号 + 镜头型号": cls.CAMERA_MODEL_LENS_MODEL
        }

    @property
    def description(self) -> str:
        """获取当前枚举值的描述"""
        return self._get_desc_map()[self.value]

    @classmethod
    def from_desc(cls: Type[T], desc: str) -> T:
        """通过中文描述获取枚举"""
        return cls._get_reverse_desc_map().get(desc, cls.MODEL)

    @classmethod
    def from_str(cls: Type[T], value: str) -> T:
        """通过枚举值字符串获取枚举"""
        try:
            return cls(value.strip())
        except ValueError:
            # 大小写不敏感匹配
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            raise ValueError(f"'{value}' 不是有效的 {cls.__name__}")

    @classmethod
    def all_descriptions(cls) -> List[str]:
        """获取所有枚举值的描述列表"""
        desc_map = cls._get_desc_map()
        return [desc_map[member.value] for member in cls]
