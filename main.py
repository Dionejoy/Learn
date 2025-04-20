import asyncio
import websockets
import json
import re
import time
import smtplib
import csv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from websockets.exceptions import ConnectionClosed
from datetime import datetime

# 用于存储每个pid的历史数据点和保存时间信息
price_history_by_pid = {}
# 用于存储程序开始运行的时间
start_time = time.time()

# 创建数据保存目录
DATA_DIR = "stock_data"
os.makedirs(DATA_DIR, exist_ok=True)

WEBSOCKET_CONFIG = {
    "请求URL": "wss://streaming.forexpros.com/echo/339/gkhxqjll/websocket",
    "请求方法": "GET",
    "状态代码": "101 Switching Protocols",
    "主机": "streaming.forexpros.com",
    "来源": "https://cn.investing.com",
    "用户代理": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "接受编码": "gzip, deflate, br, zstd",
    "接受语言": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "缓存控制": "no-cache",
    "pragma": "no-cache",
    "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
    "sec-websocket-key": "T/jcmZ8UjizjtLk+7WxwYw==",
    "sec-websocket-version": "13",
    "订阅消息": '{"_event":"bulk-subscribe","tzID":8,"message":"isOpenExch-103:%%isOpenExch-54:%%pid-40820:%%pid-28930:%%pid-179:%%isOpenExch-21:%%pid-178:%%isOpenExch-20:%%pid-1175152:%%isOpenExch-152:%%pid-1175153:%%pid-8827:%%isOpenExch-1004:%%pid-41655:%%isOpenExch-NaN:%%pid-1075487:%%pid-8969:%%pid-1155537:%%pid-41604:%%pid-41651:%%pid-41626:%%pid-944073:%%pid-41607:%%pid-944521:%%pid-1088093:%%pid-41609:%%pid-41650:%%pid-100901:%%pid-8955:%%pid-1:%%isOpenExch-1002:%%pid-2111:%%isOpenExch-1001:%%pid-961728:%%pid-1817:%%pid-3:%%pid-5:%%pid-2:%%pid-941155:%%isOpenExch-1:%%pid-102047:%%pid-6378:%%isOpenExch-2:%%pid-102911:%%pid-6435:%%pid-26490:%%pid-6408:%%pid-6369:%%pid-243:%%pid-267:%%pid-7888:%%pid-284:%%isOpenExch-3:%%pid-352:%%isOpenExch-4:%%pid-169:%%pid-20:%%pid-166:%%pid-172:%%pid-27:%%pid-167:%%isOpenExch-9:%%pid-8830:%%pid-8836:%%pid-8831:%%pid-8849:%%pid-8833:%%pid-8862:%%pid-8832:%%pid-7:%%pid-9:%%pid-10:%%pid-8916:%%pid-8575:%%pid-9217:%%pid-20245:%%pid-100276:%%pid-100287:%%pid-100289:%%pid-100290:%%pid-100299:%%pid-100303:%%pid-100310:%%pid-100320:%%pid-100350:%%pid-100493:%%pid-100673:%%pid-100727:%%pid-100978:%%pid-100989:%%pid-101060:%%pid-101062:%%pid-101064:%%pid-101072:%%pid-101073:%%pid-101076:%%pid-101078:%%pid-101079:%%pid-101083:%%pid-101084:%%pid-101097:%%pid-101099:%%pid-101103:%%pid-101113:%%pid-101119:%%pid-101122:%%pid-101123:%%pid-101137:%%pid-101143:%%pid-101158:%%pid-944122:%%pid-944220:%%pid-944315:%%pid-944451:%%pid-944524:%%pid-944533:%%pid-944579:%%pid-944897:%%pid-955759:%%pid-995189:%%pid-1017555:%%pid-1076874:%%pid-1112831:%%pid-100732:%%isOpenExch-0:%%pid-100836:%%pid-100980:%%pid-944046:%%pid-944704:%%pid-945815:%%pid-946593:%%pid-950799:%%pid-950815:%%pid-950912:%%pid-100701:%%pid-100856:%%pid-101057:%%pid-101071:%%pid-942831:%%pid-944022:%%pid-944658:%%pid-944873:%%pid-944895:%%pid-945809:"}'
}

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "sender_email": "max17788556699@163.com",
    "password": "XHVFjimTQ7srtVaJ",
    "receiver_email": "977226416@qq.com"
}


async def establish_connection_and_receive_data():
    """
    建立 WebSocket 连接并接收数据
    """
    uri = WEBSOCKET_CONFIG["请求URL"]
    while True:
        try:
            async with websockets.connect(
                    uri,
                    ping_interval=None,
                    ping_timeout=None
            ) as websocket:
                print("WebSocket 连接已建立")
                await websocket.send(WEBSOCKET_CONFIG["订阅消息"])

                # 创建心跳任务
                heartbeat_task = asyncio.create_task(send_heartbeat(websocket))

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
                    try:
                        await heartbeat_task
                    except asyncio.CancelledError:
                        pass
        except ConnectionClosed:
            print("连接中断,5秒后重新连接...")
            await asyncio.sleep(5)
        except Exception as error:
            print(f"连接错误: {error},5秒后重新连接...")
            await asyncio.sleep(5)


async def send_heartbeat(websocket):
    """
    每5秒发送一次心跳
    """
    while True:
        try:
            await websocket.send(json.dumps({"_event": "heartbeat", "data": "h"}))
            await asyncio.sleep(5)
        except Exception as e:
            print(f"发送心跳时出错: {e}")
            break


def decrypt_message(raw_message):
    """
    解密接收到的消息并翻译为中文字段
    """
    try:
        unescaped = raw_message.encode().decode('unicode_escape')
        match = re.search(r'a\["(.*)"\]', unescaped)
        if match:
            inner_string = match.group(1)
            inner_json = json.loads(inner_string)
            if "message" in inner_json:
                message_parts = inner_json["message"].split("::", 1)
                if len(message_parts) == 2:
                    message_content = message_parts[1].encode().decode('unicode_escape')
                    data = json.loads(message_content)
                    if "timestamp" in data:
                        beijing_time = datetime.fromtimestamp(int(data["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
                        time_str = data.get("time", "")

                        # 优先使用last_numeric，如果不存在则使用last
                        latest_price = data.get("last_numeric", data.get("last", ""))

                        translated_data = {
                            "产品ID": data.get("pid", ""),
                            "最新价格方向指示": data.get("last_dir", ""),
                            "最新价格": latest_price,
                            "买价": data.get("bid", ""),
                            "卖价": data.get("ask", ""),
                            "当日最高价": data.get("high", ""),
                            "当日最低价": data.get("low", ""),
                            "昨日收盘价": data.get("last_close", ""),
                            "价格变化百分比": data.get("pcp", ""),
                            "时间": time_str,
                            "时间戳": data.get("timestamp", ""),
                            "北京时间": beijing_time
                        }
                        return translated_data
    except Exception as error:
        print(f"消息解密错误: {error}")
    return None


def save_stock_data(pid, data, interval_seconds):
    """
    为特定股票保存数据到CSV文件
    """
    # 创建该股票的目录
    stock_dir = os.path.join(DATA_DIR, pid)
    os.makedirs(stock_dir, exist_ok=True)

    # 使用日期作为文件名，这样每天创建一个新文件
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(stock_dir, f"{today}.csv")

    # 确定时间区间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    two_min_ago = datetime.fromtimestamp(time.time() - interval_seconds).strftime("%Y-%m-%d %H:%M:%S")
    time_interval = f"{two_min_ago} 到 {current_time}"

    # 检查文件是否存在
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # 如果文件不存在，写入标题行
        if not file_exists:
            headers = ["产品ID", "最新价格", "买价", "卖价", "当日最高价", "当日最低价", "昨日收盘价", "价格变化百分比",
                       "时间", "北京时间", "时间区间"]
            writer.writerow(headers)

        # 写入数据
        row = [
            data.get('产品ID', ''),
            data.get('最新价格', ''),
            data.get('买价', ''),
            data.get('卖价', ''),
            data.get('当日最高价', ''),
            data.get('当日最低价', ''),
            data.get('昨日收盘价', ''),
            data.get('价格变化百分比', ''),
            data.get('时间', ''),
            data.get('北京时间', ''),
            time_interval
        ]
        writer.writerow(row)

        # 添加空行以区分不同时间的数据
        writer.writerow([])

    print(f"已保存 {pid} 的数据到 {filename}")


def process_data(data, interval_seconds, alert_threshold):
    """
    处理数据并检查是否需要报警
    """
    global price_history_by_pid

    if not isinstance(data, dict):
        return None

    pid = data.get("产品ID", "")
    timestamp = data.get("时间戳", "")
    current_price_str = data.get("最新价格", "")

    if not pid or not timestamp or not current_price_str:
        return None

    try:
        current_price = float(str(current_price_str).replace(',', ''))
        timestamp = int(timestamp)
    except (ValueError, TypeError):
        return None

    current_time = time.time()

    # 如果是该pid的第一条数据，则初始化并立即保存
    if pid not in price_history_by_pid:
        price_history_by_pid[pid] = {
            "baseline_price": current_price,
            "baseline_timestamp": timestamp,
            "last_alert_timestamp": 0,
            "last_save_timestamp": 0,  # 上次保存数据的时间
            "current_data": data  # 当前最新数据
        }
        # 首次收到该股票数据时立即保存
        save_stock_data(pid, data, interval_seconds)
        price_history_by_pid[pid]["last_save_timestamp"] = current_time
        return None

    # 更新该股票的最新数据
    price_history_by_pid[pid]["current_data"] = data

    # 检查是否需要保存数据（基于该股票的上次保存时间）
    if current_time - price_history_by_pid[pid]["last_save_timestamp"] >= interval_seconds:
        save_stock_data(pid, data, interval_seconds)
        price_history_by_pid[pid]["last_save_timestamp"] = current_time

    # 计算与基准价格的时间差
    time_diff = timestamp - price_history_by_pid[pid]["baseline_timestamp"]

    # 如果时间差大于等于间隔时间，检查是否需要报警
    if time_diff >= interval_seconds and (
            timestamp - price_history_by_pid[pid]["last_alert_timestamp"] >= interval_seconds):
        baseline_price = price_history_by_pid[pid]["baseline_price"]

        # 计算价格变化率，精确到小数点后4位
        change_rate = round((current_price - baseline_price) / baseline_price * 100, 4)
        alert_triggered = abs(change_rate) >= alert_threshold

        # 更新基准价格和时间戳
        price_history_by_pid[pid]["baseline_price"] = current_price
        price_history_by_pid[pid]["baseline_timestamp"] = timestamp

        # 如果触发警报，更新上次警报时间并返回结果
        if alert_triggered:
            price_history_by_pid[pid]["last_alert_timestamp"] = timestamp

            return {
                "pid": pid,
                "baseline_price": baseline_price,
                "current_price": current_price,
                "change_rate": change_rate,
                "alert_triggered": alert_triggered,
                "baseline_time": datetime.fromtimestamp(
                    price_history_by_pid[pid]["baseline_timestamp"] - time_diff).strftime("%Y-%m-%d %H:%M:%S"),
                "current_time": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "raw_data": data
            }

    return None


def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_CONFIG["sender_email"]
        message["To"] = EMAIL_CONFIG["receiver_email"]
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        # 使用 SMTP_SSL（适配465端口）
        with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["password"])
            server.send_message(message)
        print(f"邮件发送成功: {subject}")
    except Exception as e:
        print(f"邮件发送失败: {e}")


def handle_alert(result):
    """
    处理报警情况，发送邮件通知
    """
    if result and result["alert_triggered"]:
        direction = "上涨" if result["change_rate"] > 0 else "下跌"

        # 控制台输出
        print("\n" + "=" * 50)
        print(f"⚠️ 警报! 产品ID {result['pid']} 价格变化超过阈值")
        print(f"时间区间: {result['baseline_time']} 到 {result['current_time']}")
        print(f"价格变化: {result['baseline_price']} {direction}到 {result['current_price']}")
        print(f"变化率: {result['change_rate']}%")
        print("=" * 50 + "\n")

        # 构建邮件内容
        raw_data = result.get('raw_data', {})

        email_subject = f"股票警报: 产品ID {result['pid']} 价格{direction} {abs(result['change_rate'])}%"

        email_body = f"""
        <h2>股票价格异常波动警报</h2>
        <p><strong>产品ID:</strong> {result['pid']}</p>
        <p><strong>价格变化:</strong> {result['baseline_price']} {direction}到 {result['current_price']}</p>
        <p><strong>变化率:</strong> {result['change_rate']}%</p>
        <p><strong>时间区间:</strong> {result['baseline_time']} 到 {result['current_time']}</p>

        <h3>详细数据:</h3>
        <table border="1" cellpadding="5">
            <tr><th>字段</th><th>值</th></tr>
            <tr><td>产品ID</td><td>{raw_data.get('产品ID', '')}</td></tr>
            <tr><td>最新价格</td><td>{raw_data.get('最新价格', '')}</td></tr>
            <tr><td>买价</td><td>{raw_data.get('买价', '')}</td></tr>
            <tr><td>卖价</td><td>{raw_data.get('卖价', '')}</td></tr>
            <tr><td>当日最高价</td><td>{raw_data.get('当日最高价', '')}</td></tr>
            <tr><td>当日最低价</td><td>{raw_data.get('当日最低价', '')}</td></tr>
            <tr><td>昨日收盘价</td><td>{raw_data.get('昨日收盘价', '')}</td></tr>
            <tr><td>价格变化百分比</td><td>{raw_data.get('价格变化百分比', '')}</td></tr>
            <tr><td>时间</td><td>{raw_data.get('时间', '')}</td></tr>
            <tr><td>北京时间</td><td>{raw_data.get('北京时间', '')}</td></tr>
        </table>
        """

        # 发送邮件
        send_email(email_subject, email_body)


async def main():
    """
    主函数
    """
    print("启动 WebSocket 客户端...")

    interval_seconds = 120  # 2分钟
    alert_threshold = 0.2  # 0.2%

    async for raw_message in establish_connection_and_receive_data():
        decrypted_data = decrypt_message(raw_message)
        if decrypted_data:
            result = process_data(decrypted_data, interval_seconds, alert_threshold)
            if result:
                handle_alert(result)


if __name__ == "__main__":
    asyncio.run(main())
