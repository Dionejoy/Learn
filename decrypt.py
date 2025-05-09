import json
import re
from datetime import datetime


class DataDecrypter:
    @staticmethod
    def decrypt_message(raw_message):
        """
        解密并解析WebSocket原始消息

        Args:
            raw_message: WebSocket接收的原始消息

        Returns:
            dict: 解析后的股票数据，如果解析失败则返回None
        """
        try:
            unescaped = raw_message.encode().decode('unicode_escape')
            match = re.search(r'a\["(.*)"\]', unescaped)
            if match:
                inner_json = json.loads(match.group(1))
                if "message" in inner_json:
                    message_content = inner_json["message"].split("::", 1)[1].encode().decode('unicode_escape')
                    data = json.loads(message_content)
                    if "timestamp" in data:
                        beijing_time = datetime.fromtimestamp(int(data["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
                        return {
                            "产品ID": data.get("pid", ""),
                            "最新价格方向指示": data.get("last_dir", ""),
                            "最新价格": data.get("last_numeric", data.get("last", "")),
                            "买价": data.get("bid", ""),
                            "卖价": data.get("ask", ""),
                            "当日最高价": data.get("high", ""),
                            "当日最低价": data.get("low", ""),
                            "昨日收盘价": data.get("last_close", ""),
                            "价格变化百分比": data.get("pcp", ""),
                            "时间": data.get("time", ""),
                            "时间戳": data.get("timestamp", ""),
                            "北京时间": beijing_time
                        }
        except Exception as e:
            print(f"消息解密错误: {e}")
        return None
