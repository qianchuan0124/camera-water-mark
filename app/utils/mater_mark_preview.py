import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from .logger import setup_logger
logger = setup_logger("mater_mark_preview")
from app.config import CACHE_PATH, RESOURCE_PATH

DEFAULT_BG_PATH = RESOURCE_PATH / "assets" / "default_bg.png"
PREVIEW_IMAGE_FILENAME = CACHE_PATH / "preview.png"  # 预览的图片路径

def ensure_background(bg_path: Path) -> Path:
    """确保背景图片存在，若不存在则创建默认黑色背景"""
    if not bg_path.is_file() or not bg_path.exists():
        if not Path(DEFAULT_BG_PATH).exists():
            DEFAULT_BG_PATH.parent.mkdir(parents=True, exist_ok=True)
            run_subprocess(
                [
                    "ffmpeg",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=black:s=1920x1080",
                    "-frames:v",
                    "1",
                    str(DEFAULT_BG_PATH),
                ]
            )
        return Path(DEFAULT_BG_PATH)
    return bg_path

def generate_preview(
    style_str: str,
    preview_text: Tuple[str, Optional[str]],
    bg_path: str,
    width: int,
    height: int,
) -> str:
    """生成预览图片"""

    # ass_file = generate_ass_file(style_str, preview_text, width, height)
    # ass_file = auto_wrap_ass_file(ass_file)
    bg_path = ensure_background(Path(bg_path))

    output_path = PREVIEW_IMAGE_FILENAME
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ass_file_processed = ass_file.replace("\\", "/").replace(":", r"\\:")
    ass_file_processed = "11"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(bg_path),
        "-vf",
        f"ass={ass_file_processed}",
        "-frames:v",
        "1",
        str(output_path),
    ]
    run_subprocess(cmd)
    return str(output_path)

def run_subprocess(command: list):
    """运行子进程命令，并处理异常"""
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e.stderr}")