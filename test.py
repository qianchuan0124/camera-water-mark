from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
from app.config import ASSETS_PATH, CACHE_PATH

PADDING_PERCENT_IN_BACKGROUND = 0.15
GAUSSIAN_KERNEL_RADIUS = 35


def add_effects(img: Image.Image) -> Image.Image:
    """添加圆角阴影+背景模糊效果
    Args:
        img: 输入图片
    Returns:
        带特效的图片(RGBA)
    """

    # 1. 添加圆角
    img = img.convert("RGBA")
    rounded_img = add_rounded_corners(img)

    # 2. 添加阴影
    shadow_img = add_shadow(rounded_img)

    # 3. 添加背景模糊 (修改后的实现)
    final_img = add_background_blur(shadow_img)

    return rounded_img


def add_rounded_corners(img: Image.Image) -> Image.Image:
    """添加圆角效果"""
    radius = min(img.width, img.height) // 20
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    img.putalpha(mask)
    return img


def add_shadow(img: Image.Image) -> Image.Image:
    """添加阴影效果"""
    shadow_blur: int = 20
    shadow_color: tuple = (40, 40, 40, 180)
    corner_radius = min(img.width, img.height) // 20

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


def add_background_blur(img: Image.Image) -> Image.Image:
    """添加有效的背景模糊效果"""
    """创建扩展的模糊背景"""
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
        int(img.height * (1 + PADDING_PERCENT_IN_BACKGROUND))
    )
    blurred_bg = bg.resize(new_size)
    foreground = add_rounded_corners(img)

    # 计算居中位置
    x_offset = int((blurred_bg.width - foreground.width) / 2)
    y_offset = int((blurred_bg.height - foreground.height) / 2)

    # 创建结果画布
    result = blurred_bg.convert("RGBA")

    # 粘贴前景图（使用alpha通道）
    result.paste(foreground, (x_offset, y_offset), foreground)
    return result


if __name__ == '__main__':
    src = ASSETS_PATH / "default_bg.jpg"
    des = Path(CACHE_PATH) / "effects_result.png"

    img = Image.open(src)
    result = add_effects(img)
    result.save(des, "PNG", quality=100)
    print(f"已保存特效图片到: {des}")
