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
        # 初始化JSON堆栈
        self.json_buffer = ""

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
        if self.parent.mode == "bilibili":
            self.capture_api_response(output)
        if self.parent.mode == "youtube":
            self.capture_youtube_response(output)

    def capture_api_response(self, text):
        """捕获API响应信息"""
        # 查找包含指定URL的行
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "https://api.bilibili.com/x/web-interface/view" in line:
                self.if_record_response = True
                # 重置JSON缓冲区
                self.json_buffer = ""
                continue
            keyword = "Response: "
            if self.if_record_response:
                if keyword in line:
                    self.json_buffer = ""
                response_line = line.strip().split(keyword)[-1]
                self.json_buffer += response_line
                self.parse_response_json()

    def capture_youtube_response(self, text):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("{"):
                self.json_buffer = line
                self.if_record_response = True
                continue
            self.json_buffer += line
            self.parse_response_json()


    def parse_response_json(self):
        # 尝试解析JSON

        try:
            response_json = json.loads(self.json_buffer)
        except Exception as e:
            pass
            # 如果解析失败，可能是JSON不完整，保持缓冲区内容供下次调用使用
            # print("解析json失败，等待更多数据", str(e))
            # return "failure"
        else:
            # 解析成功，更新视频信息并重置缓冲区
            # self._base_video_info_json = response_json
            self.parent.base_video_info_json = response_json
            self.json_buffer = ""
            self.if_record_response = False
