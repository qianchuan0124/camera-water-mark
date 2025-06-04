from app.config import cfg
from PIL import Image, ImageDraw, ImageFilter
from app.entity.custom_error import CustomError
from app.utils.image_handle import hex_to_rgba, padding_image

from app.utils.logger import setup_logger
logger = setup_logger("image_render")

GAUSSIAN_KERNEL_RADIUS = 35
PADDING_PERCENT_IN_BACKGROUND = 0.18


def raduis() -> int:
    return max(100 - int(cfg.radiusInfo.value), 1)


def add_background_blur(img: Image.Image, bottom_padding=0) -> Image.Image:
    """给图片添加模糊背景效果
    参数:
        img: 输入图片(支持任意格式)
    返回:
        带模糊背景的RGB格式图片
    """
    try:
        # 转换为RGB确保无alpha通道
        bg = img.convert('RGB')

        # 应用高斯模糊
        bg = bg.filter(ImageFilter.GaussianBlur(GAUSSIAN_KERNEL_RADIUS))

        # 调整亮度
        white = Image.new('RGB', bg.size, (255, 255, 255))
        bg = Image.blend(bg, white, 0.1)

        # 扩展尺寸
        new_size = (
            int(img.width * (1 + PADDING_PERCENT_IN_BACKGROUND)),
            int(img.height * (1 + PADDING_PERCENT_IN_BACKGROUND) + bottom_padding)
        )
        blurred_bg = bg.resize(new_size)
        foreground = add_rounded_corners(img)

        # 计算居中位置
        x_offset = int((blurred_bg.width - foreground.width) / 2)
        y_offset = int(
            (blurred_bg.height - bottom_padding - foreground.height) / 2)

        # 创建结果画布
        result = blurred_bg.convert("RGBA")

        # 粘贴前景图（使用alpha通道）
        result.paste(foreground, (x_offset, y_offset), foreground)
        return result
    except Exception as e:
        logger.exception(f"增加模糊背景出错, error:{str(e)}")
        raise CustomError("增加模糊背景出错", 404)


def add_white_margin(img: Image.Image) -> Image.Image:
    """给图片添加白色边距效果
    参数:
        img: 输入图片(支持任意格式)
    返回:
        带白色边距的RGB格式图片
    """
    try:
        padding_size = int(cfg.whiteMarginWidth.value *
                           min(img.width, img.height) / 100)
        padding_img = padding_image(
            img, padding_size, 'tlrb', color=hex_to_rgba(cfg.backgroundColor.value))
        return padding_img
    except Exception as e:
        logger.exception(f"增加边距错误, error:{str(e)}")
        raise CustomError("增加边距错误", 403)


def add_shadow(img: Image.Image) -> Image.Image:
    """添加可见的圆角阴影效果
    Args:
        img: 输入图片
        corner_radius: 圆角半径(像素)
    Returns:
        带明显阴影效果的圆角图片(RGBA)
    """
    try:
        shadow_blur: int = 20
        shadow_color: tuple = (40, 40, 40, 180)
        corner_radius = min(img.width, img.height) // raduis()

        padding = shadow_blur * 2
        shadow_size = (img.width + padding, img.height + padding)

        # 创建阴影层
        shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        draw.rounded_rectangle(
            [(shadow_blur, shadow_blur),
             (img.width + shadow_blur, img.height + shadow_blur)],
            radius=corner_radius,
            fill=shadow_color
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))

        # 合成图片
        result = Image.new("RGBA", shadow_size, (255, 255, 255, 255))
        result.paste(shadow, (0, 0), shadow)
        result.paste(img, (shadow_blur//2, shadow_blur//2), img)
        return result
    except Exception as e:
        logger.exception(f"增加阴影出错, error:{str(e)}")
        raise CustomError("增加阴影出错", 402)


def add_rounded_corners(img: Image.Image) -> Image.Image:
    """给图片添加白色背景的圆角效果
    参数:
        img: 输入图片(支持任意格式)
    返回:
        带白色背景圆角的RGB格式图片
    """
    try:
        radius = min(img.width, img.height) // raduis()
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        img.putalpha(mask)
        return img
    except Exception as e:
        logger.exception(f"添加圆角出错, error:{str(e)}")
        raise CustomError("添加圆角出错", 401)
