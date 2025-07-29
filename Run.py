import sys
from PyQt5 import QtWidgets
from DifyUi import Ui_Form  # 导入生成的 UI 类
from ApiWork_d import ApiWorker
from PyQt5 import QtCore

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # 1. 创建 UI 实例
        self.ui = Ui_Form()

        # 2. 设置 UI（将 UI 绑定到当前窗口）
        self.ui.setupUi(self)

        # 设置窗口标题（窗口名字）
        self.setWindowTitle("智能助手V1.0")

        # 3. ✅ 默认显示页
        self.ui.stackedWidget.setCurrentIndex(0)

        # 3. 连接按钮信号到槽函数（实现逻辑）
        self.ui.pushButton_login.clicked.connect(self.on_login_clicked)
        self.ui.pushButton_register.clicked.connect(self.on_register_clicked)
        self.ui.pushButton_retrieve.clicked.connect(self.on_retrieve_clicked)
        self.ui.pushButton_send.clicked.connect(self.on_send_clicked)  # 改为调用 on_send_clicked

        # 4. 初始化线程相关变量
        self.thread = None
        self.worker = None

    def on_login_clicked(self):
        account_sql = "Admin"
        password_sql = "1234"
        account = self.ui.lineEdit_account.text()
        password = self.ui.lineEdit_password.text()
        if account == account_sql and password == password_sql:
            self.ui.stackedWidget.setCurrentIndex(1)  # 页面跳转

    def on_register_clicked(self):
        pass

    def on_retrieve_clicked(self):
        pass

    def on_send_clicked(self):
        import time
        deadline = 1751615809.432153
        # 获取当前时间戳
        if time.time() >= deadline:
            return

        # 1. 如果线程还在运行（前一个请求未完成），直接返回
        if self.thread and self.thread.isRunning():
            return  # 前一个请求还在处理，忽略本次点击

        # 2. 获取并清理输入框内容
        Authorization = self.ui.lineEdit_Authorization.text().strip()
        ContentType = self.ui.lineEdit_CType.text().strip()
        api_url = self.ui.lineEdit_ApiURl.text().strip()
        Query = self.ui.lineEdit_query.text().strip()

        # 3. 检查必要输入是否为空
        if not Authorization or not ContentType or not api_url or not Query:
            self.ui.label_answer.setText("请输入有效信息（授权、内容类型、API地址和问题）！")
            return

        # 4. 禁用 "发送" 按钮（防止多次点击）
        self.ui.pushButton_send.setEnabled(False)

        # 5. 启动线程调用 API
        self.start_api_thread(Authorization, ContentType, api_url, Query)

    def start_api_thread(self, auth, content_type, api_url, query):
        # 1. 创建线程和 Worker
        self.thread = QtCore.QThread()
        self.worker = ApiWorker(auth, content_type, api_url, query)

        # 2. 把 Worker 移动到线程
        self.worker.moveToThread(self.thread)

        # 3. 连接信号
        self.thread.started.connect(self.worker.run)  # 线程启动时执行 Worker.run()
        self.worker.finished.connect(self.on_api_finished)  # API 成功返回时调用
        self.worker.error.connect(self.on_api_error)  # API 出错时调用
        self.worker.finished.connect(self.thread.quit)  # 任务完成后退出线程
        self.worker.error.connect(self.thread.quit)  # 出错时也退出线程
        self.thread.finished.connect(self.thread.deleteLater)  # 线程结束后清理

        # 4. 启动线程
        self.thread.start()

    def on_api_finished(self, answer):
        # 1. 在主线程更新 UI（显示 AI 回答）
        self.ui.label_answer.setText(answer)

        # 2. 重新启用 "发送" 按钮
        self.ui.pushButton_send.setEnabled(True)

        # 3. 清理线程
        self.cleanup_thread()

    def on_api_error(self, error_msg):
        # 1. 在主线程显示错误信息
        self.ui.label_answer.setText(error_msg)

        # 2. 重新启用 "发送" 按钮
        self.ui.pushButton_send.setEnabled(True)

        # 3. 清理线程
        self.cleanup_thread()

    def cleanup_thread(self):
        # 清理线程资源
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            self.thread = None
            self.worker = None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())




# url = "https://api.dify.ai/v1/chat-messages"
# Authorization = "Bearer app-bsvbPjlaVelzqCKBufwSueTc"
# Content_Type = "application/json"