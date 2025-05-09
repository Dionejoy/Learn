import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed
from config import WEBSOCKET_CONFIG


class WebSocketClient:
    def __init__(self):
        """初始化WebSocket客户端"""
        self.uri = WEBSOCKET_CONFIG["请求URL"]
        self.subscription_msg = WEBSOCKET_CONFIG["订阅消息"]

    async def send_heartbeat(self, websocket):
        """
        发送心跳包

        Args:
            websocket: WebSocket连接
        """
        while True:
            try:
                await websocket.send(json.dumps({"_event": "heartbeat", "data": "h"}))
                await asyncio.sleep(5)
            except Exception as e:
                print(f"发送心跳时出错: {e}")
                break

    async def establish_connection_and_receive_data(self):
        """
        建立WebSocket连接并接收数据

        Yields:
            str: 接收到的WebSocket原始消息
        """
        while True:
            try:
                async with websockets.connect(self.uri, ping_interval=None, ping_timeout=None) as websocket:
                    print("WebSocket 连接已建立")
                    await websocket.send(self.subscription_msg)

                    heartbeat_task = asyncio.create_task(self.send_heartbeat(websocket))
                    try:
                        while True:
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=30)
                                if message == "o":
                                    continue
                                yield message
                            except asyncio.TimeoutError:
                                pass
                    finally:
                        heartbeat_task.cancel()
                        await heartbeat_task
            except ConnectionClosed:
                print("连接中断, 5秒后重连...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"连接错误: {e}, 5秒后重连...")
                await asyncio.sleep(5)
