from app.config import cfg
from PIL import Image, ImageDraw, ImageFilter
from app.entity.custom_error import CustomError
from app.utils.image_handle import hex_to_rgba, padding_image

from app.utils.logger import setup_logger
logger = setup_logger("image_render")


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
        bg = bg.filter(ImageFilter.GaussianBlur(cfg.blurExtent.value))

        # 调整亮度
        white = Image.new('RGB', bg.size, (255, 255, 255))
        bg = Image.blend(bg, white, 0.1)

        # 扩展尺寸
        new_size = (
            int(img.width * (1 + cfg.blurHorizontalPadding.value * 2)),
            int(img.height * (1 + cfg.blurTopPadding.value + cfg.blurBottomPadding.value) + bottom_padding)
        )
        blurred_bg = bg.resize(new_size)
        if (cfg.addShadow.value):
            foreground = add_shadow(img)
        else:
            foreground = add_rounded_corners(img)

        # 计算居中位置
        x_offset = int((blurred_bg.width - foreground.width) / 2)
        y_offset = int(img.height * cfg.blurTopPadding.value)

        # 创建结果画布
        result = blurred_bg.convert("RGBA")

        # 粘贴前景图（使用alpha通道）
        result.paste(foreground, (x_offset, y_offset), foreground)
        return result
    except Exception as e:
        logger.exception(f"增加模糊背景出错, error:{str(e)}")
        raise CustomError("增加模糊背景出错", 404)


def add_white_margin(img: Image.Image) -> Image.Image:
    """给图片添加外部边框效果
    参数:
        img: 输入图片(支持任意格式)
    返回:
        带外部边框的RGB格式图片
    """
    try:
        padding_size = int(cfg.whiteMarginWidth.value *
                           min(img.width, img.height) / 100)
        padding_img = padding_image(
            img, padding_size, 'tlrb', color=cfg.whiteMarginColor.value)
        return padding_img
    except Exception as e:
        logger.exception(f"增加边距错误, error:{str(e)}")
        raise CustomError("增加边距错误", 403)


def add_shadow(img: Image.Image) -> Image.Image:
    try:
        shadow_blur: int = cfg.shadowBlur.value
        # 使用半透明绿色 (R, G, B, Alpha)
        shadow_color = cfg.shadowColor.value
        corner_radius = min(img.width, img.height) // raduis()

        img = img.convert("RGBA")
        
        # 直接在透明背景上创建阴影层
        shadow_size = (img.width + shadow_blur*2, img.height + shadow_blur*2)
        shadow_layer = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow_layer)
        
        # 绘制带透明度的阴影
        offset = shadow_blur * 0.8  # 控制扩散程度
        draw.rounded_rectangle(
            [(offset, offset),  # 起点外移
             (shadow_size[0] - offset, shadow_size[1] - offset)],  # 终点外扩
            radius=corner_radius + int(offset/2),  # 增大圆角半径
            fill=shadow_color
        )
        
        # 应用模糊效果（保留透明度）
        blurred_shadow = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # 合成最终效果
        result = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        result.alpha_composite(blurred_shadow)
        result.alpha_composite(img, (shadow_blur, shadow_blur))
        return result
    except Exception as e:
        logger.exception(f"增加阴影出错, error:{str(e)}")
        raise CustomError("增加阴影出错", 402)


def add_rounded_corners(img: Image.Image) -> Image.Image:
    """给图片添加透明背景的圆角效果
    参数:
        img: 输入图片(支持任意格式)
    返回:
        带透明背景圆角的RGBA格式图片
    """
    try:
        img = img.convert("RGBA")  # 确保转换为RGBA模式
        radius = min(img.width, img.height) // raduis()
        
        # 创建透明背景层
        background = Image.new("RGBA", img.size, cfg.backgroundColor.value)
        
        # 创建圆角蒙版
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        
        # 将原图粘贴到透明背景并应用蒙版
        background.paste(img, (0, 0), mask=mask)
        return background
    except Exception as e:
        logger.exception(f"添加圆角出错, error:{str(e)}")
        raise CustomError("添加圆角出错", 401)