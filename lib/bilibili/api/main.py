import os
from base import BaseAPI


class BilibiliAPI(BaseAPI):
    def __init__(self, cookie_file_path=None):
        """
        初始化Bilibili API客户端

        Args:
            cookie_file_path (str): Cookie文件路径，默认为 ~/.local/bin/BBDown.data
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        }

        # 设置默认cookie文件路径
        if cookie_file_path is None:
            self.cookie_file_path = os.path.expanduser("~/.local/bin/BBDown.data")
        else:
            self.cookie_file_path = cookie_file_path

        # 读取cookie
        cookies = self._load_cookies()

        # 初始化基类
        super().__init__(
            base_url="https://api.bilibili.com",
            headers=headers,
            cookies=cookies
        )

    def _load_cookies(self):
        """
        从文件加载cookie

        Returns:
            dict: Cookie字典
        """
        try:
            with open(self.cookie_file_path, "r", encoding="utf-8") as f:
                cookie_str = f.read().strip()
            cookies = dict([item.split("=", 1) for item in cookie_str.split(";") if "=" in item])
            return cookies
        except FileNotFoundError:
            print(f"Cookie文件未找到: {self.cookie_file_path}")
            return {}
        except Exception as e:
            print(f"读取Cookie文件时出错: {e}")
            return {}

    def get_favorite_folders(self, up_mid):
        """
        获取用户创建的收藏夹列表

        Args:
            up_mid (str): 用户ID

        Returns:
            dict: API响应数据
        """
        endpoint = '/x/v3/fav/folder/created/list-all'
        params = {"up_mid": up_mid}

        return self._get(endpoint, params)


# 使用示例
if __name__ == "__main__":
    # 创建API实例
    api = BilibiliAPI()

    # 获取收藏夹列表
    result = api.get_favorite_folders('37733958')
    if result:
        print(result)