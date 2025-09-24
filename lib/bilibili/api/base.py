import requests
import os


class BaseAPI:
    """API基类，提供通用的HTTP请求功能"""

    def __init__(self, base_url="", headers=None, cookies=None):
        """
        初始化API基类

        Args:
            base_url (str): API基础URL
            headers (dict): HTTP请求头
            cookies (dict): Cookie字典
        """
        self.base_url = base_url
        self.session = requests.Session()

        if headers:
            self.session.headers.update(headers)

        if cookies:
            self.session.cookies.update(cookies)

    def _get(self, endpoint, params=None, **kwargs):
        """
        发送GET请求

        Args:
            endpoint (str): API端点
            params (dict): 查询参数
            **kwargs: 其他请求参数

        Returns:
            dict: 响应数据或None
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint

        try:
            response = self.session.get(url, params=params, **kwargs)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求出错: {e}")
            return None

    def _post(self, endpoint, data=None, json=None, **kwargs):
        """
        发送POST请求

        Args:
            endpoint (str): API端点
            data (dict): 表单数据
            json (dict): JSON数据
            **kwargs: 其他请求参数

        Returns:
            dict: 响应数据或None
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint

        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求出错: {e}")
            return None