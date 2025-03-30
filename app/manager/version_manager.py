import sys
import requests
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from app.entity.constants import CHECK_VERSION_URL, CURRENT_VERSION, IS_INNER
from packaging import version
from app.config import ROOT_PATH

from app.utils.logger import setup_logger
logger = setup_logger("version_manager")


@dataclass
class GitHubAsset:
    name: str
    download_url: str
    size: int
    download_count: int


@dataclass
class GitHubRelease:
    tag_name: str
    name: str
    published_at: str
    assets: List[GitHubAsset]
    body: Optional[str] = None  # 发布说明


class VersionManager:
    def __init__(self):
        self.downloadURL: str = None
        self.releaseInfo = self.latestReleaseInfo()

    def new_version_url(self) -> Optional[str]:
        try:
            self.update_lastest_download_url()
            logger.info(f"获取版本信息成功, url:{self.downloadURL}")
            return self.downloadURL
        except Exception as e:
            logger.exception(f"检查版本出错, error:{str(e)}")
            return None

    def latestReleaseInfo(self) -> Optional[GitHubRelease]:
        """获取GitHub仓库的最新发布信息并解析为结构化数据

        Args:
            repo: 仓库路径，格式为"owner/repo"

        Returns:
            GitHubRelease对象或None(失败时)
        """
        try:
            token = self.read_token()
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {token}"  # 使用token认证
            }
            response = requests.get(CHECK_VERSION_URL, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 解析assets
            if IS_INNER:
                assets = [
                    GitHubAsset(
                        name=asset["name"],
                        download_url=asset["browser_download_url"],
                        size=0,
                        download_count=0
                    ) for asset in data.get("assets", [])
                ]

                return GitHubRelease(
                    tag_name=data["tag_name"],
                    name=data["name"],
                    published_at="",
                    assets=assets,
                    body=data.get("body")
                )
            else:
                assets = [
                    GitHubAsset(
                        name=asset["name"],
                        download_url=asset["browser_download_url"],
                        size=asset["size"],
                        download_count=asset["download_count"]
                    ) for asset in data.get("assets", [])
                ]

                return GitHubRelease(
                    tag_name=data["tag_name"],
                    name=data["name"],
                    published_at=data["published_at"],
                    assets=assets,
                    body=data.get("body")
                )

        except (requests.exceptions.RequestException, KeyError) as e:
            logger.exception(f"获取发布信息失败: error:{str(e)}")
            return None
        except Exception as e:
            logger.exception(f"获取最新版本失败: error:{str(e)}")
            return None

    def read_token(self) -> Optional[str]:
        if getattr(sys, 'frozen', False):
            if IS_INNER:
                path = Path(f"{ROOT_PATH}/token_inner")
            else:
                path = Path(f"{ROOT_PATH}/token")
        else:
            if IS_INNER:
                path = Path("token_inner")
            else:
                path = Path("token")
        if not path.exists():
            raise FileNotFoundError(f"Token文件不存在")

        return path.read_text(encoding='utf-8').strip()

    def compare_versions(self, v1: str, v2: str) -> int:
        """比较两个版本号大小

        Args:
            v1: 版本号字符串 (如 "v0.0.1")
            v2: 版本号字符串

        Returns:
            int: 1(v1>v2) / 0(v1=v2) / -1(v1<v2)
        """
        # 去除'v'前缀
        v1_clean = v1[1:] if v1.startswith('v') else v1
        v2_clean = v2[1:] if v2.startswith('v') else v2

        v1_parsed = version.parse(v1_clean)
        v2_parsed = version.parse(v2_clean)

        if v1_parsed > v2_parsed:
            return 1
        elif v1_parsed == v2_parsed:
            return 0
        else:
            return -1

    def update_lastest_download_url(self):
        if self.releaseInfo == None:
            self.downloadURL = None
            return
        if self.compare_versions(self.releaseInfo.tag_name, CURRENT_VERSION) != 1:
            self.downloadURL = None
            return
        if sys.platform == "win32":
            self.downloadURL = self.find_exe_asset()
        else:
            self.downloadURL = self.find_zip_asset()

    def find_zip_asset(self) -> Optional[str]:
        """查找 releaseInfo.assets 中 name 以 '.zip' 结尾的 asset

        Returns:
            GitHubAsset 或 None（如果没有匹配的 asset）
        """
        if not self.releaseInfo or not self.releaseInfo.assets:
            return None

        for asset in self.releaseInfo.assets:
            if asset.name.lower().endswith('.zip'):
                return asset.download_url
        return None

    def find_exe_asset(self) -> Optional[str]:
        """查找 releaseInfo.assets 中 name 以 '.zip' 结尾的 asset

        Returns:
            GitHubAsset 或 None（如果没有匹配的 asset）
        """
        if not self.releaseInfo or not self.releaseInfo.assets:
            return None

        for asset in self.releaseInfo.assets:
            if asset.name.lower().endswith('.exe'):
                return asset.download_url
        return None


version_manager = VersionManager()
