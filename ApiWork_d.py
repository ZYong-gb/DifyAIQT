from PyQt5 import QtCore
import requests

class ApiWorker(QtCore.QObject):
    # 定义信号（用于传递结果或错误）
    finished = QtCore.pyqtSignal(str)  # 成功时发送 AI 回答
    error = QtCore.pyqtSignal(str)     # 失败时发送错误信息

    def __init__(self, auth, content_type, api_url, query):
        super().__init__()
        self.auth = auth
        self.content_type = content_type
        self.api_url = api_url
        self.query = query

    def run(self):
        # 1. 准备请求参数
        headers = {
            "Authorization": self.auth,
            "Content-Type": self.content_type
        }
        payload = {
            "inputs": {},
            "response_mode": "blocking",
            "auto_generate_name": True,
            "query": self.query,
            "user": "user123"
        }

        try:
            # 2. 发送API请求
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)

            # 3. 处理响应
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "无回复")
                self.finished.emit(answer)  # 发送成功结果
            else:
                # 尝试获取API返回的错误信息（如果有）
                error_msg = f"API调用失败（状态码：{response.status_code}"
                try:
                    error_detail = response.json().get("message", "未知错误")
                    error_msg += f"，详情：{error_detail}"
                except:
                    pass
                self.error.emit(error_msg + ")")  # 发送错误

        except requests.exceptions.RequestException as e:
            # 4. 处理各种请求异常
            error_type = type(e).__name__
            self.error.emit(f"请求发生错误（{error_type}）：{str(e)}")
        except ValueError as e:
            # 5. 处理JSON解析错误
            self.error.emit(f"响应数据解析失败：{str(e)}")
        except Exception as e:
            # 6. 处理其他未知异常
            self.error.emit(f"发生未知错误：{str(e)}")