import asyncio
import threading
from websocket_client import WebSocketClient
from decrypt import DataDecrypter
from alert_handler import AlertHandler
from data_saver import DataSaver
from email_sender import EmailSender
from api_server import run_api_server
from config import DEFAULT_INTERVAL_SECONDS, DEFAULT_ALERT_THRESHOLD


class StockMonitoringSystem:
    def __init__(self, interval_seconds=None, alert_threshold=None):
        """
        初始化股票监控系统

        Args:
            interval_seconds: 价格监控时间间隔（秒）
            alert_threshold: 价格波动警报阈值（百分比）
        """
        # 设置参数
        self.interval_seconds = interval_seconds or DEFAULT_INTERVAL_SECONDS
        self.alert_threshold = alert_threshold or DEFAULT_ALERT_THRESHOLD

        # 初始化组件
        self.data_saver = DataSaver()
        self.websocket_client = WebSocketClient()
        self.alert_handler = AlertHandler(
            self.data_saver,
            EmailSender,
            self.interval_seconds,
            self.alert_threshold
        )

        # 其他设置
        self.is_running = False

    async def websocket_main(self):
        """WebSocket主循环"""
        print("启动 WebSocket 客户端...")

        async for raw_message in self.websocket_client.establish_connection_and_receive_data():
            decrypted_data = DataDecrypter.decrypt_message(raw_message)
            if decrypted_data:
                # 处理数据并检查警报条件
                alert_result = self.alert_handler.process_data(decrypted_data)
                if alert_result:
                    self.alert_handler.handle_alert(alert_result)

    def start_websocket_loop(self):
        """启动WebSocket循环"""
        asyncio.run(self.websocket_main())

    def start(self, api_host='127.0.0.1', api_port=5000):
        """
        启动股票监控系统

        Args:
            api_host: API服务器主机
            api_port: API服务器端口
        """
        if self.is_running:
            print("系统已在运行中")
            return

        self.is_running = True

        # 启动WebSocket线程
        self.websocket_thread = threading.Thread(
            target=self.start_websocket_loop,
            daemon=True
        )
        self.websocket_thread.start()

        # 启动API服务器（在主线程中运行）
        print(f"启动API服务器在 http://{api_host}:{api_port}")
        run_api_server(host=api_host, port=api_port)

    def stop(self):
        """停止股票监控系统"""
        if not self.is_running:
            return

        self.is_running = False
        self.data_saver.close()
        # API服务器将随主线程结束而结束


# 直接运行时作为主入口
if __name__ == "__main__":
    # 创建并启动系统
    system = StockMonitoringSystem()
    system.start()
