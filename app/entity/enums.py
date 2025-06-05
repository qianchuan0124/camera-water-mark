from typing import List, Dict, TypeVar, Type
from enum import Enum
from typing import List, TypeVar, Type, Dict, Tuple

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


E = TypeVar('T', bound='ExifId')


class ExifId(Enum):
    CAMERA_MODEL = 'CameraModelName'
    CAMERA_MAKE = 'Make'
    LENS_MODEL = 'LensModel'
    LENS_MAKE = 'LensMake'
    DATETIME = 'DateTimeOriginal'
    FOCAL_LENGTH = 'FocalLength'
    FOCAL_LENGTH_IN_35MM_FILM = 'FocalLengthIn35mmFormat'
    F_NUMBER = 'FNumber'
    ISO = 'ISO'
    EXPOSURE_TIME = 'ExposureTime'
    SHUTTER_SPEED_VALUE = 'ShutterSpeedValue'
    ORIENTATION = 'Orientation'

    @staticmethod
    def lens_models() -> Tuple[str, str, str]:
        """返回镜头标签元组，以匹配 *value 的行为"""
        return ('LensModel', 'Lens', 'LensID')
    
    @staticmethod
    def update_model_info() -> str:
        return "Model"

    # 描述映射（类方法实现）
    @classmethod
    def _get_desc_map(cls) -> Dict[str, str]:
        return {
            cls.CAMERA_MODEL.value: "相机型号",
            cls.CAMERA_MAKE.value: "相机厂商",
            cls.LENS_MODEL.value: "镜头型号",
            cls.LENS_MAKE.value: "镜头厂商",
            cls.DATETIME.value: "拍摄时间",
            cls.FOCAL_LENGTH.value: "拍摄焦距",
            cls.FOCAL_LENGTH_IN_35MM_FILM.value: "等效焦距",
            cls.F_NUMBER.value: "光圈大小",
            cls.ISO.value: "拍摄ISO",
            cls.EXPOSURE_TIME.value: "曝光时间",
            cls.SHUTTER_SPEED_VALUE.value: "快门时间",
            cls.ORIENTATION.value: "旋转参数",
        }

    def ex_description(self) -> str:
        """获取当前枚举值的描述"""
        return self._get_desc_map()[self.value]

    @classmethod
    def all_descriptions(cls) -> List[str]:
        """获取所有枚举值的描述列表"""
        desc_map = cls._get_desc_map()
        return [desc_map[member.value] for member in cls]

    @classmethod
    def display_values(cls) -> List[E]:
        """获取除需要展示的所有枚举值"""
        return [member for member in cls if member != cls.ORIENTATION and member != cls.FOCAL_LENGTH_IN_35MM_FILM and member != cls.SHUTTER_SPEED_VALUE]

    def update_value(self) -> str:
        if self == ExifId.CAMERA_MODEL:
            return ExifId.update_model_info()
        else:
            return self.value

    def default_value(self) -> str:
        """获取当前枚举值的描述"""
        if self == ExifId.CAMERA_MODEL:
            return "例如: Nikon 30"
        elif self == ExifId.CAMERA_MAKE:
            return self.make_tips()
        elif self == ExifId.LENS_MODEL:
            return "例如: Nikkor 24-70 f/2.8"
        elif self == ExifId.LENS_MAKE:
            return "例如: Nikkor"
        elif self == ExifId.DATETIME:
            return "例如: 2025-01-01 12:00"
        elif self == ExifId.FOCAL_LENGTH:
            return "例如: 50mm"
        elif self == ExifId.F_NUMBER:
            return "例如: 1.8"
        elif self == ExifId.ISO:
            return "例如: ISO 100"
        elif self == ExifId.EXPOSURE_TIME:
            return "例如: 1/1000s"
        else:
            return "--"

    def make_tips(self):
        return """
        目前支持的厂商:
        苹果: apple
        佳能: canon
        尼康: nikon
        富士: fujifilm
        索尼: sony
        徕卡: leica
        奥林巴斯: olympus
        宾得: pentax
        大疆: DJI
        哈苏: hasselblad
        理光: ricoh
        松下: panasonic

        注意大小写,不支持的厂商将使用默认的logo图标。
        """


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
    NONE = "None"

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
            cls.CAMERA_MODEL_LENS_MODEL.value: "相机型号 + 镜头型号",
            cls.NONE.value: "不展示"
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
            "相机型号 + 镜头型号": cls.CAMERA_MODEL_LENS_MODEL,
            "不展示": cls.NONE
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
