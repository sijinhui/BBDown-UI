import json
from PySide6.QtCore import QProcess


class ProcessHandler:
    def __init__(self, parent):
        self.parent = parent
        # 初始化进程
        self.process = QProcess(self.parent)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        # 初始化基本信息json
        self.if_record_response = False
        self._base_video_info_json = None

    def handle_stdout(self):
        """处理标准输出"""
        data = self.process.readAllStandardOutput()
        self._handle_process_output(data)

    def handle_stderr(self):
        """处理错误输出"""
        data = self.process.readAllStandardError()
        self._handle_process_output(data, is_stderr=True)

    def process_finished(self):
        """进程结束处理"""
        self.parent.action_buttons.process_finished()

    def _handle_process_output(self, data, is_stderr=False):
        """处理进程输出的通用方法"""
        try:
            output = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用系统默认编码
            output = bytes(data).decode("gbk", errors="ignore")
        self.parent.output_area.append_output(output)

        # 检测未登录提示
        if "未登录B站账号" in output:
            self.parent.action_buttons.handle_not_logged_in()

        # 捕捉API响应信息
        self.capture_api_response(output)

    def capture_api_response(self, text):
        """捕获API响应信息"""
        # 查找包含指定URL的行
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "https://api.bilibili.com/x/web-interface/view" in line:
                self.if_record_response = True
                continue
            keyword = "Response: "
            if self.if_record_response and keyword in line:
                response_line = line.strip().split(keyword)[-1]
                try:
                    response_json = json.loads(response_line)
                except Exception as e:
                    print("解析json失败", str(e), response_line, sep='\n')
                else:
                    # self._base_video_info_json = response_json
                    self.parent.base_video_info_json = response_json
                self.if_record_response = False

    # @property
    # def base_video_info_json(self):
    #     """获取视频基本信息"""
    #     return self._base_video_info_json
    #
    # @base_video_info_json.setter
    # def base_video_info_json(self, value):
    #     """设置基本信息，并更新对应的框"""
    #     self._base_video_info_json = value
    #     self.parent.video_info_banner.update_video_info(value)