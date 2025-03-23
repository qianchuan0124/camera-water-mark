
import subprocess
import platform
import shutil
import re

from app.utils.logger import setup_logger
from app.config import EXIFTOOL_PATH
from datetime import datetime
from pathlib import Path
from dateutil import parser
from app.entity.exif_id import ExifId
from PIL import Image, ImageOps, ImageDraw
from app.entity.constants import TRANSPARENT

logger = setup_logger("image_handle")


def exiftool_command() -> Path:
    if platform.system() == 'Windows':
        return Path(f"{EXIFTOOL_PATH}/exiftool.exe")
    elif shutil.which('exiftool'):
        return Path(shutil.which('exiftool'))
    else:
        return Path(f"{EXIFTOOL_PATH}/exiftool")


def get_exif(path) -> dict:
    """
    获取exif信息
    :param path: 照片路径
    :return: exif信息
    """
    exif_dict = {}
    try:
        print(exiftool_command())
        output_bytes = subprocess.check_output(
            [exiftool_command(), '-d', '%Y-%m-%d %H:%M:%S%3f%z', path])
        output = output_bytes.decode('utf-8', errors='ignore')

        lines = output.splitlines()
        utf8_lines = [line for line in lines]

        for line in utf8_lines:
            # 将每一行按冒号分隔成键值对
            kv_pair = line.split(':')
            if len(kv_pair) < 2:
                continue
            key = kv_pair[0].strip()
            value = ':'.join(kv_pair[1:]).strip()
            # 将键中的空格移除
            key = re.sub(r'\s+', '', key)
            key = re.sub(r'/', '', key)
            # 将键值对添加到字典中
            exif_dict[key] = value
        for key, value in exif_dict.items():
            # 过滤非 ASCII 字符
            value_clean = ''.join(c for c in value if ord(c) < 128)
            # 将处理后的值更新到 exif_dict 中
            exif_dict[key] = value_clean
    except Exception as e:
        logger.error(f'get_exif error: {path} : {e}')

    return exif_dict


def extract_attribute(data_dict: dict, *keys, default_value: str = '', prefix='', suffix='') -> str:
    """
    从字典中提取对应键的属性值

    :param data_dict: 包含属性值的字典
    :param keys: 一个或多个键
    :param default_value: 默认值，默认为空字符串
    :return: 对应的属性值或空字符串
    """
    for key in keys:
        if key in data_dict:
            return data_dict[key] + suffix
    return default_value


def get_datetime(exif) -> datetime:
    dt = datetime.now()
    try:
        dt = parser.parse(extract_attribute(exif, ExifId.DATETIME.value,
                                            default_value=str(datetime.now())))
    except ValueError as e:
        logger.info(
            f'Error: 时间格式错误：{extract_attribute(exif, ExifId.DATETIME.value)}')
    return dt


DEFAULT_VALUE = '--'
PATTERN = re.compile(r"(\d+)\.")  # 匹配小数


def get_focal_length(exif):
    focal_length = DEFAULT_VALUE
    focal_length_in_35mm_film = DEFAULT_VALUE

    try:
        focal_lengths = PATTERN.findall(
            extract_attribute(exif, ExifId.FOCAL_LENGTH.value))
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
        logger.info(
            f'KeyError: 焦距转换错误：{extract_attribute(exif, ExifId.FOCAL_LENGTH.value)} : {e}')

    return focal_length, focal_length_in_35mm_film


# 获取经纬度信息
def extract_gps_info(gps_info: str):
    lat, long = gps_info.split(", ")
    return extract_gps_lat_and_long(lat, long)

# 提取出纬度和经度主要部分


def extract_gps_lat_and_long(lat: str, long: str):
    lat_deg, _, lat_min = re.findall(r"(\d+ deg \d+)", lat)[0].split()
    long_deg, _, long_min = re.findall(r"(\d+ deg \d+)", long)[0].split()

    # 提取出方向（北 / 南 / 东 / 西）
    lat_dir = re.findall(r"([NS])", lat)[0]
    long_dir = re.findall(r"([EW])", long)[0]

    latitude = f"{lat_deg}°{lat_min}'{lat_dir}"
    longitude = f"{long_deg}°{long_min}'{long_dir}"

    return latitude, longitude


# 计算像素总数
def calculate_pixel_count(width: int, height: int) -> str:
    pixel_count = width * height
    # 计算百万像素数
    megapixel_count = pixel_count / 1000000.0
    # 返回结果字符串
    return f"{megapixel_count:.2f} MP"


def append_image_by_side(background, images, side='left', padding=200, is_start=False):
    """
    将图片横向拼接到背景图片中
    :param background: 背景图片对象
    :param images: 图片对象列表
    :param side: 拼接方向，left/right
    :param padding: 图片之间的间距
    :param is_start: 是否在最左侧添加 padding
    :return: 拼接后的图片对象
    """
    if 'right' == side:
        if is_start:
            x_offset = background.width - padding
        else:
            x_offset = background.width
        images.reverse()
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(
                i, background.height, auto_close=False)
            x_offset -= i.width
            x_offset -= padding
            background.paste(i, (x_offset, 0))
    else:
        if is_start:
            x_offset = padding
        else:
            x_offset = 0
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(
                i, background.height, auto_close=False)
            background.paste(i, (x_offset, 0))
            x_offset += i.width
            x_offset += padding


def resize_image_with_height(image, height, auto_close=True):
    """
    按照高度对图片进行缩放
    :param image: 图片对象
    :param height: 指定高度
    :return: 按照高度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    width, old_height = image.size

    # 计算缩放后的宽度
    scale = height / old_height
    new_width = round(width * scale)

    # 进行等比缩放
    resized_image = image.resize((new_width, height), Image.LANCZOS)

    # 关闭图片对象
    if auto_close:
        image.close()

    # 返回缩放后的图片对象
    return resized_image


def concatenate_image(images, align='left'):
    """
    将多张图片拼接成一列
    :param images: 图片对象列表
    :param align: 对齐方向，left/center/right
    :return: 拼接后的图片对象
    """
    widths, heights = zip(*(i.size for i in images))

    sum_height = sum(heights)
    max_width = max(widths)

    new_img = Image.new('RGBA', (max_width, sum_height), color=TRANSPARENT)

    x_offset = 0
    y_offset = 0
    if 'left' == align:
        for img in images:
            new_img.paste(img, (0, y_offset))
            y_offset += img.height
    elif 'center' == align:
        for img in images:
            x_offset = int((max_width - img.width) / 2)
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    elif 'right' == align:
        for img in images:
            x_offset = max_width - img.width  # 右对齐
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    return new_img


def merge_images(images, axis=0, align=0):
    """
    拼接多张图片
    :param images: 图片对象列表
    :param axis: 0 水平拼接，1 垂直拼接
    :param align: 0 居中对齐，1 底部/右对齐，2 顶部/左对齐
    :return: 拼接后的图片对象
    """
    # 获取每张图像的 size
    widths, heights = zip(*(img.size for img in images))

    # 计算输出图像的尺寸
    if axis == 0:  # 水平拼接
        total_width = sum(widths)
        max_height = max(heights)
    else:  # 垂直拼接
        total_width = max(widths)
        max_height = sum(heights)

    # 创建输出图像
    output_image = Image.new(
        'RGBA', (total_width, max_height), color=TRANSPARENT)

    # 拼接图像
    x_offset, y_offset = 0, 0
    for img in images:
        if axis == 0:  # 水平拼接
            if align == 1:  # 底部对齐
                y_offset = max_height - img.size[1]
            elif align == 2:  # 顶部对齐
                y_offset = 0
            else:  # 居中排列
                y_offset = (max_height - img.size[1]) // 2
            output_image.paste(img, (x_offset, y_offset))
            x_offset += img.size[0]
        else:  # 垂直拼接
            if align == 1:  # 右对齐
                x_offset = total_width - img.size[0]
            elif align == 2:  # 左对齐
                x_offset = 0
            else:  # 居中排列
                x_offset = (total_width - img.size[0]) // 2
            output_image.paste(img, (x_offset, y_offset))
            y_offset += img.size[1]

    return output_image


def padding_image(image, padding_size, padding_location='tb', color=TRANSPARENT) -> Image.Image:
    """
    在图片四周填充白色像素
    :param image: 图片对象
    :param padding_size: 填充像素大小
    :param padding_location: 填充位置，top/bottom/left/right
    :return: 填充白色像素后的图片对象
    """
    if image is None:
        return None

    total_width, total_height = image.size
    x_offset, y_offset = 0, 0
    if 't' in padding_location:
        total_height += padding_size
        y_offset += padding_size
    if 'b' in padding_location:
        total_height += padding_size
    if 'l' in padding_location:
        total_width += padding_size
        x_offset += padding_size
    if 'r' in padding_location:
        total_width += padding_size

    padding_img = Image.new('RGBA', (total_width, total_height), color=color)
    padding_img.paste(image, (x_offset, y_offset))
    return padding_img


def resize_image_with_width(image, width, auto_close=True):
    """
    按照宽度对图片进行缩放
    :param image: 图片对象
    :param width: 指定宽度
    :return: 按照宽度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    old_width, height = image.size

    # 计算缩放后的宽度
    scale = width / old_width
    new_height = round(height * scale)

    # 进行等比缩放
    resized_image = image.resize((width, new_height), Image.LANCZOS)

    # 关闭图片对象
    if auto_close:
        image.close()

    # 返回缩放后的图片对象
    return resized_image


def square_image(image, auto_close=True) -> Image.Image:
    """
    将图片按照正方形进行填充
    :param auto_close: 是否自动关闭图片对象
    :param image: 图片对象
    :return: 填充后的图片对象
    """
    # 计算图片的宽度和高度
    width, height = image.size
    if width == height:
        return image

    # 计算需要填充的白色区域大小
    delta_w = abs(width - height)
    padding = (delta_w // 2, 0) if width < height else (0, delta_w // 2)

    square_img = ImageOps.expand(image, padding, fill='white')

    if auto_close:
        image.close()

    # 返回正方形图片对象
    return square_img


def text_to_image(content, font, bold_font, is_bold=False, fill='black') -> Image.Image:
    """
    将文字内容转换为图片
    """
    if is_bold:
        font = bold_font
    if content == '':
        content = '   '
    _, _, text_width, text_height = font.getbbox(content)
    image = Image.new('RGBA', (text_width, text_height), color=TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), content, fill=fill, font=font)
    return image


def extract_attribute(data_dict: dict, *keys, default_value: str = '', prefix='', suffix='') -> str:
    """
    从字典中提取对应键的属性值

    :param data_dict: 包含属性值的字典
    :param keys: 一个或多个键
    :param default_value: 默认值，默认为空字符串
    :return: 对应的属性值或空字符串
    """
    for key in keys:
        if key in data_dict:
            return data_dict[key] + suffix
    return default_value
