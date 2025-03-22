from enum import Enum

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