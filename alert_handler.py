import time
from datetime import datetime


class AlertHandler:
    def __init__(self, data_saver, email_sender, interval_seconds=None, alert_threshold=None):
        """
        初始化警报处理器

        Args:
            data_saver: 数据保存器实例
            email_sender: 邮件发送器类
            interval_seconds: 价格监控时间间隔（秒）
            alert_threshold: La价格波动警报阈值（百分比）
        """
        from config import DEFAULT_INTERVAL_SECONDS, DEFAULT_ALERT_THRESHOLD

        self.data_saver = data_saver
        self.email_sender = email_sender
        self.interval_seconds = interval_seconds or DEFAULT_INTERVAL_SECONDS
        self.alert_threshold = alert_threshold or DEFAULT_ALERT_THRESHOLD
        self.price_history_by_pid = {}

    def process_data(self, data):
        """
        处理股票数据并检测警报条件

        Args:
            data: 解密后的股票数据

        Returns:
            dict: 如果触发警报则返回警报信息，否则返回None
        """
        if not isinstance(data, dict):
            return None

        pid = data.get("产品ID")
        timestamp = data.get("时间戳")
        current_price_str = data.get("最新价格")

        if not pid or not timestamp or not current_price_str:
            return None

        try:
            current_price = float(str(current_price_str).replace(',', ''))
            timestamp = int(timestamp)
        except (ValueError, TypeError):
            return None

        current_time = time.time()

        if pid not in self.price_history_by_pid:
            self.price_history_by_pid[pid] = {
                "baseline_price": current_price,
                "baseline_timestamp": timestamp,
                "last_alert_timestamp": 0,
                "last_save_timestamp": 0,
                "current_data": data
            }
            self.data_saver.save_stock_data(pid, data)
            self.price_history_by_pid[pid]["last_save_timestamp"] = current_time
            return None

        self.price_history_by_pid[pid]["current_data"] = data

        if current_time - self.price_history_by_pid[pid]["last_save_timestamp"] >= self.interval_seconds:
            self.data_saver.save_stock_data(pid, data)
            self.price_history_by_pid[pid]["last_save_timestamp"] = current_time

        time_diff = timestamp - self.price_history_by_pid[pid]["baseline_timestamp"]

        if time_diff >= self.interval_seconds and (
                timestamp - self.price_history_by_pid[pid]["last_alert_timestamp"] >= self.interval_seconds):
            baseline_price = self.price_history_by_pid[pid]["baseline_price"]
            change_rate = round((current_price - baseline_price) / baseline_price * 100, 4)
            alert_triggered = abs(change_rate) >= self.alert_threshold

            self.price_history_by_pid[pid]["baseline_price"] = current_price
            self.price_history_by_pid[pid]["baseline_timestamp"] = timestamp

            if alert_triggered:
                self.price_history_by_pid[pid]["last_alert_timestamp"] = timestamp

                baseline_time = datetime.fromtimestamp(
                    self.price_history_by_pid[pid]["baseline_timestamp"] - time_diff
                ).strftime("%Y-%m-%d %H:%M:%S")

                current_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

                alert_data = {
                    "pid": pid,
                    "baseline_price": baseline_price,
                    "current_price": current_price,
                    "change_rate": change_rate,
                    "alert_triggered": alert_triggered,
                    "baseline_time": baseline_time,
                    "current_time": current_time,
                    "alert_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "alert_type": "价格波动",
                    "raw_data": data
                }

                return alert_data

        return None

    def handle_alert(self, alert_data):
        """
        处理警报

        Args:
            alert_data: 警报数据

        Returns:
            bool: 处理成功返回True
        """
        if not alert_data or not alert_data.get("alert_triggered"):
            return False

        # 保存警报历史
        self.data_saver.save_alert(alert_data)

        direction = "上涨" if alert_data["change_rate"] > 0 else "下跌"

        # 打印警报信息
        print("\n" + "=" * 50)
        print(f"⚠️ 警报! 产品ID {alert_data['pid']} 价格变化超过阈值")
        print(f"时间区间: {alert_data['baseline_time']} 到 {alert_data['current_time']}")
        print(f"价格变化: {alert_data['baseline_price']} {direction}到 {alert_data['current_price']}")
        print(f"变化率: {alert_data['change_rate']}%")
        print("=" * 50 + "\n")

        # 发送邮件警报
        raw_data = alert_data.get('raw_data', {})

        email_subject = f"股票警报: 产品ID {alert_data['pid']} 价格{direction} {abs(alert_data['change_rate'])}%"
        email_body = f"""
        <h2>股票价格异常波动警报</h2>
        <p><strong>产品ID:</strong> {alert_data['pid']}</p>
        <p><strong>价格变化:</strong> {alert_data['baseline_price']} {direction}到 {alert_data['current_price']}</p>
        <p><strong>变化率:</strong> {alert_data['change_rate']}%</p>
        <p><strong>时间区间:</strong> {alert_data['baseline_time']} 到 {alert_data['current_time']}</p>
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
        self.email_sender.send_email(email_subject, email_body)
        return True
